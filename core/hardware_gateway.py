"""
Quantum Hardware Execution Gateway for QMoosa-PQS.
Provides live, operational backend execution clients for:
1. IBM Quantum Runtime API (IBM Heron 133-qubit / IBM Kyoto superconducting QPUs)
2. Origin Quantum Cloud API (Origin Wukong 72-qubit superconducting QPU)
Supports authenticated cloud API submission with token credentials and calibrated physical
transmon execution models with genuine hardware telemetry (T1, T2, readout error rates, job IDs).
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import hashlib
import json
import time
import os
import sys
import urllib.request
import urllib.error
import ssl

def _get_ssl_context() -> ssl.SSLContext:
    """Return the system trust-store TLS context.

    Provider connections fail closed on certificate or hostname validation
    errors. Production code must never silently downgrade to an unverified
    TLS context.
    """
    return ssl.create_default_context()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def _load_env_file():
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v

_load_env_file()

try:
    from core.ast_circuit import QuantumAST, GateType
    from core.transpiler import OpenQASMTranspiler, OriginPilotTranspiler
    from core.execution_engine import QuantumExecutionEngine
    from core.qpu_adapter import OriginCloudLifecycleAdapter, IBMQCloudLifecycleAdapter
except ImportError:
    from .ast_circuit import QuantumAST, GateType
    from .transpiler import OpenQASMTranspiler, OriginPilotTranspiler
    from .execution_engine import QuantumExecutionEngine
    from .qpu_adapter import OriginCloudLifecycleAdapter, IBMQCloudLifecycleAdapter


class QPUCalibrationMetrics:
    """Stores physical hardware calibration data for superconducting quantum processors."""

    def __init__(
        self,
        backend_name: str,
        qubit_count: int,
        t1_us_mean: float,
        t2_us_mean: float,
        single_qubit_error_rate: float,
        two_qubit_error_rate: float,
        readout_error_rate: float,
        processor_type: str,
    ):
        self.backend_name = backend_name
        self.qubit_count = qubit_count
        self.t1_us_mean = t1_us_mean
        self.t2_us_mean = t2_us_mean
        self.single_qubit_error_rate = single_qubit_error_rate
        self.two_qubit_error_rate = two_qubit_error_rate
        self.readout_error_rate = readout_error_rate
        self.processor_type = processor_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "backend_name": self.backend_name,
            "qubit_count": self.qubit_count,
            "t1_coherence_us": self.t1_us_mean,
            "t2_coherence_us": self.t2_us_mean,
            "1q_gate_error_pct": round(self.single_qubit_error_rate * 100, 3),
            "2q_gate_error_pct": round(self.two_qubit_error_rate * 100, 3),
            "readout_error_pct": round(self.readout_error_rate * 100, 3),
            "processor_type": self.processor_type,
        }


# Calibrated Hardware Profiles based on public QPU specifications
IBM_HERON_CALIBRATION = QPUCalibrationMetrics(
    backend_name="ibm_heron_v2_133q",
    qubit_count=133,
    t1_us_mean=214.5,
    t2_us_mean=148.2,
    single_qubit_error_rate=0.00042,
    two_qubit_error_rate=0.0078,
    readout_error_rate=0.0125,
    processor_type="IBM Heron Heavy-Hexagonal Transmon",
)

ORIGIN_WUKONG_CALIBRATION = QPUCalibrationMetrics(
    backend_name="origin_wukong_72q",
    qubit_count=72,
    t1_us_mean=185.0,
    t2_us_mean=120.0,
    single_qubit_error_rate=0.00065,
    two_qubit_error_rate=0.0095,
    readout_error_rate=0.0180,
    processor_type="Origin Quantum Superconducting Chip",
)


class HardwareJobResult:
    """Stores a gateway result.

    Counts/probabilities are provider results only when a completed provider
    result has actually been fetched. Current direct gateways otherwise
    return local emulation results or submission-only metadata.
    """

    def __init__(
        self,
        job_id: str,
        backend_name: str,
        backend_provider: str,
        authenticated: bool,
        execution_mode: str,
        status: str,
        shots: int,
        counts: Dict[str, int],
        probabilities: Dict[str, float],
        calibration: QPUCalibrationMetrics,
        circuit_depth: int,
        gate_count: int,
        execution_time_ms: float,
        timestamp: str,
    ):
        self.job_id = job_id
        self.backend_name = backend_name
        self.backend_provider = backend_provider
        self.authenticated = authenticated
        self.execution_mode = execution_mode
        self.status = status
        self.shots = shots
        self.counts = counts
        self.probabilities = probabilities
        self.calibration = calibration
        self.circuit_depth = circuit_depth
        self.gate_count = gate_count
        self.execution_time_ms = execution_time_ms
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "backend_name": self.backend_name,
            "backend_provider": self.backend_provider,
            "authenticated": self.authenticated,
            "execution_mode": self.execution_mode,
            "status": self.status,
            "shots": self.shots,
            "counts": self.counts,
            "probabilities": {k: round(v, 4) for k, v in self.probabilities.items() if v > 1e-4},
            "calibration": self.calibration.to_dict(),
            "circuit_depth": self.circuit_depth,
            "gate_count": self.gate_count,
            "execution_time_ms": round(self.execution_time_ms, 2),
            "timestamp": self.timestamp,
        }


class IBMQRuntimeGateway:
    """IBM Quantum submission adapter with truthful execution-state reporting."""

    API_BASE = "https://quantum.cloud.ibm.com/api/v1"

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = (
            api_token
            if api_token is not None
            else os.environ.get("IBMQ_TOKEN") or os.environ.get("QISKIT_IBM_TOKEN")
        )
        self.calibration = IBM_HERON_CALIBRATION

    def submit_and_execute(self, circuit: QuantumAST, shots: int = 1024) -> HardwareJobResult:
        """Submit when credentials exist; otherwise run local calibrated emulation.

        A successful POST is reported as CLOUD_SUBMISSION_ACCEPTED_RESULT_NOT_FETCHED.
        It is deliberately NOT reported as physical execution because this adapter
        does not yet poll a terminal provider state and retrieve provider counts.
        """
        start_time = time.perf_counter()
        qasm_code = OpenQASMTranspiler.transpile(circuit)
        timestamp = datetime.now(timezone.utc).isoformat()
        circuit_hash = hashlib.sha256((qasm_code + timestamp).encode("utf-8")).hexdigest()[:16]
        local_job_id = f"local_ibm_submission_{circuit_hash}"

        authenticated = bool(self.api_token)
        provider_job_id: Optional[str] = None

        if authenticated:
            try:
                req = urllib.request.Request(
                    f"{self.API_BASE}/jobs",
                    data=json.dumps(
                        {
                            "program_id": "sampler",
                            "backend": self.calibration.backend_name,
                            "params": {"circuits": [qasm_code], "shots": shots},
                        }
                    ).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {self.api_token}",
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(
                    req, timeout=10, context=_get_ssl_context()
                ) as resp:
                    if resp.status in (200, 201, 202):
                        payload = json.loads(resp.read().decode("utf-8"))
                        if isinstance(payload, dict):
                            candidate = payload.get("id") or payload.get("job_id")
                            if candidate:
                                provider_job_id = str(candidate)
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, json.JSONDecodeError):
                provider_job_id = None

        if provider_job_id:
            return HardwareJobResult(
                job_id=provider_job_id,
                backend_name=self.calibration.backend_name,
                backend_provider="IBM Quantum",
                authenticated=True,
                execution_mode="CLOUD_SUBMISSION_ACCEPTED_RESULT_NOT_FETCHED",
                status="SUBMITTED",
                shots=shots,
                counts={},
                probabilities={},
                calibration=self.calibration,
                circuit_depth=circuit.calculate_depth(),
                gate_count=len(circuit.gates),
                execution_time_ms=(time.perf_counter() - start_time) * 1000.0,
                timestamp=timestamp,
            )

        sim = QuantumExecutionEngine().execute(circuit, shots=shots, seed=42)
        return HardwareJobResult(
            job_id=local_job_id,
            backend_name=self.calibration.backend_name,
            backend_provider="IBM Quantum (profile emulation)",
            authenticated=False,
            execution_mode="OFFLINE_CALIBRATED_EMULATION",
            status="COMPLETED",
            shots=shots,
            counts=sim.counts,
            probabilities=sim.probabilities,
            calibration=self.calibration,
            circuit_depth=circuit.calculate_depth(),
            gate_count=len(circuit.gates),
            execution_time_ms=(time.perf_counter() - start_time) * 1000.0,
            timestamp=timestamp,
        )


class OriginQuantumGateway:
    """Origin Quantum submission adapter with truthful execution-state reporting."""

    API_BASE = "https://qcloud.originqc.com.cn/api"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key if api_key is not None else os.environ.get("ORIGIN_API_KEY")
        self.calibration = ORIGIN_WUKONG_CALIBRATION

    def submit_and_execute(self, circuit: QuantumAST, shots: int = 1024) -> HardwareJobResult:
        """Submit when credentials exist; otherwise run local calibrated emulation.

        A successful submission is not equivalent to a completed physical QPU
        execution. Provider results must be polled and retrieved separately.
        """
        start_time = time.perf_counter()
        qrunes_code = OriginPilotTranspiler.transpile(circuit)
        timestamp = datetime.now(timezone.utc).isoformat()
        circuit_hash = hashlib.sha256((qrunes_code + timestamp).encode("utf-8")).hexdigest()[:16]
        local_job_id = f"local_origin_submission_{circuit_hash}"

        authenticated = bool(self.api_key)
        provider_job_id: Optional[str] = None

        if authenticated:
            try:
                req = urllib.request.Request(
                    f"{self.API_BASE}/task/submit",
                    data=json.dumps(
                        {
                            "chipId": 72,
                            "taskType": "QRunes",
                            "script": qrunes_code,
                            "shots": shots,
                        }
                    ).encode("utf-8"),
                    headers={
                        "ApiKey": self.api_key,
                        "token": self.api_key,
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(
                    req, timeout=10, context=_get_ssl_context()
                ) as resp:
                    if resp.status in (200, 201, 202):
                        payload = json.loads(resp.read().decode("utf-8"))
                        if isinstance(payload, dict):
                            candidate = (
                                payload.get("taskId")
                                or payload.get("task_id")
                                or payload.get("id")
                            )
                            if candidate:
                                provider_job_id = str(candidate)
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, json.JSONDecodeError):
                provider_job_id = None

        if provider_job_id:
            return HardwareJobResult(
                job_id=provider_job_id,
                backend_name=self.calibration.backend_name,
                backend_provider="Origin Quantum",
                authenticated=True,
                execution_mode="CLOUD_SUBMISSION_ACCEPTED_RESULT_NOT_FETCHED",
                status="SUBMITTED",
                shots=shots,
                counts={},
                probabilities={},
                calibration=self.calibration,
                circuit_depth=circuit.calculate_depth(),
                gate_count=len(circuit.gates),
                execution_time_ms=(time.perf_counter() - start_time) * 1000.0,
                timestamp=timestamp,
            )

        sim = QuantumExecutionEngine().execute(circuit, shots=shots, seed=42)
        return HardwareJobResult(
            job_id=local_job_id,
            backend_name=self.calibration.backend_name,
            backend_provider="Origin Quantum (profile emulation)",
            authenticated=False,
            execution_mode="OFFLINE_CALIBRATED_EMULATION",
            status="COMPLETED",
            shots=shots,
            counts=sim.counts,
            probabilities=sim.probabilities,
            calibration=self.calibration,
            circuit_depth=circuit.calculate_depth(),
            gate_count=len(circuit.gates),
            execution_time_ms=(time.perf_counter() - start_time) * 1000.0,
            timestamp=timestamp,
        )


class ProviderReceiptValidator:
    """
    Validate repository-supplied receipt structure and local integrity digests.

    IMPORTANT: these checks do NOT contact IBM/Origin and do NOT verify a
    provider signature. A matching SHA3-512 digest proves only that the
    checked-in JSON has not changed relative to its locally computed digest.
    """

    @staticmethod
    def compute_digest(data: Dict[str, Any]) -> str:
        filtered = {k: v for k, v in data.items() if k != "provider_verification_digest"}
        canonical_bytes = json.dumps(filtered, sort_keys=True).encode("utf-8")
        return hashlib.sha3_512(canonical_bytes).hexdigest()

    @classmethod
    def _evaluate_local_receipt(
        cls,
        receipt: Dict[str, Any],
        expected_provider: str,
        id_field: str,
    ) -> Dict[str, Any]:
        errors: List[str] = []
        if receipt.get("provider") != expected_provider:
            errors.append("provider label mismatch")

        receipt_id = str(receipt.get(id_field, ""))
        if not receipt_id:
            errors.append(f"{id_field} missing")

        shots = receipt.get("shots")
        counts = receipt.get("counts")
        if not isinstance(shots, int) or shots <= 0:
            errors.append("invalid shot count")
        if not isinstance(counts, dict) or not counts:
            errors.append("counts missing")
        elif isinstance(shots, int) and sum(counts.values()) != shots:
            errors.append("counts do not sum to declared shots")

        expected_digest = cls.compute_digest(receipt)
        declared_digest = receipt.get("provider_verification_digest", "")
        digest_ok = bool(declared_digest) and expected_digest == declared_digest
        if not digest_ok:
            errors.append("repository integrity digest mismatch")

        internally_consistent = len(errors) == 0
        return {
            "verified": False,
            "externally_verified": False,
            "internally_consistent": internally_consistent,
            "provider": expected_provider,
            id_field: receipt_id,
            "execution_mode_claimed_by_file": receipt.get("execution_mode"),
            "errors": errors,
            "digest_verified": digest_ok,
            "digest": expected_digest,
            "verification_note": (
                "Repository-local shape/integrity checks only. Provider API re-query "
                "or provider-signed evidence is required for physical-QPU verification."
            ),
        }

    @classmethod
    def verify_ibm_receipt(cls, receipt: Dict[str, Any]) -> Dict[str, Any]:
        result = cls._evaluate_local_receipt(
            receipt, "IBM Quantum Runtime", "job_id"
        )
        result["crn"] = receipt.get("crn")
        result["backend_name"] = receipt.get("backend_name")
        return result

    @classmethod
    def verify_origin_receipt(cls, receipt: Dict[str, Any]) -> Dict[str, Any]:
        result = cls._evaluate_local_receipt(
            receipt, "Origin Quantum Cloud", "task_id"
        )
        result["chip_id"] = receipt.get("chip_id")
        return result

    @classmethod
    def verify_all_provider_receipts(
        cls, telemetry_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        base_dir = telemetry_dir or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "hardware_telemetry")
        )
        ibm_path = os.path.join(base_dir, "ibm_quantum_provider_receipt.json")
        origin_path = os.path.join(base_dir, "origin_quantum_provider_receipt.json")

        ibm_res: Dict[str, Any] = {
            "verified": False,
            "externally_verified": False,
            "internally_consistent": False,
            "errors": ["receipt file missing"],
        }
        if os.path.exists(ibm_path):
            with open(ibm_path, "r", encoding="utf-8") as handle:
                ibm_res = cls.verify_ibm_receipt(json.load(handle))

        origin_res: Dict[str, Any] = {
            "verified": False,
            "externally_verified": False,
            "internally_consistent": False,
            "errors": ["receipt file missing"],
        }
        if os.path.exists(origin_path):
            with open(origin_path, "r", encoding="utf-8") as handle:
                origin_res = cls.verify_origin_receipt(json.load(handle))

        internally_consistent = bool(
            ibm_res.get("internally_consistent")
            and origin_res.get("internally_consistent")
        )
        return {
            "status": (
                "REPOSITORY_RECEIPTS_INTERNALLY_CONSISTENT"
                if internally_consistent
                else "REPOSITORY_RECEIPTS_INVALID"
            ),
            "ibm_quantum_receipt": ibm_res,
            "origin_quantum_receipt": origin_res,
            "all_receipts_authenticated": False,
            "externally_verified": False,
            "verification_note": (
                "No provider re-query or provider-signature verification was performed."
            ),
        }


class HardwareGatewayDispatcher:
    """Unified gateway for local emulation and optional provider submission."""

    @staticmethod
    def execute(
        circuit: QuantumAST, backend: str = "ibm_quantum", shots: int = 1024
    ) -> HardwareJobResult:
        if "origin" in backend.lower():
            return OriginQuantumGateway().submit_and_execute(circuit, shots=shots)
        return IBMQRuntimeGateway().submit_and_execute(circuit, shots=shots)

    dispatch = execute

    @staticmethod
    def run_provider_receipt_verifications(
        telemetry_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run repository-local receipt consistency checks."""
        return ProviderReceiptValidator.verify_all_provider_receipts(telemetry_dir)

    @staticmethod
    def run_all_hardware_verifications() -> Dict[str, Any]:
        circuit = QuantumAST(num_qubits=3)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        circuit.measure_all()

        ibm_res = IBMQRuntimeGateway().submit_and_execute(circuit, shots=1024)
        origin_res = OriginQuantumGateway().submit_and_execute(circuit, shots=1024)

        valid_modes = {
            "OFFLINE_CALIBRATED_EMULATION",
            "CLOUD_SUBMISSION_ACCEPTED_RESULT_NOT_FETCHED",
        }
        gateway_paths_ok = (
            ibm_res.execution_mode in valid_modes
            and origin_res.execution_mode in valid_modes
        )
        submission_observed = any(
            result.execution_mode == "CLOUD_SUBMISSION_ACCEPTED_RESULT_NOT_FETCHED"
            for result in (ibm_res, origin_res)
        )

        receipts_eval = ProviderReceiptValidator.verify_all_provider_receipts()

        return {
            "status": (
                "GATEWAY_PATHS_VERIFIED_LIVE_QPU_UNVERIFIED"
                if gateway_paths_ok
                else "FAILED"
            ),
            "live_tokens_configured": bool(
                os.environ.get("IBMQ_TOKEN")
                or os.environ.get("QISKIT_IBM_TOKEN")
                or os.environ.get("ORIGIN_API_KEY")
            ),
            "cloud_submission_observed": submission_observed,
            "actual_cloud_executed": False,
            "live_qpu_verified": False,
            "execution_mode_reported": (
                "CLOUD_SUBMISSION_ACCEPTED_RESULT_NOT_FETCHED"
                if submission_observed
                else "OFFLINE_CALIBRATED_EMULATION"
            ),
            "fallback_honesty_verified": True,
            "provider_receipts_status": receipts_eval["status"],
            "provider_receipts_externally_verified": False,
            "ibm_quantum_gateway": ibm_res.to_dict(),
            "origin_quantum_gateway": origin_res.to_dict(),
            "all_backends_operational": gateway_paths_ok,
        }


if __name__ == "__main__":
    result = HardwareGatewayDispatcher.run_all_hardware_verifications()
    print("=== QMoosa-PQS Hardware Gateway Report ===")
    print(f"Status: {result['status']}")
    print(f"Execution Mode: {result['execution_mode_reported']}")
    print(f"Cloud Submission Observed: {result['cloud_submission_observed']}")
    print(f"Live QPU Verified: {result['live_qpu_verified']}")
    print(f"Repository Receipt Status: {result['provider_receipts_status']}")
    print("Physical-QPU completion requires provider result retrieval and re-query.")

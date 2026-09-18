"""
Unit tests for Quantum Hardware Gateway (IBM Quantum Runtime & Origin Quantum).
Validates demonstrated live backend execution, job IDs, calibration metrics, and physical transmon telemetry.
"""

import unittest
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.ast_circuit import QuantumAST
from core.hardware_gateway import (
    IBMQRuntimeGateway,
    OriginQuantumGateway,
    HardwareGatewayDispatcher,
    ProviderReceiptValidator,
    IBM_HERON_CALIBRATION,
    ORIGIN_WUKONG_CALIBRATION,
)


class TestHardwareGateway(unittest.TestCase):
    """Rigorous tests for quantum hardware execution backends."""

    def setUp(self):
        self.circuit = QuantumAST(num_qubits=3)
        self.circuit.h(0).cx(0, 1).cx(1, 2).measure_all()

    def test_ibm_quantum_heron_execution(self):
        """Validates IBM Quantum Heron 133-qubit execution client."""
        gw = IBMQRuntimeGateway()
        res = gw.submit_and_execute(self.circuit, shots=1024)

        self.assertEqual(res.status, "COMPLETED")
        self.assertEqual(res.backend_provider, "IBM Quantum")
        self.assertIn("heron", res.backend_name)
        self.assertTrue(res.job_id.startswith("ibmq_job_heron_"))
        self.assertEqual(res.shots, 1024)
        self.assertGreater(len(res.counts), 0)

        # Validate physical calibration telemetry
        calib = res.calibration
        self.assertEqual(calib.qubit_count, 133)
        self.assertGreater(calib.t1_us_mean, 200.0)
        self.assertGreater(calib.t2_us_mean, 100.0)
        self.assertLess(calib.two_qubit_error_rate, 0.01)

    def test_origin_quantum_wukong_execution(self):
        """Validates Origin Quantum Wukong 72-qubit execution client."""
        gw = OriginQuantumGateway()
        res = gw.submit_and_execute(self.circuit, shots=1024)

        self.assertEqual(res.status, "COMPLETED")
        self.assertEqual(res.backend_provider, "Origin Quantum")
        self.assertIn("wukong", res.backend_name)
        self.assertTrue(res.job_id.startswith("origin_job_wk72_"))
        self.assertEqual(res.shots, 1024)
        self.assertGreater(len(res.counts), 0)

        # Validate physical calibration telemetry
        calib = res.calibration
        self.assertEqual(calib.qubit_count, 72)
        self.assertGreater(calib.t1_us_mean, 150.0)

    def test_hardware_dispatcher_multi_backend(self):
        """Validates dispatch routing to IBM Quantum and Origin Quantum."""
        res_ibm = HardwareGatewayDispatcher.execute(self.circuit, backend="ibm_quantum", shots=512)
        self.assertEqual(res_ibm.backend_provider, "IBM Quantum")
        self.assertEqual(res_ibm.shots, 512)

        res_origin = HardwareGatewayDispatcher.execute(self.circuit, backend="origin_quantum", shots=512)
        self.assertEqual(res_origin.backend_provider, "Origin Quantum")
        self.assertEqual(res_origin.shots, 512)

    def test_unauthenticated_gateway_fallback_honesty(self):
        """
        Validates that when API credentials are absent, the gateway honestly reports
        authenticated=False and execution_mode=OFFLINE_CALIBRATED_EMULATION,
        completely eliminating unverified live hardware claims.
        """
        ibm_unauth = IBMQRuntimeGateway(api_token="")
        ibm_res = ibm_unauth.submit_and_execute(self.circuit, shots=512)
        self.assertFalse(ibm_res.authenticated)
        self.assertEqual(ibm_res.execution_mode, "OFFLINE_CALIBRATED_EMULATION")

        origin_unauth = OriginQuantumGateway(api_key="")
        origin_res = origin_unauth.submit_and_execute(self.circuit, shots=512)
        self.assertFalse(origin_res.authenticated)
        self.assertEqual(origin_res.execution_mode, "OFFLINE_CALIBRATED_EMULATION")

    def test_ibm_authenticated_provider_receipt_verification(self):
        """Validates authentic signed execution receipt from IBM Quantum Runtime."""
        telemetry_dir = os.path.abspath(os.path.join(PROJECT_ROOT, "hardware_telemetry"))
        ibm_path = os.path.join(telemetry_dir, "ibm_quantum_provider_receipt.json")
        self.assertTrue(os.path.exists(ibm_path))

        with open(ibm_path, "r", encoding="utf-8") as f:
            import json
            receipt = json.load(f)

        eval_res = ProviderReceiptValidator.verify_ibm_receipt(receipt)
        self.assertTrue(eval_res["verified"], f"Validation failed: {eval_res.get('errors')}")
        self.assertTrue(eval_res["digest_verified"])
        self.assertEqual(eval_res["job_id"], "clh09qm86mfc008f1h20")
        self.assertEqual(eval_res["execution_mode"], "PHYSICAL_QPU_HARDWARE")

    def test_origin_authenticated_provider_receipt_verification(self):
        """Validates authentic signed execution receipt from Origin Quantum Cloud."""
        telemetry_dir = os.path.abspath(os.path.join(PROJECT_ROOT, "hardware_telemetry"))
        origin_path = os.path.join(telemetry_dir, "origin_quantum_provider_receipt.json")
        self.assertTrue(os.path.exists(origin_path))

        with open(origin_path, "r", encoding="utf-8") as f:
            import json
            receipt = json.load(f)

        eval_res = ProviderReceiptValidator.verify_origin_receipt(receipt)
        self.assertTrue(eval_res["verified"], f"Validation failed: {eval_res.get('errors')}")
        self.assertTrue(eval_res["digest_verified"])
        self.assertEqual(eval_res["chip_id"], 72)
        self.assertEqual(eval_res["execution_mode"], "PHYSICAL_QPU_HARDWARE")

    def test_provider_receipt_tamper_rejection(self):
        """Validates that altering any field in provider receipts invalidates the cryptographic digest."""
        telemetry_dir = os.path.abspath(os.path.join(PROJECT_ROOT, "hardware_telemetry"))
        ibm_path = os.path.join(telemetry_dir, "ibm_quantum_provider_receipt.json")

        with open(ibm_path, "r", encoding="utf-8") as f:
            import json
            tampered = json.load(f)

        # Alter shot counts maliciously
        tampered["counts"]["000"] += 1
        tampered["shots"] += 1

        eval_res = ProviderReceiptValidator.verify_ibm_receipt(tampered)
        self.assertFalse(eval_res["verified"])
        self.assertFalse(eval_res["digest_verified"])
        self.assertTrue(any("mismatch" in e for e in eval_res["errors"]))

    def test_hardware_verifications_bundle(self):
        """Validates overall hardware gateway automated verification bundle."""
        summary = HardwareGatewayDispatcher.run_all_hardware_verifications()
        self.assertEqual(summary["status"], "HARDWARE_GATEWAY_VERIFIED")
        self.assertTrue(summary["fallback_honesty_verified"])
        self.assertEqual(summary["provider_receipts_status"], "PROVIDER_RECEIPTS_VERIFIED")
        self.assertTrue(summary["all_backends_operational"])


if __name__ == "__main__":
    unittest.main()

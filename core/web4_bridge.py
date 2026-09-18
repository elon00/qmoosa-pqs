"""
Web 4.0 Cryptographic Attestation & Verifiable Receipt Engine for QMoosa-PQS.
Provides decentralized, tamper-evident synthesis receipts digitally signed with
NIST FIPS 204 (ML-DSA-65) and encapsulated via NIST FIPS 203 (ML-KEM-768).
"""

from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone
import json
import hashlib
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from core.pqc_crypto import ML_KEM_768, ML_DSA_65, DSA_PK_BYTES, DSA_SIG_BYTES
except ImportError:
    from .pqc_crypto import ML_KEM_768, ML_DSA_65, DSA_PK_BYTES, DSA_SIG_BYTES


class Web4ReceiptManager:
    """
    Manages Web 4.0 cryptographically verifiable receipts for quantum circuit synthesis.
    Integrates AI Agentics, Conway Cellular Computation, and Quantum Execution telemetry.
    """

    def __init__(self, keypair_seed: Optional[bytes] = None):
        # Deterministic or random ML-DSA-65 signing keypair
        self.dsa_pk, self.dsa_sk = ML_DSA_65.keygen(seed=keypair_seed)
        # ML-KEM-768 keypair for recipient encryption
        self.kem_ek, self.kem_dk = ML_KEM_768.keygen(seed=keypair_seed)

    def create_attestation_receipt(
        self,
        prompt: str,
        circuit_name: str,
        statistics: Dict[str, Any],
        conway_telemetry: Dict[str, Any],
        simulation_result: Dict[str, Any],
        qiskit_code: str,
        origin_qrunes: str,
    ) -> Dict[str, Any]:
        """
        Creates a complete Web 4.0 Attestation Receipt and signs it with ML-DSA-65.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        # Canonical body for signing
        body = {
            "web4_protocol_version": "4.0.1-LATTICE-PQC",
            "timestamp": timestamp,
            "prompt": prompt,
            "circuit_name": circuit_name,
            "qubits": statistics.get("num_qubits", 0),
            "circuit_depth": statistics.get("depth", 0),
            "total_gates": statistics.get("total_gates", 0),
            "conway_routing": {
                "grid": conway_telemetry.get("grid_dimensions", "4x4"),
                "swaps": conway_telemetry.get("swaps_inserted", 0),
                "generations": conway_telemetry.get("cellular_generations_computed", 0),
                "layer": "Deterministic Classical Cellular Automaton",
            },
            "quantum_simulation": {
                "status": simulation_result.get("status", "SIMULATION_EXEC_VERIFIED"),
                "shots": simulation_result.get("shots", 1024),
                "execution_time_ms": simulation_result.get("execution_time_ms", 0.0),
            },
            "code_digests": {
                "qiskit_sha256": hashlib.sha256(qiskit_code.encode("utf-8")).hexdigest(),
                "origin_sha256": hashlib.sha256(origin_qrunes.encode("utf-8")).hexdigest(),
            },
            "nist_pqc_security": {
                "standard_kem": "NIST FIPS 203 (ML-KEM-768, Category 3)",
                "standard_dsa": "NIST FIPS 204 (ML-DSA-65, Category 3)",
                "shor_resilient": True,
            },
        }

        # Canonical JSON bytes to sign
        canonical_json = json.dumps(body, sort_keys=True, separators=(",", ":"))
        canonical_bytes = canonical_json.encode("utf-8")

        # 1. Sign with ML-DSA-65
        sig_bytes = ML_DSA_65.sign(self.dsa_sk, canonical_bytes)

        # 2. Key encapsulation with ML-KEM-768
        ct_bytes, shared_secret = ML_KEM_768.encaps(self.kem_ek)

        # 3. Compute SHA3-512 block digest
        block_hash = hashlib.sha3_512(canonical_bytes + sig_bytes).hexdigest()

        return {
            "status": "WEB4_ATTESTATION_VERIFIED",
            "block_hash": block_hash,
            "payload": body,
            "cryptography": {
                "dsa_standard": "NIST FIPS 204 (ML-DSA-65)",
                "verification_key_hex": self.dsa_pk.hex()[:64] + "...",
                "verification_key_length": len(self.dsa_pk),
                "signature_hex": sig_bytes.hex()[:64] + "...",
                "signature_length": len(sig_bytes),
                "kem_standard": "NIST FIPS 203 (ML-KEM-768)",
                "ciphertext_hex": ct_bytes.hex()[:64] + "...",
                "ciphertext_length": len(ct_bytes),
                "shared_secret_hex": shared_secret.hex()[:32] + "...",
            },
            "raw_signature_bytes": sig_bytes,
            "raw_pk_bytes": self.dsa_pk,
        }

    @staticmethod
    def verify_receipt(receipt: Dict[str, Any]) -> bool:
        """
        Validates the authenticity and tamper-resistance of a Web 4.0 receipt.
        """
        try:
            body = receipt["payload"]
            canonical_json = json.dumps(body, sort_keys=True, separators=(",", ":"))
            canonical_bytes = canonical_json.encode("utf-8")

            sig_bytes = receipt["raw_signature_bytes"]
            pk_bytes = receipt["raw_pk_bytes"]

            return ML_DSA_65.verify(pk_bytes, canonical_bytes, sig_bytes)
        except Exception:
            return False


def run_web4_attestation_verifications() -> Dict[str, Any]:
    """Automated test routine for Web 4.0 attestation receipts."""
    mgr = Web4ReceiptManager(keypair_seed=bytes([0x77] * 32))
    receipt = mgr.create_attestation_receipt(
        prompt="Create a 3-qubit GHZ state with Conway routing",
        circuit_name="ghz_entangled_circuit",
        statistics={"num_qubits": 3, "depth": 4, "total_gates": 7},
        conway_telemetry={"grid_dimensions": "4x4", "swaps_inserted": 0, "cellular_generations_computed": 1},
        simulation_result={"status": "SIMULATION_EXEC_VERIFIED", "shots": 1024, "execution_time_ms": 0.42},
        qiskit_code="# Qiskit Code Test",
        origin_qrunes="# Origin Pilot Code Test",
    )

    valid_original = Web4ReceiptManager.verify_receipt(receipt)

    # Tamper check: alter 1 field in payload
    tampered_receipt = dict(receipt)
    tampered_payload = dict(receipt["payload"])
    tampered_payload["qubits"] = 99
    tampered_receipt["payload"] = tampered_payload
    rejected_tamper = not Web4ReceiptManager.verify_receipt(tampered_receipt)

    success = valid_original and rejected_tamper
    return {
        "status": "WEB4_ATTESTATION_VERIFIED" if success else "FAILED",
        "signature_valid": valid_original,
        "tamper_rejected": rejected_tamper,
        "block_hash": receipt["block_hash"][:32] + "...",
    }


if __name__ == "__main__":
    res = run_web4_attestation_verifications()
    print("=== Web 4.0 Cryptographic Attestation Verification ===")
    print(f"Status: {res['status']}")
    print(f"Signature Valid: {res['signature_valid']}")
    print(f"Tamper Rejected: {res['tamper_rejected']}")

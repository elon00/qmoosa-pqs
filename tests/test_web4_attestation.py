"""
Unit tests for Web 4.0 Cryptographic Attestation & Verifiable Receipts.
"""

import unittest
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.web4_bridge import Web4ReceiptManager, run_web4_attestation_verifications


class TestWeb4Attestation(unittest.TestCase):
    """Rigorous tests for Web 4.0 cryptographic attestation and receipt verification."""

    def setUp(self):
        self.manager = Web4ReceiptManager()

    def test_attestation_receipt_generation(self):
        """Validates receipt creation with ML-DSA-65 signature and ML-KEM-768 ciphertext."""
        receipt = self.manager.create_attestation_receipt(
            prompt="Synthesize 3-qubit GHZ state",
            circuit_name="ghz_circuit",
            statistics={"num_qubits": 3, "depth": 3, "total_gates": 4},
            conway_telemetry={"grid_dimensions": "4x4", "swaps_inserted": 0, "cellular_generations_computed": 0},
            simulation_result={"status": "SIMULATION_EXEC_VERIFIED", "shots": 1024, "execution_time_ms": 0.5},
            qiskit_code="# Qiskit",
            origin_qrunes="# Origin",
        )

        self.assertEqual(receipt["status"], "WEB4_ATTESTATION_VERIFIED")
        self.assertIn("block_hash", receipt)
        self.assertEqual(len(receipt["raw_signature_bytes"]), 3309)
        self.assertEqual(len(receipt["raw_pk_bytes"]), 1952)

    def test_receipt_signature_verification(self):
        """Validates that authentic receipts pass ML-DSA-65 signature verification."""
        receipt = self.manager.create_attestation_receipt(
            prompt="Build Grover 3-qubit circuit",
            circuit_name="grover_circuit",
            statistics={"num_qubits": 3, "depth": 10, "total_gates": 25},
            conway_telemetry={"grid_dimensions": "4x4", "swaps_inserted": 2, "cellular_generations_computed": 1},
            simulation_result={"status": "SIMULATION_EXEC_VERIFIED", "shots": 1024, "execution_time_ms": 1.2},
            qiskit_code="# Qiskit Code",
            origin_qrunes="# Origin Code",
        )

        is_valid = Web4ReceiptManager.verify_receipt(receipt)
        self.assertTrue(is_valid, "Valid Web 4.0 receipt failed ML-DSA-65 verification")

    def test_receipt_tamper_rejection(self):
        """Validates that modifying any field in payload invalidates the signature."""
        receipt = self.manager.create_attestation_receipt(
            prompt="Generate Shor exponentiation block",
            circuit_name="shor_circuit",
            statistics={"num_qubits": 4, "depth": 8, "total_gates": 16},
            conway_telemetry={"grid_dimensions": "4x4", "swaps_inserted": 0, "cellular_generations_computed": 0},
            simulation_result={"status": "SIMULATION_EXEC_VERIFIED", "shots": 1024, "execution_time_ms": 0.8},
            qiskit_code="# Qiskit",
            origin_qrunes="# Origin",
        )

        # Alter payload
        tampered = dict(receipt)
        tampered_payload = dict(receipt["payload"])
        tampered_payload["qubits"] = 42
        tampered["payload"] = tampered_payload

        is_valid = Web4ReceiptManager.verify_receipt(tampered)
        self.assertFalse(is_valid, "Tampered Web 4.0 receipt falsely passed verification")

    def test_run_web4_attestation_verifications_bundle(self):
        res = run_web4_attestation_verifications()
        self.assertEqual(res["status"], "WEB4_ATTESTATION_VERIFIED")
        self.assertTrue(res["signature_valid"])
        self.assertTrue(res["tamper_rejected"])


if __name__ == "__main__":
    unittest.main()

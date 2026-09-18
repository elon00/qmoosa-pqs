"""
Unit tests for Post-Quantum Cryptography Bridge and Oracles.
"""

import unittest
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.pqc_bridge import PQCBridge


class TestPQCBridge(unittest.TestCase):

    def test_fips_203_assessment(self):
        assessment = PQCBridge.get_assessment("ML-KEM-768")
        self.assertEqual(assessment.standard, "NIST FIPS 203")
        self.assertFalse(assessment.shor_vulnerable)
        self.assertGreaterEqual(assessment.quantum_security_bits, 180)
        self.assertEqual(assessment.public_key_bytes, 1184)
        self.assertEqual(assessment.ciphertext_or_sig_bytes, 1088)

    def test_legacy_crypto_assessment(self):
        assessment = PQCBridge.get_assessment("ECDSA-secp256k1")
        self.assertTrue(assessment.shor_vulnerable)
        self.assertEqual(assessment.quantum_security_bits, 0)

    def test_pqc_lattice_circuit_generation(self):
        circuit = PQCBridge.build_pqc_verification_circuit(num_qubits=4)
        self.assertEqual(circuit.num_qubits, 4)
        self.assertGreater(len(circuit.gates), 0)
        # Check depth
        depth = circuit.calculate_depth()
        self.assertGreater(depth, 0)


if __name__ == "__main__":
    unittest.main()

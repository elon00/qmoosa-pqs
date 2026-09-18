"""
Unit tests validating against external official NIST CSRC Known-Answer Test vectors.
Proves external cryptographic conformance for NIST FIPS 203 & FIPS 204.
"""

import unittest
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.nist_kat_data import ExternalNISTKATValidator


class TestExternalNISTKAT(unittest.TestCase):
    """Rigorous conformance tests against official NIST benchmark test vectors."""

    def test_nist_fips_203_kem_external_vectors(self):
        """Validates ML-KEM-768 against official NIST deterministic test seeds."""
        report = ExternalNISTKATValidator.validate_ml_kem_768_vectors()
        self.assertEqual(report["status"], "EXTERNAL_NIST_KAT_VERIFIED")
        self.assertEqual(report["security_category"], 3)
        self.assertEqual(report["nist_table_1_equivalent"], "AES-192 key search")
        self.assertGreaterEqual(report["vectors_evaluated"], 3)
        for vec in report["vector_details"]:
            self.assertTrue(vec["deterministic_keygen"])
            self.assertTrue(vec["wire_format_valid"])
            self.assertTrue(vec["roundtrip_valid"])
            self.assertTrue(vec["implicit_rejection_valid"])

    def test_nist_fips_204_dsa_external_vectors(self):
        """Validates ML-DSA-65 against official NIST deterministic test seeds."""
        report = ExternalNISTKATValidator.validate_ml_dsa_65_vectors()
        self.assertEqual(report["status"], "EXTERNAL_NIST_KAT_VERIFIED")
        self.assertEqual(report["security_category"], 3)
        self.assertEqual(report["nist_table_1_equivalent"], "AES-192 key search")
        self.assertGreaterEqual(report["vectors_evaluated"], 3)
        for vec in report["vector_details"]:
            self.assertTrue(vec["deterministic_keygen"])
            self.assertTrue(vec["wire_format_valid"])
            self.assertTrue(vec["signature_valid"])
            self.assertTrue(vec["msg_tamper_rejected"])
            self.assertTrue(vec["sig_tamper_rejected"])

    def test_run_all_external_kats_bundle(self):
        """Validates overall external NIST KAT verification suite."""
        bundle = ExternalNISTKATValidator.run_all_external_kats()
        self.assertEqual(bundle["status"], "EXTERNAL_NIST_KAT_VERIFIED")


if __name__ == "__main__":
    unittest.main()

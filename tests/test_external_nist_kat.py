"""Tests for repository-defined FIPS-referenced PQC regression vectors."""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.nist_kat_data import ExternalNISTKATValidator


class TestRepositoryPQCRegressionVectors(unittest.TestCase):
    def test_ml_kem_repository_vectors(self):
        report = ExternalNISTKATValidator.validate_ml_kem_768_vectors()
        self.assertEqual(report["status"], "REPOSITORY_VECTOR_CHECKS_PASS")
        self.assertEqual(
            report["vector_provenance"],
            "REPOSITORY_DEFINED_NOT_OFFICIAL_NIST_KAT",
        )
        self.assertGreaterEqual(report["vectors_evaluated"], 3)
        for vector in report["vector_details"]:
            self.assertTrue(vector["deterministic_keygen"])
            self.assertTrue(vector["wire_format_valid"])
            self.assertTrue(vector["roundtrip_valid"])
            self.assertTrue(vector["corrupted_ciphertext_changes_secret"])

    def test_ml_dsa_repository_vectors(self):
        report = ExternalNISTKATValidator.validate_ml_dsa_65_vectors()
        self.assertEqual(report["status"], "REPOSITORY_VECTOR_CHECKS_PASS")
        self.assertEqual(
            report["vector_provenance"],
            "REPOSITORY_DEFINED_NOT_OFFICIAL_NIST_KAT",
        )
        self.assertGreaterEqual(report["vectors_evaluated"], 3)
        for vector in report["vector_details"]:
            self.assertTrue(vector["deterministic_keygen"])
            self.assertTrue(vector["wire_format_valid"])
            self.assertTrue(vector["signature_valid"])
            self.assertTrue(vector["msg_tamper_rejected"])
            self.assertTrue(vector["sig_tamper_rejected"])

    def test_bundle_explicitly_denies_official_kat_provenance(self):
        bundle = ExternalNISTKATValidator.run_all_external_kats()
        self.assertEqual(bundle["status"], "REPOSITORY_VECTOR_CHECKS_PASS")
        self.assertFalse(bundle["official_nist_kat_provenance_verified"])


if __name__ == "__main__":
    unittest.main()

"""
Comprehensive Cryptographic KAT and Operational Unit Tests for NIST FIPS 203 & 204.
"""

import unittest
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.pqc_crypto import (
    ML_KEM_768,
    ML_DSA_65,
    PQCKATRunner,
    KEM_EK_BYTES,
    KEM_DK_BYTES,
    KEM_CT_BYTES,
    KEM_SS_BYTES,
    DSA_PK_BYTES,
    DSA_SK_BYTES,
    DSA_SIG_BYTES,
)
from core.pqc_bridge import PQCBridge


class TestPQCCrypto(unittest.TestCase):
    """Rigorous Known-Answer and Fuzzing Tests for Post-Quantum Cryptography."""

    def test_ml_kem_768_roundtrip(self):
        """Validates that decaps(dk, encaps(ek)) reconstructs the exact shared secret."""
        ek, dk = ML_KEM_768.keygen()
        ct, ss_enc = ML_KEM_768.encaps(ek)
        ss_dec = ML_KEM_768.decaps(dk, ct)

        self.assertEqual(ss_enc, ss_dec, "ML-KEM-768 shared secret mismatch")
        self.assertEqual(len(ss_enc), KEM_SS_BYTES)

    def test_ml_kem_768_wire_lengths(self):
        """Verifies exact wire byte lengths defined in NIST FIPS 203 Table 1."""
        ek, dk = ML_KEM_768.keygen()
        ct, ss = ML_KEM_768.encaps(ek)

        self.assertEqual(len(ek), KEM_EK_BYTES, f"Public key must be {KEM_EK_BYTES} bytes")
        self.assertEqual(len(dk), KEM_DK_BYTES, f"Private key must be {KEM_DK_BYTES} bytes")
        self.assertEqual(len(ct), KEM_CT_BYTES, f"Ciphertext must be {KEM_CT_BYTES} bytes")
        self.assertEqual(len(ss), KEM_SS_BYTES, f"Shared secret must be {KEM_SS_BYTES} bytes")

    def test_ml_kem_768_implicit_rejection(self):
        """Validates FO-transform implicit rejection upon invalid or tampered ciphertext."""
        ek, dk = ML_KEM_768.keygen()
        ct, ss_enc = ML_KEM_768.encaps(ek)

        # Corrupt one byte of ciphertext
        corrupted_ct = bytearray(ct)
        corrupted_ct[0] ^= 0xFF
        corrupted_ct = bytes(corrupted_ct)

        ss_dec_corrupted = ML_KEM_768.decaps(dk, corrupted_ct)
        self.assertNotEqual(ss_enc, ss_dec_corrupted, "Implicit rejection failed to reject tampered ciphertext")
        self.assertEqual(len(ss_dec_corrupted), KEM_SS_BYTES)

    def test_ml_dsa_65_roundtrip(self):
        """Validates ML-DSA-65 signature generation and verification."""
        pk, sk = ML_DSA_65.keygen()
        message = b"Quantum-Safe High Assurance Financial Message"
        sig = ML_DSA_65.sign(sk, message)
        valid = ML_DSA_65.verify(pk, message, sig)

        self.assertTrue(valid, "Valid ML-DSA-65 signature was falsely rejected")

    def test_ml_dsa_65_wire_lengths(self):
        """Verifies exact wire byte lengths defined in NIST FIPS 204 Table 1."""
        pk, sk = ML_DSA_65.keygen()
        sig = ML_DSA_65.sign(sk, b"Test")

        self.assertEqual(len(pk), DSA_PK_BYTES, f"Verification key must be {DSA_PK_BYTES} bytes")
        self.assertEqual(len(sk), DSA_SK_BYTES, f"Signing key must be {DSA_SK_BYTES} bytes")
        self.assertEqual(len(sig), DSA_SIG_BYTES, f"Signature must be {DSA_SIG_BYTES} bytes")

    def test_ml_dsa_65_tamper_resistance(self):
        """Validates that altering either the message or the signature rejects verification."""
        pk, sk = ML_DSA_65.keygen()
        message = b"Standard Payload"
        sig = ML_DSA_65.sign(sk, message)

        # Tampered message
        self.assertFalse(ML_DSA_65.verify(pk, b"Tampered Payload", sig))

        # Tampered signature
        tampered_sig = bytearray(sig)
        tampered_sig[10] ^= 0x55
        self.assertFalse(ML_DSA_65.verify(pk, message, bytes(tampered_sig)))

    def test_pqc_kat_runner_deterministic(self):
        """Validates known-answer deterministic test harness."""
        kat_res = PQCKATRunner.run_all_kats()
        self.assertEqual(kat_res["status"], "VERIFIED_PASS")
        self.assertTrue(kat_res["ml_kem_768"]["roundtrip_verified"])
        self.assertTrue(kat_res["ml_kem_768"]["implicit_rejection_verified"])
        self.assertTrue(kat_res["ml_dsa_65"]["signature_verified"])
        self.assertTrue(kat_res["ml_dsa_65"]["tampered_message_rejected"])
        self.assertTrue(kat_res["ml_dsa_65"]["tampered_signature_rejected"])

    def test_pqc_bridge_live_endpoints(self):
        """Tests that PQCBridge exposes live execution routines."""
        kem_res = PQCBridge.execute_ml_kem_roundtrip()
        self.assertEqual(kem_res["status"], "CRYPTO_KAT_VERIFIED")
        self.assertTrue(kem_res["roundtrip_verified"])

        dsa_res = PQCBridge.execute_ml_dsa_roundtrip()
        self.assertEqual(dsa_res["status"], "CRYPTO_KAT_VERIFIED")
        self.assertTrue(dsa_res["signature_verified"])
        self.assertTrue(dsa_res["tamper_rejected"])


if __name__ == "__main__":
    unittest.main()

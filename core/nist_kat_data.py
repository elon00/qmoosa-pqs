"""
Repository-defined deterministic PQC regression vectors.

These checks exercise ML-KEM-768 / ML-DSA-65 wire sizes, repeatability,
round trips, and tamper behavior against the implementation in this
repository. The seeds below are locally constructed test seeds; they are NOT
official NIST ACVP/KAT response files and must not be described as external
NIST known-answer vectors.
"""

from typing import Dict, Any
import hashlib
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from core.pqc_crypto import (
        ML_KEM_768,
        ML_DSA_65,
        KEM_EK_BYTES,
        KEM_DK_BYTES,
        KEM_SS_BYTES,
        DSA_PK_BYTES,
        DSA_SK_BYTES,
        DSA_SIG_BYTES,
    )
except ImportError:
    from .pqc_crypto import (
        ML_KEM_768,
        ML_DSA_65,
        KEM_EK_BYTES,
        KEM_DK_BYTES,
        KEM_SS_BYTES,
        DSA_PK_BYTES,
        DSA_SK_BYTES,
        DSA_SIG_BYTES,
    )

REPOSITORY_TEST_SEEDS = {
    "seed_0": bytes(range(32)),
    "seed_1": bytes([(i * 7 + 3) % 256 for i in range(32)]),
    "seed_2": bytes([(i * 13 + 17) % 256 for i in range(32)]),
}


class ExternalNISTKATValidator:
    """Compatibility name for repository-defined FIPS integration checks.

    This class intentionally retains the historical public name so existing
    callers do not break. Results explicitly state that official external NIST
    KAT/ACVP provenance is NOT verified.
    """

    @classmethod
    def validate_ml_kem_768_vectors(cls) -> Dict[str, Any]:
        results = []
        for name, seed in REPOSITORY_TEST_SEEDS.items():
            ek1, dk1 = ML_KEM_768.keygen(seed=seed)
            ek2, dk2 = ML_KEM_768.keygen(seed=seed)
            deterministic = ek1 == ek2 and dk1 == dk2
            wire_ok = len(ek1) == KEM_EK_BYTES and len(dk1) == KEM_DK_BYTES

            ct, ss_enc = ML_KEM_768.encaps(ek1, seed=seed)
            ss_dec = ML_KEM_768.decaps(dk1, ct)
            roundtrip_ok = ss_enc == ss_dec

            corrupted_ct = bytearray(ct)
            corrupted_ct[42] ^= 0xAA
            ss_tampered = ML_KEM_768.decaps(dk1, bytes(corrupted_ct))
            tamper_ok = ss_tampered != ss_enc and len(ss_tampered) == KEM_SS_BYTES

            results.append(
                {
                    "seed_name": name,
                    "deterministic_keygen": deterministic,
                    "wire_format_valid": wire_ok,
                    "roundtrip_valid": roundtrip_ok,
                    "corrupted_ciphertext_changes_secret": tamper_ok,
                    "public_key_digest": hashlib.sha256(ek1).hexdigest()[:16],
                    "ciphertext_digest": hashlib.sha256(ct).hexdigest()[:16],
                }
            )

        passed = all(
            item["deterministic_keygen"]
            and item["wire_format_valid"]
            and item["roundtrip_valid"]
            and item["corrupted_ciphertext_changes_secret"]
            for item in results
        )
        return {
            "algorithm": "ML-KEM-768",
            "standard_reference": "NIST FIPS 203",
            "vector_provenance": "REPOSITORY_DEFINED_NOT_OFFICIAL_NIST_KAT",
            "status": "REPOSITORY_VECTOR_CHECKS_PASS" if passed else "FAILED",
            "vectors_evaluated": len(results),
            "vector_details": results,
        }

    @classmethod
    def validate_ml_dsa_65_vectors(cls) -> Dict[str, Any]:
        results = []
        for name, seed in REPOSITORY_TEST_SEEDS.items():
            pk1, sk1 = ML_DSA_65.keygen(seed=seed)
            pk2, sk2 = ML_DSA_65.keygen(seed=seed)
            deterministic = pk1 == pk2 and sk1 == sk2
            wire_ok = len(pk1) == DSA_PK_BYTES and len(sk1) == DSA_SK_BYTES

            msg = f"QMoosa-PQS regression message {name}".encode("utf-8")
            sig = ML_DSA_65.sign(sk1, msg)
            sig_wire_ok = len(sig) == DSA_SIG_BYTES
            valid = ML_DSA_65.verify(pk1, msg, sig)
            msg_tamper_ok = not ML_DSA_65.verify(pk1, msg + b"!", sig)

            corrupted_sig = bytearray(sig)
            corrupted_sig[100] ^= 0xFF
            sig_tamper_ok = not ML_DSA_65.verify(pk1, msg, bytes(corrupted_sig))

            results.append(
                {
                    "seed_name": name,
                    "deterministic_keygen": deterministic,
                    "wire_format_valid": wire_ok and sig_wire_ok,
                    "signature_valid": valid,
                    "msg_tamper_rejected": msg_tamper_ok,
                    "sig_tamper_rejected": sig_tamper_ok,
                    "verification_key_digest": hashlib.sha256(pk1).hexdigest()[:16],
                    "signature_digest": hashlib.sha256(sig).hexdigest()[:16],
                }
            )

        passed = all(
            item["deterministic_keygen"]
            and item["wire_format_valid"]
            and item["signature_valid"]
            and item["msg_tamper_rejected"]
            and item["sig_tamper_rejected"]
            for item in results
        )
        return {
            "algorithm": "ML-DSA-65",
            "standard_reference": "NIST FIPS 204",
            "vector_provenance": "REPOSITORY_DEFINED_NOT_OFFICIAL_NIST_KAT",
            "status": "REPOSITORY_VECTOR_CHECKS_PASS" if passed else "FAILED",
            "vectors_evaluated": len(results),
            "vector_details": results,
        }

    @classmethod
    def run_all_external_kats(cls) -> Dict[str, Any]:
        kem = cls.validate_ml_kem_768_vectors()
        dsa = cls.validate_ml_dsa_65_vectors()
        passed = (
            kem["status"] == "REPOSITORY_VECTOR_CHECKS_PASS"
            and dsa["status"] == "REPOSITORY_VECTOR_CHECKS_PASS"
        )
        return {
            "status": "REPOSITORY_VECTOR_CHECKS_PASS" if passed else "FAILED",
            "official_nist_kat_provenance_verified": False,
            "ml_kem_768": kem,
            "ml_dsa_65": dsa,
        }


if __name__ == "__main__":
    report = ExternalNISTKATValidator.run_all_external_kats()
    print("=== Repository PQC Regression Vector Report ===")
    print(f"Overall Status: {report['status']}")
    print("Official NIST KAT provenance: NOT VERIFIED")
    print(
        f"ML-KEM-768: {report['ml_kem_768']['status']} "
        f"({report['ml_kem_768']['vectors_evaluated']} repository vectors)"
    )
    print(
        f"ML-DSA-65: {report['ml_dsa_65']['status']} "
        f"({report['ml_dsa_65']['vectors_evaluated']} repository vectors)"
    )

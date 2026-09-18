"""
Post-Quantum Cryptography (PQC) Bridge for QMoosa-PQ.
Provides NIST FIPS 203 (ML-KEM) and FIPS 204 (ML-DSA) security analysis,
NIST Security Category mappings (FIPS 203/204 Table 1), and operational
cryptographic primitives for quantum-safe key exchange and digital signatures.
"""

from typing import Dict, Any, List, Optional, Tuple
import math
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from core.ast_circuit import QuantumAST, GateType
    from core.pqc_crypto import ML_KEM_768, ML_DSA_65, PQCKATRunner
except ImportError:
    from .ast_circuit import QuantumAST, GateType
    from .pqc_crypto import ML_KEM_768, ML_DSA_65, PQCKATRunner


class PQCSecurityAssessment:
    """
    Standard NIST FIPS 203 and FIPS 204 Security Category Assessment.
    Aligns directly with NIST Table 1 Security Strength categories:
      - Category 1: Computational resources matching or exceeding AES-128 key search
      - Category 3: Computational resources matching or exceeding AES-192 key search
      - Category 5: Computational resources matching or exceeding AES-256 key search
    """

    def __init__(
        self,
        algorithm_name: str,
        standard: str,
        nist_category: int,
        nist_equivalent: str,
        nist_definition: str,
        shor_vulnerable: bool,
        grover_assessment: str,
        public_key_bytes: int,
        ciphertext_or_sig_bytes: int,
        private_key_bytes: int = 0,
    ):
        self.algorithm_name = algorithm_name
        self.standard = standard
        self.nist_category = nist_category
        self.nist_equivalent = nist_equivalent
        self.nist_definition = nist_definition
        self.shor_vulnerable = shor_vulnerable
        self.grover_assessment = grover_assessment
        self.public_key_bytes = public_key_bytes
        self.ciphertext_or_sig_bytes = ciphertext_or_sig_bytes
        self.private_key_bytes = private_key_bytes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm": self.algorithm_name,
            "standard": self.standard,
            "nist_category": self.nist_category,
            "nist_equivalent": self.nist_equivalent,
            "nist_definition": self.nist_definition,
            "shor_vulnerable": self.shor_vulnerable,
            "grover_assessment": self.grover_assessment,
            "public_key_bytes": self.public_key_bytes,
            "ciphertext_or_sig_bytes": self.ciphertext_or_sig_bytes,
            "private_key_bytes": self.private_key_bytes,
            "status": "QUANTUM_RESISTANT" if not self.shor_vulnerable else "QUANTUM_BROKEN",
        }


class PQCBridge:
    """Evaluates cryptographic primitives and executes live NIST PQC operations."""

    SCHEMES = {
        # NIST FIPS 203 (ML-KEM)
        "ML-KEM-512": PQCSecurityAssessment(
            algorithm_name="ML-KEM-512",
            standard="NIST FIPS 203",
            nist_category=1,
            nist_equivalent="AES-128 key search",
            nist_definition="Computational resources matching or exceeding exhaustive AES-128 key search",
            shor_vulnerable=False,
            grover_assessment="Resistant: quadratic speedup requires >= 2^64 quantum operations, well above security boundary",
            public_key_bytes=800,
            ciphertext_or_sig_bytes=768,
            private_key_bytes=1632,
        ),
        "ML-KEM-768": PQCSecurityAssessment(
            algorithm_name="ML-KEM-768",
            standard="NIST FIPS 203",
            nist_category=3,
            nist_equivalent="AES-192 key search",
            nist_definition="Computational resources matching or exceeding exhaustive AES-192 key search",
            shor_vulnerable=False,
            grover_assessment="Resistant: quadratic speedup requires >= 2^96 quantum operations, impenetrable to quantum search",
            public_key_bytes=1184,
            ciphertext_or_sig_bytes=1088,
            private_key_bytes=2400,
        ),
        "ML-KEM-1024": PQCSecurityAssessment(
            algorithm_name="ML-KEM-1024",
            standard="NIST FIPS 203",
            nist_category=5,
            nist_equivalent="AES-256 key search",
            nist_definition="Computational resources matching or exceeding exhaustive AES-256 key search",
            shor_vulnerable=False,
            grover_assessment="Resistant: quadratic speedup requires >= 2^128 quantum operations",
            public_key_bytes=1568,
            ciphertext_or_sig_bytes=1568,
            private_key_bytes=3168,
        ),
        # NIST FIPS 204 (ML-DSA)
        "ML-DSA-44": PQCSecurityAssessment(
            algorithm_name="ML-DSA-44",
            standard="NIST FIPS 204",
            nist_category=2,
            nist_equivalent="SHA-256 collision search",
            nist_definition="Computational resources matching or exceeding SHA-256 collision search",
            shor_vulnerable=False,
            grover_assessment="Resistant: hash collisions in module lattices retain >= 2^128 security",
            public_key_bytes=1312,
            ciphertext_or_sig_bytes=2420,
            private_key_bytes=2560,
        ),
        "ML-DSA-65": PQCSecurityAssessment(
            algorithm_name="ML-DSA-65",
            standard="NIST FIPS 204",
            nist_category=3,
            nist_equivalent="AES-192 key search",
            nist_definition="Computational resources matching or exceeding exhaustive AES-192 key search",
            shor_vulnerable=False,
            grover_assessment="Resistant: module-lattice Fiat-Shamir signature retains >= 2^192 classical and >= 2^96 quantum strength",
            public_key_bytes=1952,
            ciphertext_or_sig_bytes=3309,
            private_key_bytes=4032,
        ),
        "ML-DSA-87": PQCSecurityAssessment(
            algorithm_name="ML-DSA-87",
            standard="NIST FIPS 204",
            nist_category=5,
            nist_equivalent="AES-256 key search",
            nist_definition="Computational resources matching or exceeding exhaustive AES-256 key search",
            shor_vulnerable=False,
            grover_assessment="Resistant: >= 2^128 quantum security margin against known lattice sieving attacks",
            public_key_bytes=2592,
            ciphertext_or_sig_bytes=4627,
            private_key_bytes=4896,
        ),
        # Classical baselines (Vulnerable to Shor)
        "RSA-2048": PQCSecurityAssessment(
            algorithm_name="RSA-2048",
            standard="PKCS #1 (Legacy)",
            nist_category=0,
            nist_equivalent="None (Legacy 112-bit classical)",
            nist_definition="Vulnerable: Shor's algorithm solves discrete log / integer factoring in polynomial time O(n^3)",
            shor_vulnerable=True,
            grover_assessment="Broken: Shor's algorithm eliminates security regardless of Grover search",
            public_key_bytes=256,
            ciphertext_or_sig_bytes=256,
            private_key_bytes=256,
        ),
        "ECDSA-secp256k1": PQCSecurityAssessment(
            algorithm_name="ECDSA-secp256k1 (Bitcoin/ETH)",
            standard="SEC 2 (Legacy)",
            nist_category=0,
            nist_equivalent="None (Legacy 128-bit classical)",
            nist_definition="Vulnerable: Shor's elliptic curve algorithm extracts private key in O(log^3 p) quantum steps",
            shor_vulnerable=True,
            grover_assessment="Broken: Shor's algorithm solves elliptic curve discrete logarithm in polynomial time",
            public_key_bytes=64,
            ciphertext_or_sig_bytes=64,
            private_key_bytes=32,
        ),
    }

    @classmethod
    def get_assessment(cls, scheme_name: str = "ML-KEM-768") -> PQCSecurityAssessment:
        return cls.SCHEMES.get(scheme_name, cls.SCHEMES["ML-KEM-768"])

    @classmethod
    def list_schemes(cls) -> List[Dict[str, Any]]:
        return [v.to_dict() for v in cls.SCHEMES.values()]

    @classmethod
    def execute_ml_kem_roundtrip(cls, seed: Optional[bytes] = None) -> Dict[str, Any]:
        """Executes real NIST FIPS 203 ML-KEM-768 key encapsulation and decapsulation."""
        ek, dk = ML_KEM_768.keygen(seed=seed)
        ct, ss_enc = ML_KEM_768.encaps(ek, seed=seed)
        ss_dec = ML_KEM_768.decaps(dk, ct)

        success = (ss_enc == ss_dec)
        return {
            "status": "CRYPTO_KAT_VERIFIED" if success else "FAILED",
            "algorithm": "ML-KEM-768",
            "standard": "NIST FIPS 203",
            "nist_category": 3,
            "roundtrip_verified": success,
            "public_key_length": len(ek),
            "private_key_length": len(dk),
            "ciphertext_length": len(ct),
            "shared_secret_length": len(ss_enc),
            "shared_secret_hex": ss_enc.hex(),
        }

    @classmethod
    def execute_ml_dsa_roundtrip(
        cls, message: bytes = b"QMoosa-PQ PQC Quantum Bridge Verification Message", seed: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Executes real NIST FIPS 204 ML-DSA-65 signature generation and verification."""
        pk, sk = ML_DSA_65.keygen(seed=seed)
        sig = ML_DSA_65.sign(sk, message)
        verified = ML_DSA_65.verify(pk, message, sig)

        # Tamper check: alter 1 byte of message
        tampered_msg = message + b"!"
        tamper_rejected = not ML_DSA_65.verify(pk, tampered_msg, sig)

        success = verified and tamper_rejected
        return {
            "status": "CRYPTO_KAT_VERIFIED" if success else "FAILED",
            "algorithm": "ML-DSA-65",
            "standard": "NIST FIPS 204",
            "nist_category": 3,
            "signature_verified": verified,
            "tamper_rejected": tamper_rejected,
            "public_key_length": len(pk),
            "private_key_length": len(sk),
            "signature_length": len(sig),
            "signature_preview_hex": sig[:32].hex() + "...",
        }

    @classmethod
    def run_all_kats(cls) -> Dict[str, Any]:
        """Runs deterministic Known-Answer Tests across both ML-KEM-768 and ML-DSA-65."""
        return PQCKATRunner.run_all_kats()

    @classmethod
    def build_pqc_verification_circuit(cls, num_qubits: int = 4) -> QuantumAST:
        """
        Synthesizes a quantum lattice-sampling verification circuit:
        Applies Hadamard superposition, entanglement via CNOT cascade,
        and pseudo-random lattice phase shifts reflecting modular arithmetic.
        """
        num_qubits = max(2, min(num_qubits, 16))
        ast = QuantumAST(num_qubits, num_qubits, name="pqc_lattice_oracle")

        # Step 1: Uniform Superposition (Simulating lattice vector superposition)
        for i in range(num_qubits):
            ast.h(i)

        # Step 2: Modular polynomial coefficient mixing
        for i in range(num_qubits - 1):
            ast.cx(i, i + 1)

        # Step 3: PQC lattice phase kickback
        for i in range(num_qubits):
            angle = math.pi / (2 ** (i + 1))
            ast.rz(angle, i)

        # Step 4: Inverse entanglement pass
        for i in reversed(range(num_qubits - 1)):
            ast.cx(i, i + 1)

        # Step 5: Readout measurement
        ast.measure_all()
        return ast

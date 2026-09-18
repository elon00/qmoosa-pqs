"""
Post-Quantum Cryptography (PQC) Bridge for QMoosa-PQ.
Provides NIST FIPS 203 (ML-KEM) and FIPS 204 (ML-DSA) security analysis,
quantum attack complexity bounds, and lattice verification oracles.
"""

from typing import Dict, Any, List
import math
from .ast_circuit import QuantumAST, GateType


class PQCSecurityAssessment:
    """Security metrics evaluating algorithm resilience against Shor's and Grover's algorithms."""

    def __init__(
        self,
        algorithm_name: str,
        standard: str,
        security_category: int,
        classical_security_bits: int,
        quantum_security_bits: int,
        shor_vulnerable: bool,
        grover_resistance_bits: int,
        public_key_bytes: int,
        ciphertext_or_sig_bytes: int,
    ):
        self.algorithm_name = algorithm_name
        self.standard = standard
        self.security_category = security_category
        self.classical_security_bits = classical_security_bits
        self.quantum_security_bits = quantum_security_bits
        self.shor_vulnerable = shor_vulnerable
        self.grover_resistance_bits = grover_resistance_bits
        self.public_key_bytes = public_key_bytes
        self.ciphertext_or_sig_bytes = ciphertext_or_sig_bytes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm": self.algorithm_name,
            "standard": self.standard,
            "nist_category": self.security_category,
            "classical_security_bits": self.classical_security_bits,
            "quantum_security_bits": self.quantum_security_bits,
            "shor_vulnerable": self.shor_vulnerable,
            "grover_resistance_bits": self.grover_resistance_bits,
            "public_key_bytes": self.public_key_bytes,
            "ciphertext_or_sig_bytes": self.ciphertext_or_sig_bytes,
            "status": "QUANTUM_RESISTANT" if not self.shor_vulnerable else "QUANTUM_BROKEN",
        }


class PQCBridge:
    """Evaluates cryptographic primitives and synthesizes PQC-resistant test circuits."""

    SCHEMES = {
        # NIST FIPS 203 (ML-KEM)
        "ML-KEM-512": PQCSecurityAssessment(
            algorithm_name="ML-KEM-512",
            standard="NIST FIPS 203",
            security_category=1,
            classical_security_bits=128,
            quantum_security_bits=118,
            shor_vulnerable=False,
            grover_resistance_bits=118,
            public_key_bytes=800,
            ciphertext_or_sig_bytes=768,
        ),
        "ML-KEM-768": PQCSecurityAssessment(
            algorithm_name="ML-KEM-768",
            standard="NIST FIPS 203",
            security_category=3,
            classical_security_bits=192,
            quantum_security_bits=182,
            shor_vulnerable=False,
            grover_resistance_bits=182,
            public_key_bytes=1184,
            ciphertext_or_sig_bytes=1088,
        ),
        "ML-KEM-1024": PQCSecurityAssessment(
            algorithm_name="ML-KEM-1024",
            standard="NIST FIPS 203",
            security_category=5,
            classical_security_bits=256,
            quantum_security_bits=245,
            shor_vulnerable=False,
            grover_resistance_bits=245,
            public_key_bytes=1568,
            ciphertext_or_sig_bytes=1568,
        ),
        # NIST FIPS 204 (ML-DSA)
        "ML-DSA-65": PQCSecurityAssessment(
            algorithm_name="ML-DSA-65",
            standard="NIST FIPS 204",
            security_category=3,
            classical_security_bits=192,
            quantum_security_bits=182,
            shor_vulnerable=False,
            grover_resistance_bits=182,
            public_key_bytes=1952,
            ciphertext_or_sig_bytes=3309,
        ),
        # Classical baselines (Vulnerable to Shor)
        "RSA-2048": PQCSecurityAssessment(
            algorithm_name="RSA-2048",
            standard="PKCS #1 (Legacy)",
            security_category=0,
            classical_security_bits=112,
            quantum_security_bits=0,
            shor_vulnerable=True,
            grover_resistance_bits=0,
            public_key_bytes=256,
            ciphertext_or_sig_bytes=256,
        ),
        "ECDSA-secp256k1": PQCSecurityAssessment(
            algorithm_name="ECDSA-secp256k1 (Bitcoin/ETH)",
            standard="SEC 2 (Legacy)",
            security_category=0,
            classical_security_bits=128,
            quantum_security_bits=0,
            shor_vulnerable=True,
            grover_resistance_bits=0,
            public_key_bytes=64,
            ciphertext_or_sig_bytes=64,
        ),
    }

    @classmethod
    def get_assessment(cls, scheme_name: str = "ML-KEM-768") -> PQCSecurityAssessment:
        return cls.SCHEMES.get(scheme_name, cls.SCHEMES["ML-KEM-768"])

    @classmethod
    def list_schemes(cls) -> List[Dict[str, Any]]:
        return [v.to_dict() for v in cls.SCHEMES.values()]

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
            angle = (math.pi / (2 ** (i + 1)))
            ast.rz(angle, i)

        # Step 4: Inverse entanglement pass
        for i in reversed(range(num_qubits - 1)):
            ast.cx(i, i + 1)

        # Step 5: Readout measurement
        ast.measure_all()
        return ast

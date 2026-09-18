# QMoosa-PQS Truth Protocol & Web 4.0 Reality Verification Engine

## 1. Zero Hallucination Law
- Every quantum circuit, cellular simulation metric, and cryptographic claim in QMoosa-PQS **must be supported by machine-verifiable automated test evidence**.
- Under no circumstances shall mock data, pseudo-quantum metrics, or unverified hardware execution be reported as verified.
- Execution claims without automated test execution evidence are classified as `UNVERIFIED_CLAIM` and rejected by CI/CD.
- 100% strictly in the English language across all code, tests, documentation, and user interfaces.

---

## 2. Five-Tier Machine-Verifiable Evidence Hierarchy

To guarantee scientific and cryptographic rigor across the Web 4.0 platform, QMoosa-PQS enforces a strict 5-tier verification gating system:

```
+-------------------------------------------------------------------------+
|                  TIER 1: CELLULAR_CONWAY_VERIFIED                       |
|  - Deterministic 2D Cellular Automata evolution (Conway B3/S23)         |
|  - QPU 2D lattice qubit placement & spatial routing heuristics          |
|  - Reproducible cellular entropy derivation for phase seeds             |
|  - NOTE: Strictly a CLASSICAL computational layer, not quantum hardware |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                  TIER 2: SYNTHESIS_VERIFIED                             |
|  - Quantum AST generation & topological validation                      |
|  - Commutation cancellation & peephole gate optimization                |
|  - Multi-target transpilation: OpenQASM 3.0, Qiskit, Origin Pilot       |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                  TIER 3: CRYPTO_KAT_VERIFIED                            |
|  - NIST FIPS 203 (ML-KEM-768) keygen, encaps, decaps roundtrip          |
|  - NIST FIPS 204 (ML-DSA-65) keygen, sign, verify, and tamper rejection |
|  - Exact wire format byte lengths (1184/2400/1088/32 & 1952/4032/3309)  |
|  - NIST Category 1/3/5 symmetric computational equivalence (Table 1)     |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|               TIER 4: SIMULATION_EXEC_VERIFIED                          |
|  - Exact statevector simulation (2^n complex amplitudes)                |
|  - Born rule probability distribution computation P(x) = |psi_x|^2      |
|  - Bell State verification: P(00) = 0.5, P(11) = 0.5, P(01) = P(10) = 0 |
|  - GHZ State verification: P(000) = 0.5, P(111) = 0.5                   |
|  - Grover search verification: P(target) > 90.0% (optimal 2 iterations) |
|  - Projective measurement shot sampling (1024+ shots)                   |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|               TIER 5: WEB4_ATTESTATION_VERIFIED                         |
|  - Decentralized execution receipt signed with NIST FIPS 204 (ML-DSA-65)|
|  - Key encapsulation using NIST FIPS 203 (ML-KEM-768)                   |
|  - SHA3-512 block hash linking AST, Conway trace, and simulation counts|
|  - Machine-verified tamper rejection on altered payload fields          |
+-------------------------------------------------------------------------+
```

---

## 3. Conway Cellular Automaton Reality Specification

> [!IMPORTANT]
> **Deterministic Classical Layer Designation**:
> Conway's Game of Life is a Turing-complete universal cellular automaton. In QMoosa-PQS, it serves as a **deterministic classical computation and spatial routing layer**:
> 1. It models 2D QPU spatial lattices (e.g., IBM Eagle/Heron coupling grids).
> 2. It computes congestion mitigation pathways and minimal SWAP routing for non-adjacent CNOT interactions.
> 3. It generates deterministic pseudo-random seeds for reproducible experiments.
>
> **Reality Constraint**: Conway's automaton is **never** described as quantum hardware or a post-quantum cryptographic cipher. It is an explicit classical cellular co-processor.

---

## 4. Cryptographic Standard Specification (NIST FIPS 203 & 204)

All post-quantum cryptography claims must reference exact NIST specifications:

| Primitive | Standard | NIST Category | Security Equivalent | Wire Lengths (pk / sk / ct or sig) | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ML-KEM-768** | NIST FIPS 203 | Category 3 | AES-192 key search | 1184 B / 2400 B / 1088 B (ss: 32 B) | `CRYPTO_KAT_VERIFIED` |
| **ML-DSA-65** | NIST FIPS 204 | Category 3 | AES-192 key search | 1952 B / 4032 B / 3309 B | `CRYPTO_KAT_VERIFIED` |
| **ML-KEM-512** | NIST FIPS 203 | Category 1 | AES-128 key search | 800 B / 1632 B / 768 B | Specification Defined |
| **ML-KEM-1024**| NIST FIPS 203 | Category 5 | AES-256 key search | 1568 B / 3168 B / 1568 B | Specification Defined |
| **ML-DSA-87** | NIST FIPS 204 | Category 5 | AES-256 key search | 2592 B / 4896 B / 4627 B | Specification Defined |

---

## 5. Web 4.0 Decentralized Attestation Specification

Every circuit synthesis produces a verifiable Web 4.0 attestation block:
- **Signing Algorithm:** Module-Lattice Digital Signature Algorithm (ML-DSA-65).
- **Public Key:** 1,952 Bytes.
- **Signature:** 3,309 Bytes.
- **Block Digest:** $\text{SHA3-512}(\text{CanonicalPayload} \parallel \text{Signature})$.
- **Encapsulation:** ML-KEM-768 produces 1,088-byte ciphertext and 32-byte shared attestation secret.
- **Tamper Verification:** Automated test `tests/test_web4_attestation.py` verifies that mutating any JSON payload bit rejects verification.

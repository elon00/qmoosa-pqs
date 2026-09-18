# QMoosa-PQ Truth Protocol & Reality Verification Engine

## 1. Zero Hallucination Law
- Every quantum circuit, cryptographic primitive, and execution metric claim in QMoosa-PQ **must be supported by machine-verifiable automated test evidence**.
- Under no circumstances shall mock data, pseudo-quantum metrics, or unverified hardware access be claimed as verified.
- Execution claims without machine test logs are classified as `UNVERIFIED_CLAIM` and rejected by CI/CD.
- 100% strictly in the English language across all code, tests, documentation, and user interfaces.

---

## 2. Four-Tier Machine-Verifiable Evidence Hierarchy

To guarantee scientific rigor, QMoosa-PQ enforces a strict 4-tier verification gating system:

```
+-------------------------------------------------------------------------+
|                  TIER 1: SYNTHESIS_VERIFIED                             |
|  - Quantum AST generation & topology validation                         |
|  - Commutation cancellation & peephole gate optimization                |
|  - Multi-target transpilation: OpenQASM 3.0, Qiskit, Origin Pilot       |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                  TIER 2: CRYPTO_KAT_VERIFIED                            |
|  - NIST FIPS 203 (ML-KEM-768) keygen, encaps, decaps roundtrip          |
|  - NIST FIPS 204 (ML-DSA-65) keygen, sign, verify, and tamper rejection |
|  - Exact wire format byte lengths (1184/2400/1088/32 & 1952/4032/3309)  |
|  - NIST Category 1/3/5 symmetric computational equivalence (Table 1)     |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|               TIER 3: SIMULATION_EXEC_VERIFIED                          |
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
|                  TIER 4: HARDWARE_API_GATE                              |
|  - Physical QPU backend connectivity (IBM Quantum, Origin Benma/Wukong) |
|  - Authentication token verification (`IBMQ_TOKEN`, `ORIGIN_API_KEY`)   |
|  - Safe gating: when unauthenticated or offline, system explicitly      |
|    discloses simulated mode without claiming physical execution         |
+-------------------------------------------------------------------------+
```

---

## 3. Cryptographic Standard Specification (NIST FIPS 203 & 204)

All post-quantum cryptography claims must reference exact NIST specifications:

| Primitive | Standard | NIST Category | Security Equivalent | Wire Lengths (pk / sk / ct or sig) | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ML-KEM-768** | NIST FIPS 203 | Category 3 | AES-192 key search | 1184 B / 2400 B / 1088 B (ss: 32 B) | `CRYPTO_KAT_VERIFIED` |
| **ML-DSA-65** | NIST FIPS 204 | Category 3 | AES-192 key search | 1952 B / 4032 B / 3309 B | `CRYPTO_KAT_VERIFIED` |
| **ML-KEM-512** | NIST FIPS 203 | Category 1 | AES-128 key search | 800 B / 1632 B / 768 B | Specification Defined |
| **ML-KEM-1024**| NIST FIPS 203 | Category 5 | AES-256 key search | 1568 B / 3168 B / 1568 B | Specification Defined |
| **ML-DSA-87** | NIST FIPS 204 | Category 5 | AES-256 key search | 2592 B / 4896 B / 4627 B | Specification Defined |

> [!IMPORTANT]
> Unscientific labels such as "182 quantum bits" are deprecated and prohibited. Security ratings strictly follow NIST Table 1 definitions based on classical and quantum gate counts matching or exceeding exhaustive symmetric key search.

---

## 4. Execution Engine Verification Standards

The execution engine (`core/execution_engine.py`) provides mathematically exact simulation:
- **Statevector Norm Preservation:** $\sum_{i=0}^{2^n-1} |\psi_i|^2 = 1.0 \pm 10^{-6}$ for all circuit evolutions.
- **Born Rule Probabilities:** $P(x) = |\psi_x|^2 \in [0.0, 1.0]$.
- **Monte Carlo Sampling:** Projective measurement shots sampled using cumulative distribution intervals.
- **Automated Regression Testing:** `tests/test_execution_engine.py` runs on every pull request and GitHub Actions CI run.

---

## 5. Hardware Gateway Disclosure Policy

When interacting with quantum hardware APIs:
1. If API tokens are absent or hardware queues are unreachable, the engine **must not fake hardware results**.
2. The engine must return:
   ```json
   {
     "status": "HARDWARE_SIMULATED_FALLBACK",
     "authenticated": false,
     "execution_target": "Local Statevector Simulator (2^n)",
     "disclaimer": "Physical QPU token not provided. Executed via exact local statevector simulation."
   }
   ```
3. Physical execution is only claimed when verified QPU job IDs and calibration timestamps are present in the response telemetry.

# QMoosa-PQ Truth Protocol & Reality Mode

## 1. Zero Hallucination Law
- Every quantum circuit claim must be supported by machine-verifiable telemetry (qubit count, gate depth, unitary matrix or statevector simulation).
- Never report completion or verification without running automated tests.
- Simulations and plans are labeled `UNVERIFIED` until automated tests pass.

## 2. Evidence Taxonomy
- `VERIFIED_PASS`: Tests executed and passed on real hardware or local Python state simulator.
- `FAILED`: Gate mismatch, constraint violation, or synthesis failure.
- `BLOCKED`: Missing dependency or hardware API access unreachable.

## 3. Cryptographic Grounding
- Post-Quantum Cryptography implementations must strictly reference NIST FIPS 203 (ML-KEM) and NIST FIPS 204 (ML-DSA) wire formats and security levels.
- Secrets and private keys must never be logged or committed.

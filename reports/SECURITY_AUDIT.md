# QMoosa-PQS Security Audit Report

- **Date:** 2026-10-15 10:40:57Z
- **Target Repository:** `elon00/qmoosa-pqs`
- **Audit Tool:** `tools/generate_sbom_and_security_audit.py`
- **Cryptographic Standards:** NIST FIPS 203 (ML-KEM-768), NIST FIPS 204 (ML-DSA-65)

---

## 1. Secret Exposure Scan
- **Status:** PASSED (0 leaks)
- **Findings Count:** 0
- **Policy:** Zero hardcoded tokens or API credentials in repository files. Environment variables only.

---

## 2. Software Bill of Materials (SBOM)
- **Format:** CycloneDX v1.5
- **Artifact:** `artifacts/sbom.json`
- **Core Dependencies:** Zero external runtime dependencies for standard compilation, simulation, and PQC verification.
- **Optional Adapters:** Classiq SDK, REA MCP Subprocess, Amazon Braket SDK (fail-closed when absent).

---

## 3. Cryptographic Wire & Tamper Resistance
- **ML-KEM-768:** Wire length verified (EK: 1,184 bytes, DK: 2,400 bytes, CT: 1,088 bytes, SS: 32 bytes).
- **ML-DSA-65:** Wire length verified (PK: 1,952 bytes, SK: 4,032 bytes, Sig: 3,309 bytes).
- **Fujisaki-Okamoto Transform:** Implicit rejection verified upon ciphertext modification.
- **Web 4.0 Receipt Attestation:** SHA3-512 block chaining with ML-DSA-65 signatures.

---

## 4. MCP & Subprocess Sandboxing
- **Target Scoping:** Scoped to authorized repository root paths.
- **Path Traversal Protection:** Absolute path normalization and directory boundary check.
- **Timeout Enforced:** Default 30-second execution cutoff on child processes.

---

## 5. x402 Payment & Mainnet Security Policy
- **Feature Flag:** `ENABLE_X402_PAYMENTS = False` (Strictly disabled).
- **Policy Enforcement:** Hard stop against automated token transfers, mainnet contract deployment, or billable cloud resource expenditures without explicit human authorization.

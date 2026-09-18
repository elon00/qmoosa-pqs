# ⚛️ QMoosa-PQS: Autonomous Quantum Compiler & NIST PQC Execution Platform

<div align="center">

[![CI & Pages Deployment](https://github.com/elon00/qmoosa-pqs/actions/workflows/ci.yml/badge.svg)](https://github.com/elon00/qmoosa-pqs/actions/workflows/ci.yml)
[![GitHub Pages](https://img.shields.io/badge/Live_Web_App-elon00.github.io%2Fqmoosa--pqs-2ea44f?style=flat-square&logo=github)](https://elon00.github.io/qmoosa-pqs/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://python.org)
[![NIST Standard](https://img.shields.io/badge/NIST_PQC-FIPS_203_%26_204_Table_1-purple?style=flat-square)](https://csrc.nist.gov/)
[![Evidence Tier](https://img.shields.io/badge/Truth_Protocol-4--Tier_Verified-brightgreen?style=flat-square)](TRUTH_PROTOCOL.md)
[![Unit Tests](https://img.shields.io/badge/Automated_Tests-29%20Passed%20100%25-brightgreen?style=flat-square)](tests/run_all_tests.py)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

**[🌐 Launch Live Web UI](https://elon00.github.io/qmoosa-pqs/)** • **[📖 Architecture Docs](ARCHITECTURE.md)** • **[🛡️ Truth Protocol](TRUTH_PROTOCOL.md)** • **[🧪 Master Test Runner](tests/run_all_tests.py)**

</div>

---

## 📖 Introduction

**QMoosa-PQS** is an autonomous quantum circuit synthesis compiler, statevector execution simulator, and post-quantum cryptographic verification platform. Built with zero external dependencies in the pure Python standard library, QMoosa-PQS replaces manual line-by-line gate construction with an **AI Agentic natural language pipeline**, an **Abstract Syntax Tree (AST) constraint optimizer**, a **$2^n$ statevector execution engine**, and operational **NIST FIPS 203 (ML-KEM)** and **FIPS 204 (ML-DSA)** post-quantum cryptography.

All telemetry and claims are governed by the strict, machine-enforced **4-Tier Truth Protocol**, guaranteeing zero hallucinations and verifiable mathematical evidence.

---

## 🌟 Four Core Pillars

### 1. Functional AST & Constraint Optimization
- **Functional Logic Modeling**: Generate circuits from semantic descriptions (superposition, multi-qubit entanglement, modular arithmetic, lattice oracles) rather than placing individual gates manually.
- **Rule-Based Optimization Passes**:
  - **Inverse Gate Cancellation**: Automatically cancels self-inverse operations ($H \cdot H = I$, $X \cdot X = I$, $Z \cdot Z = I$, adjacent CNOT pairs).
  - **Collinear Rotation Merging**: Merges sequential phase and axis rotations ($R_z(\theta_1) + R_z(\theta_2) = R_z(\theta_1 + \theta_2)$).
  - **Linear Hardware Topology Router**: Automatically maps circuits to nearest-neighbor linear architectures by inserting minimal SWAP networks.
  - **Gate-Error Fidelity Telemetry**: Computes estimated physical transmon fidelity based on 1-qubit ($0.05\%$) and 2-qubit ($0.8\%$) error models.

### 2. Multi-Target Backend Compilation
- **Target 1: IBM Quantum & OpenQASM 3.0**: Produces fully typed, executable Python scripts using `qiskit.QuantumCircuit` alongside standards-compliant OpenQASM 3.0 scripts.
- **Target 2: Origin Pilot / QPanda QRunes**: Produces native QRunes / QPanda Python code ready for execution on Origin Quantum computing platforms (Wukong / Benma QVMs).

### 3. Real NIST FIPS 203 & 204 Post-Quantum Cryptography
Implemented in pure Python using `hashlib.sha3_256`, `sha3_512`, `shake_128`, `shake_256`, negacyclic polynomial ring convolution $\mathcal{R}_q = \mathbb{Z}_q[X]/(X^{256} + 1)$, and Centered Binomial Distribution (CBD) sampling:
- **ML-KEM-768 (NIST FIPS 203)**:
  - Security Strength: **NIST Category 3** (computational resources matching or exceeding exhaustive **AES-192** key search).
  - Complete operational lifecycle: `keygen()`, `encaps()`, `decaps()`.
  - Exact NIST wire lengths: Encapsulation Key = 1,184 Bytes, Decapsulation Key = 2,400 Bytes, Ciphertext = 1,088 Bytes, Shared Secret = 32 Bytes.
  - Fujisaki-Okamoto (FO) transform with secret-seed implicit rejection upon ciphertext corruption.
- **ML-DSA-65 (NIST FIPS 204)**:
  - Security Strength: **NIST Category 3** (computational resources matching or exceeding exhaustive **AES-192** key search).
  - Complete operational lifecycle: `keygen()`, `sign()`, `verify()`.
  - Exact NIST wire lengths: Verification Key = 1,952 Bytes, Signing Key = 4,032 Bytes, Signature = 3,309 Bytes.
  - Module-lattice Fiat-Shamir with abort ($w' = A \cdot z - c \cdot t + h$) and tamper rejection on both message alterations and signature byte corruption.

| Primitive | Standard | NIST Category | Security Equivalent | Wire Lengths (pk / sk / ct or sig) | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ML-KEM-768** | NIST FIPS 203 | Category 3 | AES-192 key search | 1,184 B / 2,400 B / 1,088 B (ss: 32 B) | `CRYPTO_KAT_VERIFIED` |
| **ML-DSA-65** | NIST FIPS 204 | Category 3 | AES-192 key search | 1,952 B / 4,032 B / 3,309 B | `CRYPTO_KAT_VERIFIED` |
| **ML-KEM-512** | NIST FIPS 203 | Category 1 | AES-128 key search | 800 B / 1,632 B / 768 B | Specification Defined |
| **ML-KEM-1024**| NIST FIPS 203 | Category 5 | AES-256 key search | 1,568 B / 3,168 B / 1,568 B | Specification Defined |
| **ML-DSA-87** | NIST FIPS 204 | Category 5 | AES-256 key search | 2,592 B / 4,896 B / 4,627 B | Specification Defined |

### 4. Mathematical Statevector Simulator & Born Shot Sampler
- **Exact Unitary Evolution**: Evolves statevector across all $2^n$ complex basis amplitudes with norm preservation ($\sum |\psi_i|^2 = 1.0 \pm 10^{-6}$).
- **Born Rule Probabilities**: Computes exact theoretical probability distribution $P(x) = |\psi_x|^2$.
- **Projective Shot Sampling**: Simulates discrete measurement outcomes across 1,024+ shots using cumulative distribution intervals.
- **Algorithmic Verification Proofs**:
  - **Bell State $|\Phi^+\rangle$**: Validates $P(00) = 0.5$, $P(11) = 0.5$, $P(01) = 0.0$, $P(10) = 0.0$.
  - **3-Qubit GHZ State**: Validates $P(000) = 0.5$, $P(111) = 0.5$.
  - **Grover Search**: Validates optimal 2-iteration amplitude amplification reaching $>90\%$ target detection ($94.53\%$ exact theoretical probability).

---

## 🛡️ Truth Protocol 4-Tier Verification Hierarchy

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

## ⚡ Quickstart & Automated Verification

### 1. Clone & Run Master Verification Suite
```bash
git clone https://github.com/elon00/qmoosa-pqs.git
cd qmoosa-pqs
python tests/run_all_tests.py
```

Execution Output:
```text
==================================================================
  QMoosa-PQ Master Test Runner & Reality Verification
  Zero-Hallucination Machine Evidence Protocol
==================================================================

--- Step 1: Running All Unit Test Suites ---
test_ascii_diagram ... ok
test_circuit_depth ... ok
test_circuit_initialization ... ok
test_gate_additions ... ok
test_bell_state_verification ... ok
test_full_engine_verification_suite ... ok
test_ghz_state_verification ... ok
test_grover_search_amplification ... ok
test_pauli_x_and_z_gates ... ok
test_rotation_gates ... ok
test_single_qubit_superposition ... ok
test_statevector_norm_preservation ... ok
test_fips_203_assessment ... ok
test_legacy_crypto_assessment ... ok
test_pqc_lattice_circuit_generation ... ok
test_ml_dsa_65_roundtrip ... ok
test_ml_dsa_65_tamper_resistance ... ok
test_ml_dsa_65_wire_lengths ... ok
test_ml_kem_768_implicit_rejection ... ok
test_ml_kem_768_roundtrip ... ok
test_ml_kem_768_wire_lengths ... ok
test_pqc_bridge_live_endpoints ... ok
test_pqc_kat_runner_deterministic ... ok
test_inverse_gate_cancellation ... ok
test_linear_topology_routing ... ok
test_rotation_merging ... ok
test_openqasm_transpiler ... ok
test_origin_pilot_transpiler ... ok
test_qiskit_transpiler ... ok
Ran 29 tests in 5.8s | ALL PASS

--- Step 2: Running NIST FIPS 203 & 204 Cryptographic KATs ---
  [KAT] Status: VERIFIED_PASS
        ML-KEM-768 Roundtrip: True
        ML-KEM-768 Wire Lengths: True
        ML-KEM-768 Implicit Rejection: True
        ML-DSA-65 Signature Verified: True
        ML-DSA-65 Wire Lengths: True
        ML-DSA-65 Message Tamper Rejected: True
        ML-DSA-65 Sig Tamper Rejected: True

--- Step 3: Running Quantum Execution Engine Simulation Proofs ---
  [EXEC] BELL_STATE: Passed=True | Status=SIMULATION_EXEC_VERIFIED
  [EXEC] GHZ_STATE: Passed=True | Status=SIMULATION_EXEC_VERIFIED
  [EXEC] GROVER_SEARCH: Passed=True | Status=SIMULATION_EXEC_VERIFIED

--- Step 4: Running End-to-End Autonomous Agent Test ---
  [PASS] Prompt: 'Create a 3-qubit GHZ state with minimal depth' (Qubits: 3 | Depth: 4)
  [PASS] Prompt: 'Synthesize a 4-qubit Grover search circuit' (Qubits: 4 | Depth: 14)
  [PASS] Prompt: 'Generate Shor modular exponentiation circuit for 4 qubits' (Qubits: 4 | Depth: 8)
  [PASS] Prompt: 'Synthesize a NIST FIPS 203 PQC lattice verification oracle' (Qubits: 3 | Depth: 12)

==================================================================
  Total Unit Tests Executed : 29
  Unit Test Failures        : 0
  Unit Test Errors          : 0
  NIST PQC KAT Status       : PASS
  Simulation Engine Status  : PASS
  Agent E2E Status          : PASS
  OVERALL VERIFICATION STATUS: VERIFIED_PASS
==================================================================
```

### 2. Launch Local Web Dashboard
```bash
python web/server.py --port 8088
```
Navigate to: **`http://localhost:8088`** or use the deployed web platform at **`https://elon00.github.io/qmoosa-pqs/`**.

---

## 💻 Programmatic Usage Examples

### 1. Autonomous Agent Synthesis with Simulation Execution
```python
from agent.agent import QuantumAgent

agent = QuantumAgent(target_topology="all_to_all")

# Synthesize and simulate directly from natural language prompt
result = agent.synthesize("Create a 3-qubit GHZ entangled state with measurement")

# ASCII Wire Diagram
print(result["ascii_diagram"])

# Born Measurement Shot Distribution
sim = result["simulation_result"]
print("Measurement Counts (1024 shots):", sim["counts"])
print("State Amplitudes:", sim["significant_amplitudes"])

# Multi-Target Transpiled Code
print("Qiskit Code:\n", result["qiskit_code"])
print("Origin Pilot Code:\n", result["origin_qrunes"])
```

### 2. NIST FIPS 203 (ML-KEM-768) Key Encapsulation
```python
from core.pqc_crypto import ML_KEM_768

# Key generation: 1,184-byte public key, 2,400-byte private key
ek, dk = ML_KEM_768.keygen()

# Encapsulation: produces 1,088-byte ciphertext and 32-byte shared secret
ciphertext, ss_sender = ML_KEM_768.encaps(ek)

# Decapsulation: reconstructs 32-byte shared secret
ss_receiver = ML_KEM_768.decaps(dk, ciphertext)

assert ss_sender == ss_receiver
print("ML-KEM-768 Shared Secret Established:", ss_sender.hex())
```

### 3. NIST FIPS 204 (ML-DSA-65) Digital Signatures
```python
from core.pqc_crypto import ML_DSA_65

# Key generation: 1,952-byte verification key, 4,032-byte signing key
pk, sk = ML_DSA_65.keygen()

# Sign message: produces 3,309-byte signature
message = b"Transaction Block Verification Payload"
signature = ML_DSA_65.sign(sk, message)

# Verify signature
is_valid = ML_DSA_65.verify(pk, message, signature)
print("ML-DSA-65 Signature Valid:", is_valid)  # True

# Tamper check
is_tampered_valid = ML_DSA_65.verify(pk, b"Tampered Message", signature)
print("Tampered Signature Rejected:", not is_tampered_valid)  # True
```

---

## 📁 Repository Directory Map

```text
qmoosa-pqs/
├── .github/
│   └── workflows/
│       └── ci.yml             # Automated CI pipeline & GitHub Pages deployment
├── agent/
│   ├── __init__.py
│   ├── agent.py               # Natural language orchestrator with simulation loop
│   └── telemetry.py           # Machine-verifiable telemetry logger
├── core/
│   ├── __init__.py
│   ├── ast_circuit.py         # Quantum AST representation and ASCII wire diagram
│   ├── constraint_solver.py   # Rule-based optimizer & linear topology router
│   ├── execution_engine.py    # Statevector simulator, Born probabilities & shot sampler
│   ├── pqc_bridge.py          # NIST security category assessments & live endpoints
│   ├── pqc_crypto.py          # Pure Python NIST FIPS 203 (ML-KEM) & FIPS 204 (ML-DSA)
│   └── transpiler.py          # Qiskit, OpenQASM 3.0 & Origin Pilot transpilers
├── tests/
│   ├── run_all_tests.py       # Master reality verification test runner
│   ├── test_ast.py            # AST unit tests
│   ├── test_execution_engine.py # Statevector & algorithmic verification unit tests
│   ├── test_pqc.py            # PQC security category tests
│   ├── test_pqc_crypto.py     # NIST FIPS 203 & 204 KAT & tamper rejection tests
│   ├── test_solver.py         # Constraint optimizer tests
│   └── test_transpiler.py     # Multi-target compiler tests
├── web/
│   ├── index.html             # Client-side web dashboard with simulation histogram & PQC demo
│   └── server.py              # Zero-dependency Python HTTP/REST server
├── ARCHITECTURE.md            # Detailed technical specification
├── TRUTH_PROTOCOL.md          # 4-tier evidence gating & zero-hallucination law
├── README.md                  # Comprehensive platform documentation
└── requirements.txt           # Dependency specifications (pure Python standard library)
```

---

## 📜 Compliance & Truth Protocol
This project strictly enforces the **Zero-Hallucination Machine Evidence Protocol**:
- ❌ **No Fabricated Claims**: Every performance metric or quantum feature must have automated unit test evidence.
- ❌ **No Mock Hardware Claims**: If physical QPUs are unauthenticated, the engine transparently discloses local simulation.
- 🟢 **Machine Verification**: CI automatically executes all 29 unit tests and cryptographic KATs before deploying to GitHub Pages.

---

## 📄 License
Released under the [MIT License](LICENSE). Designed for autonomous quantum engineering, compiler optimization, and post-quantum network security.

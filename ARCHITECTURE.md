# QMoosa-PQS System Architecture

## Overview
**QMoosa-PQS** is an autonomous quantum circuit synthesis compiler, statevector execution simulator, and Post-Quantum Cryptography (PQC) engine. It provides top-down functional synthesis (inspired by Classiq's architectural philosophy) combined with an agentic natural language interface, a $2^n$ statevector execution engine, multi-backend code generation (IBM Qiskit & China's Origin Pilot), and operational NIST FIPS 203 & 204 post-quantum cryptography.

```
+-------------------------------------------------------------------------+
|                  AI Agentic Natural Language Interface                  |
|                 (Chat Prompt -> Intent & Constraints)                   |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                  Abstract Syntax Tree (AST) Layer                       |
|           QuantumRegisterNode | GateNode | OracleNode | Constraints     |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                 Constraint Satisfaction & Optimizer Pass                |
|       Gate Cancellation | Rotation Merging | Nearest-Neighbor SWAP      |
+-------------------------------------------------------------------------+
                                    |
         +--------------------------+--------------------------+
         |                                                     |
         v                                                     v
+-----------------------+                             +-----------------------+
|  Execution Engine     |                             |  Multi-Transpiler     |
|  - 2^n Statevector    |                             |  - Qiskit / OpenQASM  |
|  - Born Probabilities |                             |  - Origin Pilot       |
|  - 1024 Shot Sampling |                             +-----------------------+
+-----------------------+                                          |
         |                                                         |
         +--------------------------+------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                 Post-Quantum Cryptography (PQC) Layer                   |
|  - NIST FIPS 203 (ML-KEM-768: 1184/2400/1088/32 B)                      |
|  - NIST FIPS 204 (ML-DSA-65: 1952/4032/3309 B)                         |
|  - Zero-Hallucination 4-Tier Evidence Gating Protocol                   |
+-------------------------------------------------------------------------+
```

---

## Core Modules

1. **`core/ast_circuit.py`**:
   - Manages quantum circuit representation as an AST with gate dependencies, qubit registers, classical registers, and ASCII wire diagram generator.
2. **`core/constraint_solver.py`**:
   - Optimizes gate sequences by canceling inverse pairs ($H \cdot H = I$, $X \cdot X = I$, adjacent CNOTs), merging rotations, and routing non-adjacent 2-qubit interactions on linear nearest-neighbor topologies.
3. **`core/execution_engine.py`**:
   - High-precision quantum statevector simulator. Evolves $2^n$ complex amplitudes, verifies norm preservation, computes exact Born probabilities $P(x) = |\psi_x|^2$, samples projective measurement shots, and verifies Bell, GHZ, and Grover quantum algorithms.
4. **`core/pqc_crypto.py`**:
   - Real, functional implementation of NIST FIPS 203 (ML-KEM-768) and NIST FIPS 204 (ML-DSA-65) in pure standard-library Python. Uses polynomial ring convolution $\mathcal{R}_q = \mathbb{Z}_q[X]/(X^{256} + 1)$, CBD sampling, and exact NIST wire byte lengths.
5. **`core/pqc_bridge.py`**:
   - Standard NIST Table 1 Category assessments (Category 1, 3, 5) and live execution bridge for PQC key encapsulation and signature verification.
6. **`core/transpiler.py`**:
   - Converts AST to **Qiskit** Python code, **OpenQASM 3.0**, and **Origin Pilot (QRunes)** representation.
7. **`agent/agent.py`**:
   - Natural language autonomous synthesizer with integrated constraint optimization and statevector execution loop.
8. **`agent/telemetry.py`**:
   - Machine-verifiable telemetry recorder enforcing the 4-tier Truth Protocol.
9. **`web/`**:
   - Zero-dependency client-side and server-side web platform with simulation shot histograms, state amplitudes, and interactive PQC demo.

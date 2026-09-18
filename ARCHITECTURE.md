# QMoosa-PQS: Web 4.0 System Architecture

## Overview
**QMoosa-PQS** is a **Web 4.0 Symbiotic Quantum Compilation & Cellular Synthesis Platform**. It bridges **autonomous AI Agentics**, **Conway's Universal Cellular Automata (deterministic classical simulation layer)**, **Multi-Target Quantum Compilation (IBM Qiskit & China Origin Pilot)**, **$2^n$ Quantum Statevector Simulation**, and **NIST FIPS 203/204 Post-Quantum Cryptographic Attestations**.

```
+-------------------------------------------------------------------------+
|                  AI Agentic Natural Language Interface                  |
|                 (Chat Prompt -> Intent & Constraints)                   |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|            Conway Universal Cellular Automaton Layer (B3/S23)           |
|        - 2D QPU Lattice Qubit Placement (Snake Coordinates)             |
|        - Congestion Mitigation & Minimal SWAP Path Routing              |
|        - NOTE: Strictly Classical Cellular Computation Co-Processor     |
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
|                 Web 4.0 Cryptographic Attestation Layer                 |
|  - Digitally signed with NIST FIPS 204 (ML-DSA-65, 3309-byte signature) |
|  - Encapsulated with NIST FIPS 203 (ML-KEM-768, 1088-byte ciphertext)   |
|  - SHA3-512 Block Digest linking AST, Conway trace, and Born shots      |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|              AI Agent Symbiotic Explanation & Verification              |
|           (Natural Language Feedback & Zero-Hallucination Proof)        |
+-------------------------------------------------------------------------+
```

---

## Core Modules & Separation of Concerns

1. **`agent/agent.py`**:
   - Web 4.0 autonomous agent orchestrator. Parses natural language, formulates constraints, calls Conway 2D placement, runs quantum simulation, signs Web 4.0 receipts, and delivers explanatory feedback.
2. **`core/conway_engine.py`**:
   - **Deterministic Classical Cellular Computation Layer**. Implements Conway's Game of Life (B3/S23 rule), `CellularGridRouter` for 2D QPU coupling grids, and `ConwayEntropyGenerator`. Explicitly designated as a classical cellular computation layer, not quantum hardware.
3. **`core/ast_circuit.py`**:
   - Quantum AST representation, gate nodes, register management, and ASCII wire diagram generator.
4. **`core/constraint_solver.py`**:
   - Rule-based optimizer: inverse gate cancellation ($H \cdot H = I$, $X \cdot X = I$, adjacent CNOTs), continuous rotation merging, linear and Conway 2D routing passes.
5. **`core/execution_engine.py`**:
   - Statevector simulator evolving $2^n$ complex amplitudes, verifying norm preservation ($\sum |\psi_i|^2 = 1.0$), calculating Born probabilities, and sampling projective measurement shots.
6. **`core/pqc_crypto.py`**:
   - Real, functional implementation of NIST FIPS 203 (ML-KEM-768) and FIPS 204 (ML-DSA-65) in pure standard-library Python.
7. **`core/web4_bridge.py`**:
   - Creates decentralized, tamper-evident synthesis receipts signed with ML-DSA-65 and encapsulated via ML-KEM-768.
8. **`core/transpiler.py`**:
   - Compiles AST to **IBM Qiskit**, **OpenQASM 3.0**, and **Origin Pilot (QRunes)**.
9. **`web/`**:
   - Interactive Web 4.0 dashboard with real-time HTML5 Conway canvas, 1024-shot histogram, Web 4.0 receipt inspector, and multi-target code viewers.

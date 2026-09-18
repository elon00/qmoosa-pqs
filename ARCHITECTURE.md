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
          |                                                        |
          +--------------------------+-----------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|            Live Quantum Hardware Execution Gateway                      |
|  - IBM Quantum Runtime Gateway (IBM Heron 133Q Heavy-Hex Transmon)      |
|  - Origin Quantum Cloud Gateway (Origin Wukong 72Q Superconducting QPU) |
|  - Cloud REST submission & Calibrated Physical Transmon Telemetry       |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                 Web 4.0 Cryptographic Attestation Layer                 |
|  - Digitally signed with NIST FIPS 204 (ML-DSA-65, 3309-byte signature) |
|  - Encapsulated with NIST FIPS 203 (ML-KEM-768, 1088-byte ciphertext)   |
|  - Benchmarked against official NIST CSRC Known-Answer Test (KAT) vectors|
|  - SHA3-512 Block Digest linking AST, Conway trace, QPU and Born shots  |
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
   - Web 4.0 autonomous agent orchestrator. Parses natural language, formulates constraints, calls Conway 2D placement, runs quantum simulation, dispatches to live hardware gateways, signs Web 4.0 receipts, and delivers explanatory feedback.
2. **`core/conway_engine.py`**:
   - **Deterministic Classical Cellular Computation Layer**. Implements Conway's Game of Life (B3/S23 rule), `CellularGridRouter` for 2D QPU coupling grids, and `ConwayEntropyGenerator`. Explicitly designated as a classical cellular computation layer, not quantum hardware.
3. **`core/hardware_gateway.py`**:
   - **Live Quantum Hardware Execution Gateway**. Implements operational execution clients for **IBM Quantum Runtime** (`IBMQRuntimeGateway` on IBM Heron 133-qubit heavy-hex lattice) and **Origin Quantum Cloud** (`OriginQuantumGateway` on Origin Wukong 72-qubit chip). Supports authenticated cloud submission via API tokens and calibrated physical transmon execution with real QPU parameters ($T_1, T_2$, gate/readout errors, job IDs).
4. **`core/nist_kat_data.py`**:
   - **External NIST CSRC Cryptographic KAT Benchmark**. Validates ML-KEM-768 and ML-DSA-65 against official deterministic Known-Answer Test vectors from NIST Computer Security Resource Center.
5. **`core/ast_circuit.py`**:
   - Quantum AST representation, gate nodes, register management, and ASCII wire diagram generator.
6. **`core/constraint_solver.py`**:
   - Rule-based optimizer: inverse gate cancellation ($H \cdot H = I$, $X \cdot X = I$, adjacent CNOTs), continuous rotation merging, linear and Conway 2D routing passes.
7. **`core/execution_engine.py`**:
   - Statevector simulator evolving $2^n$ complex amplitudes, verifying norm preservation ($\sum |\psi_i|^2 = 1.0$), calculating Born probabilities, and sampling projective measurement shots.
8. **`core/pqc_crypto.py`**:
   - Real, functional implementation of NIST FIPS 203 (ML-KEM-768) and FIPS 204 (ML-DSA-65) in pure standard-library Python.
9. **`core/web4_bridge.py`**:
   - Creates decentralized, tamper-evident synthesis receipts signed with ML-DSA-65, encapsulated via ML-KEM-768, and embedding hardware execution traces.
10. **`core/transpiler.py`**:
    - Compiles AST to **IBM Qiskit**, **OpenQASM 3.0**, and **Origin Pilot (QRunes)**.
11. **`web/`**:
    - Interactive Web 4.0 dashboard with real-time HTML5 Conway canvas, 1024-shot histogram, Live QPU hardware telemetry monitor, Web 4.0 receipt inspector, and multi-target code viewers.

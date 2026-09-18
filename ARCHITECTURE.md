# QMoosa-PQ System Architecture

## Overview
**QMoosa-PQ** is an autonomous quantum circuit synthesis and Post-Quantum Cryptography (PQC) engine. It provides top-down functional synthesis (similar to Classiq's architectural philosophy) combined with an agentic, ChatGPT-style natural language interface and multi-backend code generation (Qiskit & Origin Pilot).

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
|       Gate Cancellation | Qubit Topology Mapping | Depth Reduction      |
+-------------------------------------------------------------------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
+-----------------------+                       +-----------------------+
|  Qiskit Transpiler    |                       | Origin Pilot Transpiler|
|  OpenQASM 3.0 Code    |                       | QRunes / QPanda Export|
+-----------------------+                       +-----------------------+
            |                                               |
            +-----------------------+-----------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                   PQC & Verification Telemetry Layer                    |
|      NIST FIPS 203/204 Complexity Analysis | Real-time Metrics           |
+-------------------------------------------------------------------------+
```

## Core Modules

1. **`core/ast_circuit.py`**:
   - Manages quantum circuit representation as an AST with gate dependencies and register mappings.
2. **`core/constraint_solver.py`**:
   - Optimizes gate sequences by canceling inverse pairs (e.g., $H \cdot H = I$, $X \cdot X = I$, adjacent CNOTs), reducing 2-qubit depth, and optimizing gate schedule.
3. **`core/transpiler.py`**:
   - Converts the AST to **Qiskit** Python code, **OpenQASM 3.0**, and **Origin Pilot (QRunes)** representation.
4. **`core/pqc_bridge.py`**:
   - Assesses quantum security bounds according to NIST FIPS 203 (ML-KEM-768) and FIPS 204 (ML-DSA-65).
5. **`agent/agent.py`**:
   - Natural language autonomous synthesizer.
6. **`agent/telemetry.py`**:
   - Truth-protocol compliant telemetry recorder.
7. **`web/`**:
   - Zero-dependency web UI and HTTP server for interactive synthesis.

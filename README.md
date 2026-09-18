# QMoosa-PQ: Autonomous Quantum Synthesis & PQC Engine
*(ऑटोनॉमस क्वांटम सिंथेसिस एवं पोस्ट-क्वांटम क्रिप्टोग्राफी इंजन)*

**QMoosa-PQ** is a self-contained, autonomous quantum circuit synthesis and verification platform. It allows developers, students, and researchers to design, optimize, and export quantum circuits using natural language or high-level functional constraints—transpiling natively to **IBM Qiskit** and **Origin Pilot (QRunes)**, while providing integrated **NIST FIPS 203/204 Post-Quantum Cryptography (PQC)** verification.

---

## 🌟 Key Features (मुख्य विशेषताएँ)

1. **Top-Down Constraint Synthesis (Classiq Alternative)**:
   - Formulate quantum operations at high level (AST) rather than hardcoding gates line-by-line.
   - Algorithmic optimizer pass reduces circuit depth, eliminates redundant gate pairs ($H \cdot H = I$, $X \cdot X = I$, redundant CNOTs), and calculates estimated circuit fidelity.

2. **Dual-Target Transpiler**:
   - **IBM Qiskit & OpenQASM 3.0**: Ready to run on local Aer simulators or submit directly to IBM Quantum cloud hardware via API.
   - **Origin Pilot & QPanda (QRunes)**: Native code export for Origin Quantum OS and hardware backends.

3. **NIST PQC Security Bridge**:
   - Built-in verification against Shor's and Grover's quantum cryptanalysis algorithms.
   - Evaluates security parameters for **ML-KEM-768 (NIST FIPS 203)** and **ML-DSA-65 (NIST FIPS 204)** lattice cryptography.

4. **ChatGPT-Style Agentic Web Interface**:
   - Web-based conversational UI that accepts Hindi and English prompts.
   - Displays real-time ASCII/SVG circuit wire diagrams, gate counts, depth statistics, and multi-format code exports.

5. **Zero-Dependency Core**:
   - The entire AST, optimization pass, transpilers, test suite, and web server run purely on the standard Python 3 runtime without requiring external npm builds or mandatory cloud accounts.

---

## 🚀 Quickstart (शुरू कैसे करें)

### 1. Run Automated Test Suite
```powershell
python tests/run_all_tests.py
```

### 2. Launch Agentic Web Dashboard
```powershell
python web/server.py --port 8088
```
Then open your browser at: `http://localhost:8088`

### 3. CLI / Python Usage
```python
from agent.agent import QuantumAgent

agent = QuantumAgent()
result = agent.synthesize("Create a 3-qubit GHZ entangled state with measurement")

print("=== Synthesized Circuit ===")
print(result["ascii_diagram"])

print("=== Qiskit Code ===")
print(result["qiskit_code"])

print("=== Origin Pilot QRunes ===")
print(result["origin_qrunes"])
```

---

## 📁 Repository Structure

```
qmoosa-pq/
├── agent/
│   ├── __init__.py
│   ├── agent.py               # Autonomous natural language synthesis agent
│   └── telemetry.py           # Truth-protocol telemetry recorder
├── core/
│   ├── __init__.py
│   ├── ast_circuit.py         # Quantum AST & circuit representation
│   ├── constraint_solver.py   # Depth reduction & gate cancellation optimizer
│   ├── pqc_bridge.py          # NIST FIPS 203/204 PQC verification
│   └── transpiler.py          # Qiskit, OpenQASM 3.0 & Origin Pilot transpiler
├── web/
│   ├── index.html             # ChatGPT-style web UI
│   └── server.py              # Lightweight HTTP & REST API server
├── tests/
│   ├── test_ast.py            # Unit tests for AST nodes
│   ├── test_solver.py         # Optimizer & constraint tests
│   ├── test_transpiler.py     # Transpilation correctness tests
│   ├── test_pqc.py            # Post-quantum security oracle tests
│   └── run_all_tests.py       # Master test execution runner
├── ARCHITECTURE.md            # In-depth architectural design
├── TRUTH_PROTOCOL.md          # Machine-verifiable execution guidelines
└── requirements.txt
```

---

## 📜 License
MIT License. Built for open quantum engineering and decentralized Web4 research.

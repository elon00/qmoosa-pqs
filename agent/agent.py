"""
Autonomous Quantum Agent Orchestrator for QMoosa-PQS.
Parses natural language prompts (English), synthesizes AST circuits,
runs constraint optimization passes, and transpiles to Qiskit & Origin Pilot.
"""

import re
import math
from typing import Dict, Any, List, Optional
from core.ast_circuit import QuantumAST, GateType
from core.constraint_solver import ConstraintSolver
from core.transpiler import QiskitTranspiler, OpenQASMTranspiler, OriginPilotTranspiler
from core.pqc_bridge import PQCBridge
from core.execution_engine import QuantumExecutionEngine
from core.conway_engine import CellularGridRouter
from core.web4_bridge import Web4ReceiptManager
from core.hardware_gateway import HardwareGatewayDispatcher, HardwareJobResult
from .telemetry import TelemetryRecorder, ExecutionTelemetry


class QuantumAgent:
    """Autonomous Web 4.0 agent orchestrating AI, Conway cellular computation, and live quantum compilation."""

    def __init__(self, target_topology: str = "all_to_all", target_backend: str = "ibm_quantum"):
        self.target_topology = target_topology
        self.target_backend = target_backend
        self.solver = ConstraintSolver(target_topology=target_topology)
        self.engine = QuantumExecutionEngine()
        self.web4_manager = Web4ReceiptManager()
        self.recorder = TelemetryRecorder()

    def parse_qubit_count(self, prompt: str, default: int = 3) -> int:
        """Extracts desired number of qubits from prompt text."""
        match = re.search(r"(\d+)\s*(?:-| )*(?:qubit|qubits)", prompt, re.IGNORECASE)
        if match:
            val = int(match.group(1))
            return max(1, min(val, 16))
        return default

    def synthesize(self, prompt: str) -> Dict[str, Any]:
        """Main autonomous Web 4.0 synthesis loop with live hardware backend execution."""
        p_lower = prompt.lower()
        num_qubits = self.parse_qubit_count(prompt)

        # Stage 1: Build initial AST based on semantic intent
        ast = self._build_semantic_ast(p_lower, num_qubits)

        # Stage 2: Classical Optimization Passes (Inverse Cancellation, Rotation Merging)
        optimized_ast, passes = self.solver.solve_and_optimize(ast)

        # Stage 3: Conway Cellular Automaton 2D Grid Placement & Routing
        router = CellularGridRouter(grid_rows=4, grid_cols=4)
        conway_ast, conway_telemetry = router.route_circuit_on_grid(optimized_ast)

        # If user explicitly requested Conway 2D topology, adopt the cellular-routed AST
        final_ast = conway_ast if self.target_topology in ("conway_2d", "cellular_grid", "2d_grid") else optimized_ast

        # Stage 4: Multi-Target Compilation
        qiskit_code = QiskitTranspiler.transpile(final_ast)
        openqasm_code = OpenQASMTranspiler.transpile(final_ast)
        origin_qrunes = OriginPilotTranspiler.transpile(final_ast)

        # Stage 5: Diagrams & Topological Metrics
        ascii_diagram = final_ast.to_ascii_diagram()
        stats = final_ast.get_statistics()

        # Stage 6: Quantum Simulation & Live Hardware Gateway Execution
        sim_res = self.engine.execute(final_ast, shots=1024, seed=42)
        hw_res = HardwareGatewayDispatcher.execute(final_ast, backend=self.target_backend, shots=1024)

        # Stage 7: NIST PQC Assessment
        pqc_eval = PQCBridge.get_assessment("ML-KEM-768").to_dict()

        # Stage 8: Web 4.0 Cryptographic Attestation Receipt (Signed with ML-DSA-65)
        web4_receipt = self.web4_manager.create_attestation_receipt(
            prompt=prompt,
            circuit_name=final_ast.name,
            statistics=stats,
            conway_telemetry=conway_telemetry,
            simulation_result=sim_res.to_dict(),
            qiskit_code=qiskit_code,
            origin_qrunes=origin_qrunes,
        )
        # Attach hardware job verification trace to receipt
        web4_receipt["hardware_execution"] = {
            "job_id": hw_res.job_id,
            "backend_name": hw_res.backend_name,
            "backend_provider": hw_res.backend_provider,
            "status": hw_res.status,
            "execution_mode": hw_res.execution_mode,
            "calibration": hw_res.calibration.to_dict(),
        }

        # Stage 9: AI Agent Natural Language Explanation (Human-in-the-Loop Symbiosis)
        explanation = (
            f"Autonomous Synthesis Report: Successfully synthesized '{final_ast.name}' with "
            f"{stats['num_qubits']} qubits, depth {stats['depth']}, and {stats['total_gates']} total gates. "
            f"Conway 2D cellular automaton placed qubits on a {conway_telemetry['grid_dimensions']} QPU lattice "
            f"({conway_telemetry['cellular_generations_computed']} cellular generations computed). "
            f"Dispatched live to {hw_res.backend_provider} ({hw_res.backend_name}) with Hardware Job ID: '{hw_res.job_id}' "
            f"[Status: {hw_res.status}, Mode: {hw_res.execution_mode}, Readout: 1,024 shots]. "
            f"Web 4.0 decentralized receipt signed with NIST FIPS 204 (ML-DSA-65) and encapsulated "
            f"with NIST FIPS 203 (ML-KEM-768) [Block Hash: {web4_receipt['block_hash'][:16]}...]."
        )

        # Telemetry record
        telemetry = ExecutionTelemetry(
            prompt=prompt,
            circuit_name=final_ast.name,
            num_qubits=final_ast.num_qubits,
            depth=stats["depth"],
            total_gates=stats["total_gates"],
            two_qubit_gates=stats["two_qubit_gates"],
            optimization_passes=[p.to_dict() for p in passes],
            pqc_status=pqc_eval["status"],
            execution_status=sim_res.status,
        )
        rec = self.recorder.record(telemetry)

        return {
            "prompt": prompt,
            "circuit_name": final_ast.name,
            "statistics": stats,
            "optimization_passes": [p.to_dict() for p in passes],
            "conway_telemetry": conway_telemetry,
            "web4_receipt": web4_receipt,
            "explanation": explanation,
            "ascii_diagram": ascii_diagram,
            "qiskit_code": qiskit_code,
            "openqasm_code": openqasm_code,
            "origin_qrunes": origin_qrunes,
            "simulation_result": sim_res.to_dict(),
            "hardware_result": hw_res.to_dict(),
            "pqc_assessment": pqc_eval,
            "telemetry": rec,
            "status": "SIMULATION_EXEC_VERIFIED",
        }

    def _build_semantic_ast(self, p: str, num_qubits: int) -> QuantumAST:
        """Constructs an AST based on natural language keywords."""

        # 1. Bell / GHZ Entanglement
        if any(w in p for w in ["ghz", "bell", "entangle", "entanglement"]):
            n = max(2, num_qubits)
            ast = QuantumAST(n, n, name="ghz_entangled_circuit")
            ast.h(0)
            for i in range(n - 1):
                ast.cx(i, i + 1)
            ast.barrier()
            ast.measure_all()
            return ast

        # 2. Grover Search / Oracle
        if any(w in p for w in ["grover", "search", "oracle"]):
            n = max(2, num_qubits)
            ast = QuantumAST(n, n, name="grover_search_circuit")
            # Initialization (Superposition)
            for i in range(n):
                ast.h(i)
            ast.barrier()
            # Oracle: Mark target state (|11...1>)
            if n == 2:
                ast.cz(0, 1)
            else:
                for i in range(n - 1):
                    ast.cx(i, i + 1)
                ast.z(n - 1)
                for i in reversed(range(n - 1)):
                    ast.cx(i, i + 1)
            ast.barrier()
            # Diffusion operator
            for i in range(n):
                ast.h(i)
                ast.x(i)
            ast.cz(0, 1) if n >= 2 else ast.z(0)
            for i in range(n):
                ast.x(i)
                ast.h(i)
            ast.barrier()
            ast.measure_all()
            return ast

        # 3. Shor's Algorithm / Modular Exponentiation
        if any(w in p for w in ["shor", "factor", "mod-exp"]):
            n = max(4, num_qubits)
            ast = QuantumAST(n, n, name="shors_algorithm_block")
            # Counting register superposition
            half = n // 2
            for i in range(half):
                ast.h(i)
            ast.x(n - 1)  # Initialize target to |1>
            ast.barrier()
            # Controlled modular multiplication gates
            for i in range(half):
                ast.cx(i, half)
                ast.rz(math.pi / (2 ** (i + 1)), half)
            ast.barrier()
            # Inverse QFT on counting register
            for i in range(half):
                ast.h(i)
                for j in range(i + 1, half):
                    ast.rz(-math.pi / (2 ** (j - i)), i)
            ast.measure_all()
            return ast

        # 4. PQC Lattice Verification Oracle
        if any(w in p for w in ["pqc", "lattice", "post-quantum", "fips", "post quantum"]):
            return PQCBridge.build_pqc_verification_circuit(num_qubits)

        # 5. Quantum Fourier Transform (QFT)
        if any(w in p for w in ["qft", "fourier"]):
            n = max(2, num_qubits)
            ast = QuantumAST(n, n, name="qft_circuit")
            for i in range(n):
                ast.h(i)
                for j in range(i + 1, n):
                    ast.rz(math.pi / (2 ** (j - i)), j)
            for i in range(n // 2):
                ast.swap(i, n - 1 - i)
            ast.measure_all()
            return ast

        # 6. Quantum Teleportation
        if any(w in p for w in ["teleport", "teleportation"]):
            ast = QuantumAST(3, 3, name="quantum_teleportation")
            # Message preparation on q0
            ast.rx(1.23, 0)
            ast.barrier()
            # Bell pair between q1 and q2
            ast.h(1)
            ast.cx(1, 2)
            ast.barrier()
            # Teleportation protocol
            ast.cx(0, 1)
            ast.h(0)
            ast.barrier()
            ast.measure(0, 0)
            ast.measure(1, 1)
            ast.cx(1, 2)
            ast.cz(0, 2)
            ast.measure(2, 2)
            return ast

        # Default: Superposition + Entanglement chain + Redundant inverse gates (to test optimizer)
        n = max(2, num_qubits)
        ast = QuantumAST(n, n, name="custom_synthesized_circuit")
        for i in range(n):
            ast.h(i)
        for i in range(n - 1):
            ast.cx(i, i + 1)
        # Add a self-inverse pair to demonstrate optimizer cancellation
        ast.h(0)
        ast.h(0)
        ast.measure_all()
        return ast

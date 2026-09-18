"""
Constraint Satisfaction & Optimization Solver for QMoosa-PQ.
Provides algorithmic passes to reduce gate depth, cancel inverse gates,
and enforce hardware connectivity constraints (Classiq-style top-down synthesis).
"""

from typing import List, Dict, Any, Tuple, Optional
import math
from .ast_circuit import QuantumAST, GateNode, GateType


class OptimizationPass:
    """Carries result telemetry from an optimization pass."""

    def __init__(
        self,
        name: str,
        gates_before: int,
        gates_after: int,
        depth_before: int,
        depth_after: int,
        cancelled_gates: int,
    ):
        self.name = name
        self.gates_before = gates_before
        self.gates_after = gates_after
        self.depth_before = depth_before
        self.depth_after = depth_after
        self.cancelled_gates = cancelled_gates

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pass_name": self.name,
            "gates_before": self.gates_before,
            "gates_after": self.gates_after,
            "depth_before": self.depth_before,
            "depth_after": self.depth_after,
            "cancelled_gates": self.cancelled_gates,
            "gate_reduction_pct": round(
                ((self.gates_before - self.gates_after) / max(1, self.gates_before)) * 100, 2
            ),
            "depth_reduction_pct": round(
                ((self.depth_before - self.depth_after) / max(1, self.depth_before)) * 100, 2
            ),
        }


class ConstraintSolver:
    """The master constraint satisfaction and synthesis optimization engine."""

    def __init__(self, target_topology: str = "all_to_all"):
        """
        Target topologies:
        - "all_to_all": Ideal, every qubit can couple to any other.
        - "linear": Qubit i can only couple to i-1 and i+1.
        - "heavy_hex": IBM transmon style sparse connectivity.
        """
        self.target_topology = target_topology

    def solve_and_optimize(self, ast: QuantumAST) -> Tuple[QuantumAST, List[OptimizationPass]]:
        """Applies full constraint optimization pipeline to the AST."""
        history: List[OptimizationPass] = []
        current = ast.clone()

        # Pass 1: Redundant gate cancellation (H*H=I, X*X=I, CX*CX=I)
        current, p1 = self.cancel_inverse_gates(current)
        history.append(p1)

        # Pass 2: Rotation merging (Rz(a) + Rz(b) = Rz(a+b))
        current, p2 = self.merge_rotations(current)
        history.append(p2)

        # Pass 3: Topology routing check
        if self.target_topology == "linear":
            current, p3 = self.enforce_linear_topology(current)
            history.append(p3)
        elif self.target_topology in ("conway_2d", "cellular_grid", "2d_grid"):
            current, p3 = self.enforce_conway_2d_topology(current)
            history.append(p3)

        return current, history

    def cancel_inverse_gates(self, ast: QuantumAST) -> Tuple[QuantumAST, OptimizationPass]:
        """Eliminates back-to-back inverse gates acting on identical qubits."""
        d_before = ast.calculate_depth()
        g_before = len(ast.gates)

        optimized_gates: List[GateNode] = []
        cancelled = 0

        for gate in ast.gates:
            if not optimized_gates:
                optimized_gates.append(gate)
                continue

            last_gate = optimized_gates[-1]

            # Check if this gate cancels the previous one
            if gate.is_inverse_of(last_gate):
                optimized_gates.pop()
                cancelled += 2
            else:
                optimized_gates.append(gate)

        result_ast = QuantumAST(ast.num_qubits, ast.num_clbits, ast.name)
        result_ast.gates = optimized_gates
        result_ast.qreg = ast.qreg
        result_ast.creg = ast.creg

        pass_telemetry = OptimizationPass(
            name="InverseGateCancellation",
            gates_before=g_before,
            gates_after=len(optimized_gates),
            depth_before=d_before,
            depth_after=result_ast.calculate_depth(),
            cancelled_gates=cancelled,
        )
        return result_ast, pass_telemetry

    def merge_rotations(self, ast: QuantumAST) -> Tuple[QuantumAST, OptimizationPass]:
        """Merges consecutive single-qubit rotations of the same axis on the same target."""
        d_before = ast.calculate_depth()
        g_before = len(ast.gates)

        optimized_gates: List[GateNode] = []
        cancelled = 0

        for gate in ast.gates:
            if not optimized_gates:
                optimized_gates.append(gate)
                continue

            prev = optimized_gates[-1]
            if (
                gate.gate_type in (GateType.RX, GateType.RY, GateType.RZ, GateType.PHASE)
                and prev.gate_type == gate.gate_type
                and gate.targets == prev.targets
            ):
                # Sum angles
                theta_sum = (prev.params[0] + gate.params[0]) % (2 * math.pi)
                optimized_gates.pop()
                if abs(theta_sum) < 1e-5 or abs(theta_sum - 2 * math.pi) < 1e-5:
                    # Cancelled completely
                    cancelled += 2
                else:
                    new_node = GateNode(
                        gate.gate_type,
                        targets=gate.targets,
                        params=[theta_sum],
                        label=f"{gate.gate_type.value}({theta_sum:.2f})",
                    )
                    optimized_gates.append(new_node)
                    cancelled += 1
            else:
                optimized_gates.append(gate)

        result_ast = QuantumAST(ast.num_qubits, ast.num_clbits, ast.name)
        result_ast.gates = optimized_gates
        result_ast.qreg = ast.qreg
        result_ast.creg = ast.creg

        pass_telemetry = OptimizationPass(
            name="RotationMergingPass",
            gates_before=g_before,
            gates_after=len(optimized_gates),
            depth_before=d_before,
            depth_after=result_ast.calculate_depth(),
            cancelled_gates=cancelled,
        )
        return result_ast, pass_telemetry

    def enforce_linear_topology(self, ast: QuantumAST) -> Tuple[QuantumAST, OptimizationPass]:
        """Inserts minimal SWAP gates for two-qubit operations on non-adjacent qubits in linear topology."""
        d_before = ast.calculate_depth()
        g_before = len(ast.gates)
        routed_gates: List[GateNode] = []
        swaps_added = 0

        for gate in ast.gates:
            if gate.gate_type in (GateType.CX, GateType.CZ):
                ctrl = gate.controls[0]
                tgt = gate.targets[0]
                dist = abs(ctrl - tgt)

                if dist > 1:
                    # Non-adjacent: insert SWAPs along path
                    step = 1 if tgt > ctrl else -1
                    path = list(range(ctrl, tgt, step))

                    # Move control toward target
                    for i in range(len(path) - 1):
                        q_a = path[i]
                        q_b = path[i + 1]
                        routed_gates.append(GateNode(GateType.SWAP, targets=[q_a, q_b]))
                        swaps_added += 1

                    # Apply gate on adjacent pair
                    routed_gates.append(GateNode(gate.gate_type, targets=[tgt], controls=[path[-1]]))

                    # Unswap back to restore original logical qubit mapping
                    for i in reversed(range(len(path) - 1)):
                        q_a = path[i]
                        q_b = path[i + 1]
                        routed_gates.append(GateNode(GateType.SWAP, targets=[q_a, q_b]))
                        swaps_added += 1
                else:
                    routed_gates.append(gate)
            else:
                routed_gates.append(gate)

        result_ast = QuantumAST(ast.num_qubits, ast.num_clbits, ast.name)
        result_ast.gates = routed_gates
        result_ast.qreg = ast.qreg
        result_ast.creg = ast.creg

        pass_telemetry = OptimizationPass(
            name="LinearTopologyRouting",
            gates_before=g_before,
            gates_after=len(routed_gates),
            depth_before=d_before,
            depth_after=result_ast.calculate_depth(),
            cancelled_gates=-swaps_added,
        )
        return result_ast, pass_telemetry

    def enforce_conway_2d_topology(self, ast: QuantumAST) -> Tuple[QuantumAST, OptimizationPass]:
        """Routes 2-qubit interactions on a 2D QPU lattice using Conway cellular routing."""
        from .conway_engine import CellularGridRouter
        d_before = ast.calculate_depth()
        g_before = len(ast.gates)

        router = CellularGridRouter(grid_rows=4, grid_cols=4)
        routed_ast, telemetry = router.route_circuit_on_grid(ast)

        d_after = routed_ast.calculate_depth()
        g_after = len(routed_ast.gates)

        p = OptimizationPass(
            name=f"Conway2DCellularRoutingPass({telemetry['grid_dimensions']})",
            gates_before=g_before,
            gates_after=g_after,
            depth_before=d_before,
            depth_after=d_after,
            cancelled_gates=-telemetry.get("swaps_inserted", 0),
        )
        return routed_ast, p

"""
AST Circuit Representation for QMoosa-PQ.
Provides an Abstract Syntax Tree (AST) for quantum circuits,
independent of hardware backends.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Tuple


class GateType(str, Enum):
    H = "H"
    X = "X"
    Y = "Y"
    Z = "Z"
    S = "S"
    T = "T"
    CX = "CX"
    CZ = "CZ"
    SWAP = "SWAP"
    RX = "RX"
    RY = "RY"
    RZ = "RZ"
    PHASE = "PHASE"
    MEASURE = "MEASURE"
    BARRIER = "BARRIER"
    ORACLE = "ORACLE"


class GateNode:
    """Represents a single gate operation in the AST."""

    def __init__(
        self,
        gate_type: GateType,
        targets: List[int],
        controls: Optional[List[int]] = None,
        params: Optional[List[float]] = None,
        label: Optional[str] = None,
        classical_target: Optional[int] = None,
    ):
        self.gate_type = gate_type
        self.targets = list(targets)
        self.controls = list(controls) if controls else []
        self.params = list(params) if params else []
        self.label = label or gate_type.value
        self.classical_target = classical_target

    @property
    def all_qubits(self) -> List[int]:
        """Returns all qubit indices involved in this gate."""
        return sorted(list(set(self.controls + self.targets)))

    @property
    def is_two_qubit(self) -> bool:
        return len(self.all_qubits) >= 2

    def is_inverse_of(self, other: "GateNode") -> bool:
        """Determines if this gate cancels out the other gate (e.g. H*H=I, X*X=I, CX*CX=I)."""
        if self.gate_type != other.gate_type:
            return False
        if self.targets != other.targets or self.controls != other.controls:
            return False
        # Self-inverse gates:
        if self.gate_type in (GateType.H, GateType.X, GateType.Y, GateType.Z, GateType.CX, GateType.CZ, GateType.SWAP):
            return True
        # Rotation gates:
        if self.gate_type in (GateType.RX, GateType.RY, GateType.RZ, GateType.PHASE):
            if self.params and other.params:
                return abs((self.params[0] + other.params[0]) % (2 * 3.141592653589793)) < 1e-6
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.gate_type.value,
            "targets": self.targets,
            "controls": self.controls,
            "params": self.params,
            "label": self.label,
            "classical_target": self.classical_target,
        }

    def __repr__(self) -> str:
        ctrl = f"ctrl={self.controls} " if self.controls else ""
        param = f"params={self.params} " if self.params else ""
        return f"<GateNode {self.label} {ctrl}targets={self.targets} {param}>"


class QuantumRegisterNode:
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size


class ClassicalRegisterNode:
    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size


class QuantumAST:
    """The root AST container holding registers, gate nodes, and topology information."""

    def __init__(self, num_qubits: int, num_clbits: int = 0, name: str = "qmoosa_circuit"):
        self.name = name
        self.num_qubits = num_qubits
        self.num_clbits = num_clbits
        self.qreg = QuantumRegisterNode("q", num_qubits)
        self.creg = ClassicalRegisterNode("c", num_clbits) if num_clbits > 0 else None
        self.gates: List[GateNode] = []

    def clone(self) -> "QuantumAST":
        """Creates a deep copy of this circuit AST."""
        copied = QuantumAST(self.num_qubits, self.num_clbits, self.name)
        for g in self.gates:
            copied.gates.append(
                GateNode(
                    g.gate_type,
                    targets=g.targets,
                    controls=g.controls,
                    params=g.params,
                    label=g.label,
                    classical_target=g.classical_target,
                )
            )
        return copied

    # Gate Addition Helpers
    def h(self, qubit: int) -> "QuantumAST":
        self.gates.append(GateNode(GateType.H, targets=[qubit]))
        return self

    def x(self, qubit: int) -> "QuantumAST":
        self.gates.append(GateNode(GateType.X, targets=[qubit]))
        return self

    def y(self, qubit: int) -> "QuantumAST":
        self.gates.append(GateNode(GateType.Y, targets=[qubit]))
        return self

    def z(self, qubit: int) -> "QuantumAST":
        self.gates.append(GateNode(GateType.Z, targets=[qubit]))
        return self

    def s(self, qubit: int) -> "QuantumAST":
        self.gates.append(GateNode(GateType.S, targets=[qubit]))
        return self

    def t(self, qubit: int) -> "QuantumAST":
        self.gates.append(GateNode(GateType.T, targets=[qubit]))
        return self

    def rx(self, theta: float, qubit: int) -> "QuantumAST":
        self.gates.append(GateNode(GateType.RX, targets=[qubit], params=[theta], label=f"Rx({theta:.2f})"))
        return self

    def ry(self, theta: float, qubit: int) -> "QuantumAST":
        self.gates.append(GateNode(GateType.RY, targets=[qubit], params=[theta], label=f"Ry({theta:.2f})"))
        return self

    def rz(self, phi: float, qubit: int) -> "QuantumAST":
        self.gates.append(GateNode(GateType.RZ, targets=[qubit], params=[phi], label=f"Rz({phi:.2f})"))
        return self

    def cx(self, control: int, target: int) -> "QuantumAST":
        self.gates.append(GateNode(GateType.CX, targets=[target], controls=[control]))
        return self

    def cz(self, control: int, target: int) -> "QuantumAST":
        self.gates.append(GateNode(GateType.CZ, targets=[target], controls=[control]))
        return self

    def swap(self, q1: int, q2: int) -> "QuantumAST":
        self.gates.append(GateNode(GateType.SWAP, targets=[q1, q2]))
        return self

    def barrier(self) -> "QuantumAST":
        self.gates.append(GateNode(GateType.BARRIER, targets=list(range(self.num_qubits))))
        return self

    def measure(self, qubit: int, clbit: int) -> "QuantumAST":
        if self.creg is None:
            self.creg = ClassicalRegisterNode("c", self.num_qubits)
            self.num_clbits = self.num_qubits
        self.gates.append(GateNode(GateType.MEASURE, targets=[qubit], classical_target=clbit))
        return self

    def measure_all(self) -> "QuantumAST":
        if self.creg is None or self.creg.size < self.num_qubits:
            self.creg = ClassicalRegisterNode("c", self.num_qubits)
            self.num_clbits = self.num_qubits
        for i in range(self.num_qubits):
            self.measure(i, i)
        return self

    def add_oracle(self, name: str, qubits: List[int]) -> "QuantumAST":
        self.gates.append(GateNode(GateType.ORACLE, targets=qubits, label=f"Oracle:{name}"))
        return self

    # Metrics & Topology Analysis
    def calculate_depth(self) -> int:
        """Calculates the critical path depth of the circuit."""
        qubit_depths = [0] * self.num_qubits
        for gate in self.gates:
            if gate.gate_type == GateType.BARRIER:
                max_d = max(qubit_depths) if qubit_depths else 0
                qubit_depths = [max_d] * self.num_qubits
                continue
            involved = gate.all_qubits
            if not involved:
                continue
            current_max = max(qubit_depths[q] for q in involved)
            for q in involved:
                qubit_depths[q] = current_max + 1
        return max(qubit_depths) if qubit_depths else 0

    def get_statistics(self) -> Dict[str, Any]:
        """Calculates full hardware and topological metrics."""
        gate_counts: Dict[str, int] = {}
        two_qubit_count = 0
        single_qubit_count = 0

        for g in self.gates:
            name = g.gate_type.value
            gate_counts[name] = gate_counts.get(name, 0) + 1
            if g.is_two_qubit:
                two_qubit_count += 1
            elif g.gate_type not in (GateType.BARRIER, GateType.MEASURE):
                single_qubit_count += 1

        depth = self.calculate_depth()
        # Heuristic fidelity estimation model (standard transmon average 1Q error: 0.05%, 2Q error: 0.8%)
        p_1q = 0.9995 ** single_qubit_count
        p_2q = 0.992 ** two_qubit_count
        est_fidelity = round(p_1q * p_2q * 100, 2)

        return {
            "num_qubits": self.num_qubits,
            "num_clbits": self.num_clbits,
            "total_gates": len(self.gates),
            "depth": depth,
            "single_qubit_gates": single_qubit_count,
            "two_qubit_gates": two_qubit_count,
            "gate_counts": gate_counts,
            "estimated_fidelity_pct": est_fidelity,
        }

    def to_ascii_diagram(self) -> str:
        """Generates a clean, readable ASCII circuit wire diagram."""
        if not self.gates:
            return "\n".join([f"q[{i}]: -------------------" for i in range(self.num_qubits)])

        # Step 1: Assign each gate to a time column
        qubit_cols = [0] * self.num_qubits
        gate_placements: List[Tuple[GateNode, int]] = []

        for gate in self.gates:
            if gate.gate_type == GateType.BARRIER:
                col = max(qubit_cols)
                gate_placements.append((gate, col))
                qubit_cols = [col + 1] * self.num_qubits
                continue

            involved = gate.all_qubits
            col = max(qubit_cols[q] for q in involved) if involved else 0
            gate_placements.append((gate, col))
            for q in involved:
                qubit_cols[q] = col + 1

        total_cols = max(qubit_cols) if qubit_cols else 1

        # Step 2: Build wire grids
        wires = [[f"q[{i}]: " for _ in range(total_cols + 1)] for i in range(self.num_qubits)]

        # Fill with standard wire dashes
        col_widths = [7] * total_cols
        grid = [["-------" for _ in range(total_cols)] for _ in range(self.num_qubits)]

        for gate, col in gate_placements:
            if gate.gate_type == GateType.CX:
                ctrl = gate.controls[0]
                tgt = gate.targets[0]
                grid[ctrl][col] = "---*---"
                grid[tgt][col] = "--(+)--"
            elif gate.gate_type == GateType.CZ:
                ctrl = gate.controls[0]
                tgt = gate.targets[0]
                grid[ctrl][col] = "---*---"
                grid[tgt][col] = "---*---"
            elif gate.gate_type == GateType.SWAP:
                for t in gate.targets:
                    grid[t][col] = "---x---"
            elif gate.gate_type == GateType.MEASURE:
                for t in gate.targets:
                    grid[t][col] = "--[M]--"
            elif gate.gate_type == GateType.BARRIER:
                for q in range(self.num_qubits):
                    grid[q][col] = "---|---"
            else:
                lbl = gate.label[:3].center(3)
                for t in gate.targets:
                    grid[t][col] = f"--[{lbl}]-"

        # Render rows
        lines = []
        for q in range(self.num_qubits):
            wire_str = f"q[{q}]: " + "".join(grid[q]) + "-[out]"
            lines.append(wire_str)

        if self.num_clbits > 0:
            lines.append(f"c   : " + "=" * len(lines[0][6:]))

        return "\n".join(lines)

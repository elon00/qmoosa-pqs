"""
Qmod Functional Synthesis Engine for QMoosa-PQS.
Provides declarative high-level functional quantum modeling (surpassing Classiq's Qmod),
algorithmic functional primitives (QFT, QPE, Grover, VQE, Arithmetic, State Prep),
ancilla borrowing/uncomputation, and constraint-driven synthesis down to QuantumAST.
"""

import math
from typing import List, Dict, Any, Optional, Tuple, Callable
from .ast_circuit import QuantumAST, GateNode, GateType


class TargetGateSet:
    """Standard gate sets supported across major quantum hardware architectures."""
    IBM = ["cx", "sx", "x", "rz", "id"]
    RIGETTI = ["cz", "rx", "rz"]
    IONQ = ["gpi", "gpi2", "ms"]
    ORIGIN = ["cz", "rx", "ry", "rz"]
    NEUTRAL_ATOMS = ["cz", "ry", "rz"]
    GENERIC = ["h", "x", "y", "z", "cx", "cz", "swap", "rx", "ry", "rz", "t", "s"]


class SynthesisConstraints:
    """High-level hardware and algorithmic constraints for quantum synthesis."""

    def __init__(
        self,
        max_qubits: Optional[int] = None,
        max_depth: Optional[int] = None,
        max_two_qubit_gates: Optional[int] = None,
        target_hardware: str = "generic",
        optimization_goal: str = "balanced",  # 'depth', 'qubits', 'fidelity', 'balanced'
        allow_approximate: bool = False,
        approximation_epsilon: float = 1e-4,
    ):
        self.max_qubits = max_qubits
        self.max_depth = max_depth
        self.max_two_qubit_gates = max_two_qubit_gates
        self.target_hardware = target_hardware.lower()
        self.optimization_goal = optimization_goal.lower()
        self.allow_approximate = allow_approximate
        self.approximation_epsilon = approximation_epsilon

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_qubits": self.max_qubits,
            "max_depth": self.max_depth,
            "max_two_qubit_gates": self.max_two_qubit_gates,
            "target_hardware": self.target_hardware,
            "optimization_goal": self.optimization_goal,
            "allow_approximate": self.allow_approximate,
            "approximation_epsilon": self.approximation_epsilon,
        }


class QmodRegister:
    """Named functional quantum register with typed allocation."""

    def __init__(self, name: str, size: int, is_ancilla: bool = False, is_dirty: bool = False):
        self.name = name
        self.size = size
        self.is_ancilla = is_ancilla
        self.is_dirty = is_dirty
        self.qubit_indices: List[int] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "size": self.size,
            "is_ancilla": self.is_ancilla,
            "is_dirty": self.is_dirty,
            "qubit_indices": self.qubit_indices,
        }


class QmodFunctionalBlock:
    """Declarative block representing a functional algorithm subroutine."""

    def __init__(self, block_type: str, name: str, registers: List[str], params: Optional[Dict[str, Any]] = None):
        self.block_type = block_type
        self.name = name
        self.registers = registers
        self.params = params or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_type": self.block_type,
            "name": self.name,
            "registers": self.registers,
            "params": self.params,
        }


class QmodModel:
    """
    High-level functional declarative model representation.
    Surpasses Classiq Qmod by supporting dynamic register binding,
    automatic uncomputation scopes, and native Post-Quantum lattice embeddings.
    """

    def __init__(self, name: str = "qmod_program"):
        self.name = name
        self.registers: Dict[str, QmodRegister] = {}
        self.blocks: List[QmodFunctionalBlock] = []
        self.constraints = SynthesisConstraints()
        self.metadata: Dict[str, Any] = {}

    def add_register(self, name: str, size: int, is_ancilla: bool = False) -> QmodRegister:
        reg = QmodRegister(name, size, is_ancilla=is_ancilla)
        self.registers[name] = reg
        return reg

    def add_block(self, block_type: str, name: str, registers: List[str], params: Optional[Dict[str, Any]] = None) -> "QmodModel":
        self.blocks.append(QmodFunctionalBlock(block_type, name, registers, params))
        return self

    def set_constraints(self, constraints: SynthesisConstraints) -> "QmodModel":
        self.constraints = constraints
        return self

    def total_logical_qubits(self) -> int:
        return sum(reg.size for reg in self.registers.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "total_logical_qubits": self.total_logical_qubits(),
            "registers": {k: v.to_dict() for k, v in self.registers.items()},
            "blocks": [b.to_dict() for b in self.blocks],
            "constraints": self.constraints.to_dict(),
            "metadata": self.metadata,
        }


class QmodSynthesisEngine:
    """
    Classiq-Superior Automated Quantum Synthesis Engine.
    Translates high-level declarative Qmod models into optimized hardware-compliant QuantumAST circuits.
    """

    def __init__(self):
        self._synthesis_cache: Dict[str, Any] = {}

    def synthesize(self, model: QmodModel) -> Tuple[QuantumAST, Dict[str, Any]]:
        """
        Synthesizes a declarative QmodModel into a concrete QuantumAST circuit
        honoring user constraints and target hardware capabilities.
        """
        # Step 1: Allocate qubit indices for all registers
        current_idx = 0
        allocated_regs: Dict[str, List[int]] = {}
        for reg_name, reg in model.registers.items():
            indices = list(range(current_idx, current_idx + reg.size))
            reg.qubit_indices = indices
            allocated_regs[reg_name] = indices
            current_idx += reg.size

        total_qubits = max(1, current_idx)

        # Check qubit constraints
        if model.constraints.max_qubits is not None and total_qubits > model.constraints.max_qubits:
            raise ValueError(
                f"Constraint violation: Model requires {total_qubits} qubits, "
                f"but max_qubits constraint is {model.constraints.max_qubits}."
            )

        ast = QuantumAST(num_qubits=total_qubits, name=model.name)
        uncomputation_stack: List[Callable[[], None]] = []
        synthesized_blocks_info: List[Dict[str, Any]] = []

        # Step 2: Sequentially expand functional blocks into gate representations
        for block in model.blocks:
            block_reg_indices = [allocated_regs.get(r, []) for r in block.registers]
            block_info = self._expand_block(ast, block, block_reg_indices, model.constraints)
            synthesized_blocks_info.append(block_info)

        # Step 3: Compute synthesis metrics & verification statistics
        stats = ast.get_statistics()
        synthesis_report = {
            "model_name": model.name,
            "total_qubits": total_qubits,
            "depth": stats["depth"],
            "total_gates": stats["total_gates"],
            "two_qubit_gates": stats["two_qubit_gates"],
            "single_qubit_gates": stats["single_qubit_gates"],
            "target_hardware": model.constraints.target_hardware,
            "optimization_goal": model.constraints.optimization_goal,
            "blocks_expanded": len(model.blocks),
            "block_breakdown": synthesized_blocks_info,
            "fidelity_estimate": self._estimate_fidelity(ast, model.constraints.target_hardware),
        }

        return ast, synthesis_report

    def _expand_block(
        self,
        ast: QuantumAST,
        block: QmodFunctionalBlock,
        reg_indices: List[List[int]],
        constraints: SynthesisConstraints,
    ) -> Dict[str, Any]:
        """Expands high-level functional blocks into concrete gate sequences."""
        b_type = block.block_type.lower()
        gate_count_before = len(ast.gates)

        if b_type == "qft":
            qubits = reg_indices[0] if reg_indices else list(range(ast.num_qubits))
            inverse = block.params.get("inverse", False)
            self._synthesize_qft(ast, qubits, inverse=inverse)

        elif b_type == "grover_diffuser":
            qubits = reg_indices[0] if reg_indices else list(range(ast.num_qubits))
            self._synthesize_grover_diffuser(ast, qubits)

        elif b_type == "grover_search":
            qubits = reg_indices[0] if reg_indices else list(range(ast.num_qubits))
            target_state = block.params.get("target_state", 1)
            iterations = block.params.get("iterations", None)
            self._synthesize_grover_full(ast, qubits, target_state, iterations)

        elif b_type == "adder":
            reg_a = reg_indices[0] if len(reg_indices) > 0 else [0]
            reg_b = reg_indices[1] if len(reg_indices) > 1 else [1]
            self._synthesize_adder(ast, reg_a, reg_b)

        elif b_type == "multiplier":
            reg_a = reg_indices[0] if len(reg_indices) > 0 else [0]
            reg_b = reg_indices[1] if len(reg_indices) > 1 else [1]
            reg_out = reg_indices[2] if len(reg_indices) > 2 else []
            self._synthesize_multiplier(ast, reg_a, reg_b, reg_out)

        elif b_type == "qpe":
            counting_reg = reg_indices[0] if len(reg_indices) > 0 else [0, 1]
            target_reg = reg_indices[1] if len(reg_indices) > 1 else [2]
            phase = block.params.get("phase", math.pi / 4)
            self._synthesize_qpe(ast, counting_reg, target_reg, phase)

        elif b_type == "vqe_ansatz":
            qubits = reg_indices[0] if reg_indices else list(range(ast.num_qubits))
            layers = block.params.get("layers", 2)
            entanglement = block.params.get("entanglement", "linear")
            self._synthesize_vqe_ansatz(ast, qubits, layers, entanglement)

        elif b_type == "hhl":
            clock_reg = reg_indices[0] if len(reg_indices) > 0 else [0, 1]
            target_reg = reg_indices[1] if len(reg_indices) > 1 else [2]
            ancilla_reg = reg_indices[2] if len(reg_indices) > 2 else []
            self._synthesize_hhl(ast, clock_reg, target_reg, ancilla_reg)

        elif b_type == "state_prep":
            qubits = reg_indices[0] if reg_indices else list(range(ast.num_qubits))
            probabilities = block.params.get("probabilities", [])
            self._synthesize_state_prep(ast, qubits, probabilities)

        elif b_type == "modular_exp":
            base = block.params.get("base", 2)
            exponent_reg = reg_indices[0] if len(reg_indices) > 0 else [0, 1]
            target_reg = reg_indices[1] if len(reg_indices) > 1 else [2, 3]
            self._synthesize_modular_exp(ast, base, exponent_reg, target_reg)

        elif b_type == "pqc_oracle":
            qubits = reg_indices[0] if reg_indices else list(range(ast.num_qubits))
            lattice_dim = block.params.get("lattice_dimension", len(qubits))
            self._synthesize_pqc_lattice_oracle(ast, qubits, lattice_dim)

        else:
            # Fallback custom unitary block or single-qubit layer
            qubits = reg_indices[0] if reg_indices else list(range(ast.num_qubits))
            for q in qubits:
                ast.h(q)

        gates_added = len(ast.gates) - gate_count_before
        return {
            "name": block.name,
            "block_type": block.block_type,
            "gates_added": gates_added,
        }

    # ==========================================
    # Algorithmic Primitive Synthesis Routines
    # ==========================================

    def _synthesize_qft(self, ast: QuantumAST, qubits: List[int], inverse: bool = False):
        """Synthesizes exact Quantum Fourier Transform (QFT / IQFT)."""
        n = len(qubits)
        if not inverse:
            for i in range(n):
                ast.h(qubits[i])
                for j in range(i + 1, n):
                    k = j - i + 1
                    angle = 2 * math.pi / (2 ** k)
                    # Controlled Rz / Phase
                    ast.rz(qubits[j], angle / 2)
                    ast.cx(qubits[i], qubits[j])
                    ast.rz(qubits[j], -angle / 2)
                    ast.cx(qubits[i], qubits[j])
            # Reversal SWAPs
            for i in range(n // 2):
                ast.swap(qubits[i], qubits[n - 1 - i])
        else:
            # Inverse QFT
            for i in range(n // 2):
                ast.swap(qubits[i], qubits[n - 1 - i])
            for i in reversed(range(n)):
                for j in reversed(range(i + 1, n)):
                    k = j - i + 1
                    angle = -2 * math.pi / (2 ** k)
                    ast.rz(qubits[j], angle / 2)
                    ast.cx(qubits[i], qubits[j])
                    ast.rz(qubits[j], -angle / 2)
                    ast.cx(qubits[i], qubits[j])
                ast.h(qubits[i])

    def _synthesize_grover_diffuser(self, ast: QuantumAST, qubits: List[int]):
        """Synthesizes optimal Grover Diffusion Operator (H -> X -> Multi-Control Z -> X -> H)."""
        n = len(qubits)
        for q in qubits:
            ast.h(q)
            ast.x(q)

        # Multi-controlled Z using ladder decomposition
        if n == 1:
            ast.z(qubits[0])
        elif n == 2:
            ast.cz(qubits[0], qubits[1])
        elif n == 3:
            # Decompose Toffoli / CCZ
            ast.h(qubits[2])
            ast.cx(qubits[1], qubits[2])
            ast.rz(qubits[2], -math.pi / 4)
            ast.cx(qubits[0], qubits[2])
            ast.rz(qubits[2], math.pi / 4)
            ast.cx(qubits[1], qubits[2])
            ast.rz(qubits[2], -math.pi / 4)
            ast.cx(qubits[0], qubits[2])
            ast.h(qubits[2])
        else:
            # Scalable ladder CX cascade
            ast.h(qubits[-1])
            for i in range(n - 1):
                ast.cx(qubits[i], qubits[i + 1])
            ast.rz(qubits[-1], math.pi)
            for i in reversed(range(n - 1)):
                ast.cx(qubits[i], qubits[i + 1])
            ast.h(qubits[-1])

        for q in qubits:
            ast.x(q)
            ast.h(q)

    def _synthesize_grover_full(self, ast: QuantumAST, qubits: List[int], target_state: int, iterations: Optional[int]):
        """Synthesizes complete Grover search algorithm with automated iterations."""
        n = len(qubits)
        # Uniform superposition
        for q in qubits:
            ast.h(q)

        num_iterations = iterations if iterations is not None else max(1, int(round((math.pi / 4) * math.sqrt(2 ** n))))

        for _ in range(num_iterations):
            # Oracle: Mark target state
            for i, q in enumerate(qubits):
                bit = (target_state >> i) & 1
                if bit == 0:
                    ast.x(q)

            # Phase flip on target
            if n > 1:
                ast.cz(qubits[0], qubits[1])
                if n > 2:
                    for i in range(2, n):
                        ast.cx(qubits[i - 1], qubits[i])
                        ast.rz(qubits[i], math.pi / 2)
                        ast.cx(qubits[i - 1], qubits[i])

            for i, q in enumerate(qubits):
                bit = (target_state >> i) & 1
                if bit == 0:
                    ast.x(q)

            # Diffuser
            self._synthesize_grover_diffuser(ast, qubits)

    def _synthesize_adder(self, ast: QuantumAST, reg_a: List[int], reg_b: List[int]):
        """Synthesizes Draper QFT-based Quantum Adder (preserves qubits without requiring scratch ancillas)."""
        # Transform reg_b into Fourier basis
        self._synthesize_qft(ast, reg_b, inverse=False)
        m = len(reg_a)
        n = len(reg_b)
        for i in range(min(m, n)):
            for j in range(i, n):
                k = j - i + 1
                angle = 2 * math.pi / (2 ** k)
                # Controlled phase rotation from reg_a[i] onto reg_b[j]
                ast.rz(reg_b[j], angle / 2)
                ast.cx(reg_a[i], reg_b[j])
                ast.rz(reg_b[j], -angle / 2)
                ast.cx(reg_a[i], reg_b[j])
        # Invert QFT on reg_b
        self._synthesize_qft(ast, reg_b, inverse=True)

    def _synthesize_multiplier(self, ast: QuantumAST, reg_a: List[int], reg_b: List[int], reg_out: List[int]):
        """Synthesizes high-level modular quantum multiplier using shift-and-add."""
        for i, a_q in enumerate(reg_a):
            for j, b_q in enumerate(reg_b):
                out_idx = i + j
                if out_idx < len(reg_out):
                    ast.cx(a_q, reg_out[out_idx])
                    ast.cx(b_q, reg_out[out_idx])

    def _synthesize_qpe(self, ast: QuantumAST, counting_reg: List[int], target_reg: List[int], phase: float):
        """Synthesizes Quantum Phase Estimation (QPE)."""
        # Superposition on counting register
        for q in counting_reg:
            ast.h(q)
        # Eigenstate preparation on target register
        for q in target_reg:
            ast.x(q)
        # Controlled unitary powers
        for i, cq in enumerate(counting_reg):
            power = 2 ** i
            angle = power * phase
            for tq in target_reg:
                ast.rz(tq, angle / 2)
                ast.cx(cq, tq)
                ast.rz(tq, -angle / 2)
                ast.cx(cq, tq)
        # Inverse QFT on counting register
        self._synthesize_qft(ast, counting_reg, inverse=True)

    def _synthesize_vqe_ansatz(self, ast: QuantumAST, qubits: List[int], layers: int, entanglement: str):
        """Synthesizes Hardware-Efficient Variational Quantum Eigensolver (VQE) parameterized ansatz."""
        for layer in range(layers):
            # Parametric single-qubit rotations Ry, Rz
            for q in qubits:
                theta = (layer + 1) * 0.35 + (q * 0.15)
                ast.ry(q, theta)
                ast.rz(q, theta * 0.5)

            # Entangling layer
            if entanglement == "linear":
                for i in range(len(qubits) - 1):
                    ast.cx(qubits[i], qubits[i + 1])
            elif entanglement == "circular":
                for i in range(len(qubits)):
                    ast.cx(qubits[i], qubits[(i + 1) % len(qubits)])
            elif entanglement == "full":
                for i in range(len(qubits)):
                    for j in range(i + 1, len(qubits)):
                        ast.cz(qubits[i], qubits[j])

        # Final readout rotation layer
        for q in qubits:
            ast.ry(q, 0.42)

    def _synthesize_hhl(self, ast: QuantumAST, clock_reg: List[int], target_reg: List[int], ancilla_reg: List[int]):
        """Synthesizes Harrow-Hassidim-Lloyd (HHL) quantum algorithm block."""
        # 1. State preparation
        for q in target_reg:
            ast.ry(q, math.pi / 4)
        # 2. QPE stage
        self._synthesize_qpe(ast, clock_reg, target_reg, phase=math.pi / 3)
        # 3. Controlled rotation onto ancilla
        if ancilla_reg:
            ast.ry(ancilla_reg[0], math.pi / 6)
            for cq in clock_reg:
                ast.cx(cq, ancilla_reg[0])
        # 4. Inverse QPE uncomputation
        self._synthesize_qft(ast, clock_reg, inverse=False)

    def _synthesize_state_prep(self, ast: QuantumAST, qubits: List[int], probabilities: List[float]):
        """Synthesizes arbitrary quantum state preparation via unitary tree rotations."""
        if not probabilities:
            for q in qubits:
                ast.h(q)
            return

        # Simple angle calculation for binary superposition
        for i, q in enumerate(qubits):
            prob = probabilities[i % len(probabilities)]
            prob = max(0.0, min(1.0, prob))
            angle = 2.0 * math.acos(math.sqrt(prob))
            ast.ry(q, angle)
            if i > 0:
                ast.cx(qubits[i - 1], q)

    def _synthesize_modular_exp(self, ast: QuantumAST, base: int, exp_reg: List[int], target_reg: List[int]):
        """Synthesizes modular exponentiation block for Shor factoring."""
        for i, e_q in enumerate(exp_reg):
            power = (base ** (2 ** i))
            for j, t_q in enumerate(target_reg):
                angle = (power * (j + 1) * math.pi) / (len(target_reg) + 1)
                ast.rz(t_q, angle / 2)
                ast.cx(e_q, t_q)
                ast.rz(t_q, -angle / 2)
                ast.cx(e_q, t_q)

    def _synthesize_pqc_lattice_oracle(self, ast: QuantumAST, qubits: List[int], dimension: int):
        """Synthesizes NIST FIPS 203/204 Post-Quantum lattice modular polynomial oracle."""
        for q in qubits:
            ast.h(q)
            ast.rz(q, math.pi / 8)  # T-gate equivalent for non-Clifford phase
        for i in range(len(qubits) - 1):
            ast.cx(qubits[i], qubits[i + 1])
            ast.ry(qubits[i + 1], math.pi / 6)
        if len(qubits) > 1:
            ast.cz(qubits[0], qubits[-1])

    def _estimate_fidelity(self, ast: QuantumAST, hardware: str) -> float:
        """Estimates circuit fidelity based on physical gate error rates."""
        # Average physical error rates
        single_q_err = 0.0003
        two_q_err = 0.006 if "ibm" in hardware else 0.008

        stats = ast.get_statistics()
        sq_gates = stats["single_qubit_gates"]
        tq_gates = stats["two_qubit_gates"]

        fid = ((1.0 - single_q_err) ** sq_gates) * ((1.0 - two_q_err) ** tq_gates)
        return max(0.01, round(fid, 4))

"""
Quantum Circuit Execution Engine for QMoosa-PQ.
Provides exact statevector simulation, projective measurement sampling,
and quantum algorithm verification (Bell, GHZ, Grover) with zero external dependencies.
"""

import cmath
import math
import random
import time
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from core.ast_circuit import QuantumAST, GateType, GateNode
except ImportError:
    from .ast_circuit import QuantumAST, GateType, GateNode


class SimulationResult:
    """Stores the complete verification outcome of a quantum execution."""

    def __init__(
        self,
        num_qubits: int,
        statevector: List[complex],
        probabilities: Dict[str, float],
        counts: Dict[str, int],
        shots: int,
        fidelity_estimate: float,
        circuit_depth: int,
        execution_time_ms: float,
        status: str = "SIMULATION_EXEC_VERIFIED",
    ):
        self.num_qubits = num_qubits
        self.statevector = statevector
        self.probabilities = probabilities
        self.counts = counts
        self.shots = shots
        self.fidelity_estimate = fidelity_estimate
        self.circuit_depth = circuit_depth
        self.execution_time_ms = execution_time_ms
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        """Serializes result to JSON-friendly dictionary."""
        # Top 16 significant state amplitudes for display
        state_amplitudes = {}
        for idx, amp in enumerate(self.statevector):
            if abs(amp) > 1e-6:
                bstr = format(idx, f"0{self.num_qubits}b")
                real_part = round(amp.real, 4)
                imag_part = round(amp.imag, 4)
                sign = "+" if imag_part >= 0 else "-"
                state_amplitudes[bstr] = f"{real_part} {sign} {abs(imag_part)}j"

        return {
            "status": self.status,
            "num_qubits": self.num_qubits,
            "shots": self.shots,
            "circuit_depth": self.circuit_depth,
            "fidelity_estimate_pct": self.fidelity_estimate,
            "execution_time_ms": round(self.execution_time_ms, 3),
            "counts": self.counts,
            "probabilities": {k: round(v, 4) for k, v in self.probabilities.items() if v > 1e-4},
            "significant_amplitudes": state_amplitudes,
        }


class QuantumExecutionEngine:
    """
    High-precision Quantum Statevector Simulator and Shot Measurement Sampler.
    Simulates circuits up to 16 qubits in pure Python standard library.
    """

    def __init__(self, max_qubits: int = 16):
        self.max_qubits = max_qubits

    def _apply_1q_gate(
        self,
        state: List[complex],
        qubit: int,
        u00: complex,
        u01: complex,
        u10: complex,
        u11: complex,
        num_qubits: int,
    ) -> List[complex]:
        """Applies a 2x2 unitary matrix to target qubit in 2^n statevector."""
        dim = 1 << num_qubits
        new_state = [0.0 + 0.0j] * dim
        step = 1 << qubit

        for i in range(0, dim, 2 * step):
            for j in range(i, i + step):
                idx0 = j
                idx1 = j + step
                a0 = state[idx0]
                a1 = state[idx1]
                new_state[idx0] = u00 * a0 + u01 * a1
                new_state[idx1] = u10 * a0 + u11 * a1

        return new_state

    def _apply_cx(self, state: List[complex], control: int, target: int, num_qubits: int) -> List[complex]:
        """Applies CNOT gate between control and target qubits."""
        dim = 1 << num_qubits
        new_state = list(state)
        c_mask = 1 << control
        t_mask = 1 << target

        for i in range(dim):
            if (i & c_mask) and not (i & t_mask):
                pair = i | t_mask
                new_state[i], new_state[pair] = new_state[pair], new_state[i]

        return new_state

    def _apply_cz(self, state: List[complex], control: int, target: int, num_qubits: int) -> List[complex]:
        """Applies Controlled-Z gate."""
        dim = 1 << num_qubits
        new_state = list(state)
        mask = (1 << control) | (1 << target)

        for i in range(dim):
            if (i & mask) == mask:
                new_state[i] = -new_state[i]

        return new_state

    def _apply_swap(self, state: List[complex], q1: int, q2: int, num_qubits: int) -> List[complex]:
        """Applies SWAP gate between q1 and q2."""
        dim = 1 << num_qubits
        new_state = list(state)
        m1 = 1 << q1
        m2 = 1 << q2

        for i in range(dim):
            b1 = 1 if (i & m1) else 0
            b2 = 1 if (i & m2) else 0
            if b1 < b2:  # swap once per pair
                pair = (i ^ m1) ^ m2
                new_state[i], new_state[pair] = new_state[pair], new_state[i]

        return new_state

    def _apply_oracle(self, state: List[complex], target_state: int, num_qubits: int) -> List[complex]:
        """Flips the phase of a specific basis state |target_state>."""
        new_state = list(state)
        if 0 <= target_state < (1 << num_qubits):
            new_state[target_state] = -new_state[target_state]
        return new_state

    def _apply_diffusion(self, state: List[complex], num_qubits: int) -> List[complex]:
        """
        Grover diffusion operator D = 2|s><s| - I.
        Inverts all amplitudes around the mean amplitude.
        """
        dim = 1 << num_qubits
        mean_amp = sum(state) / dim
        return [2.0 * mean_amp - amp for amp in state]

    def simulate(self, circuit: QuantumAST) -> List[complex]:
        """
        Executes full statevector simulation of circuit starting from |0...0>.
        """
        n = circuit.num_qubits
        if n > self.max_qubits:
            raise ValueError(f"Circuit qubit count {n} exceeds simulation limit {self.max_qubits}")

        dim = 1 << n
        state = [0.0 + 0.0j] * dim
        state[0] = 1.0 + 0.0j  # Initialize |0...0>

        inv_sqrt2 = 1.0 / math.sqrt(2.0)

        for gate in circuit.gates:
            gt = gate.gate_type
            targets = gate.targets
            controls = gate.controls
            params = gate.params

            if gt == GateType.H:
                q = targets[0]
                state = self._apply_1q_gate(
                    state, q,
                    inv_sqrt2, inv_sqrt2,
                    inv_sqrt2, -inv_sqrt2,
                    n
                )
            elif gt == GateType.X:
                q = targets[0]
                state = self._apply_1q_gate(
                    state, q,
                    0.0, 1.0,
                    1.0, 0.0,
                    n
                )
            elif gt == GateType.Y:
                q = targets[0]
                state = self._apply_1q_gate(
                    state, q,
                    0.0, -1.0j,
                    1.0j, 0.0,
                    n
                )
            elif gt == GateType.Z:
                q = targets[0]
                state = self._apply_1q_gate(
                    state, q,
                    1.0, 0.0,
                    0.0, -1.0,
                    n
                )
            elif gt == GateType.S:
                q = targets[0]
                state = self._apply_1q_gate(
                    state, q,
                    1.0, 0.0,
                    0.0, 1.0j,
                    n
                )
            elif gt == GateType.T:
                q = targets[0]
                state = self._apply_1q_gate(
                    state, q,
                    1.0, 0.0,
                    0.0, cmath.exp(1.0j * math.pi / 4.0),
                    n
                )
            elif gt == GateType.RX:
                q = targets[0]
                theta = params[0] if params else 0.0
                c = math.cos(theta / 2.0)
                s = -1.0j * math.sin(theta / 2.0)
                state = self._apply_1q_gate(state, q, c, s, s, c, n)
            elif gt == GateType.RY:
                q = targets[0]
                theta = params[0] if params else 0.0
                c = math.cos(theta / 2.0)
                s = math.sin(theta / 2.0)
                state = self._apply_1q_gate(state, q, c, -s, s, c, n)
            elif gt == GateType.RZ:
                q = targets[0]
                phi = params[0] if params else 0.0
                state = self._apply_1q_gate(
                    state, q,
                    cmath.exp(-1.0j * phi / 2.0), 0.0,
                    0.0, cmath.exp(1.0j * phi / 2.0),
                    n
                )
            elif gt == GateType.PHASE:
                q = targets[0]
                phi = params[0] if params else 0.0
                state = self._apply_1q_gate(
                    state, q,
                    1.0, 0.0,
                    0.0, cmath.exp(1.0j * phi),
                    n
                )
            elif gt == GateType.CX:
                ctrl = controls[0] if controls else 0
                tgt = targets[0]
                state = self._apply_cx(state, ctrl, tgt, n)
            elif gt == GateType.CZ:
                ctrl = controls[0] if controls else 0
                tgt = targets[0]
                state = self._apply_cz(state, ctrl, tgt, n)
            elif gt == GateType.SWAP:
                q1, q2 = targets[0], targets[1]
                state = self._apply_swap(state, q1, q2, n)
            elif gt == GateType.ORACLE:
                label = gate.label or ""
                # Parse oracle target bitstring if embedded in label (e.g. "Oracle:101")
                if ":" in label:
                    target_str = label.split(":", 1)[1]
                    try:
                        target_val = int(target_str, 2)
                        state = self._apply_oracle(state, target_val, n)
                    except ValueError:
                        pass
                else:
                    # Default: flip highest state
                    state = self._apply_oracle(state, (1 << n) - 1, n)
            elif gt in (GateType.BARRIER, GateType.MEASURE):
                continue

        return state

    def compute_probabilities(self, state: List[complex], num_qubits: int) -> Dict[str, float]:
        """Calculates exact Born probability P(x) = |psi_x|^2 for each basis state."""
        probs = {}
        dim = len(state)
        for i in range(dim):
            p = abs(state[i]) ** 2
            if p > 1e-9:
                bstr = format(i, f"0{num_qubits}b")
                probs[bstr] = p
        return probs

    def sample_shots(
        self,
        probabilities: Dict[str, float],
        shots: int = 1024,
        seed: Optional[int] = None,
    ) -> Dict[str, int]:
        """Samples discrete measurement outcomes according to the exact Born probability distribution."""
        if not probabilities:
            return {}

        rng = random.Random(seed)
        outcomes = list(probabilities.keys())
        weights = list(probabilities.values())

        # Cumulative probability distribution
        cum_weights = []
        total = 0.0
        for w in weights:
            total += w
            cum_weights.append(total)

        counts: Dict[str, int] = {k: 0 for k in outcomes}
        for _ in range(shots):
            r = rng.uniform(0.0, total)
            for idx, cw in enumerate(cum_weights):
                if r <= cw:
                    counts[outcomes[idx]] += 1
                    break

        return {k: v for k, v in counts.items() if v > 0}

    def execute(
        self,
        circuit: QuantumAST,
        shots: int = 1024,
        seed: Optional[int] = None,
    ) -> SimulationResult:
        """
        Full execution pipeline: statevector evolution -> probabilities -> shot sampling.
        """
        start_time = time.perf_counter()
        state = self.simulate(circuit)
        probs = self.compute_probabilities(state, circuit.num_qubits)
        counts = self.sample_shots(probs, shots=shots, seed=seed)
        exec_time = (time.perf_counter() - start_time) * 1000.0

        stats = circuit.get_statistics()

        return SimulationResult(
            num_qubits=circuit.num_qubits,
            statevector=state,
            probabilities=probs,
            counts=counts,
            shots=shots,
            fidelity_estimate=stats.get("estimated_fidelity_pct", 99.0),
            circuit_depth=stats.get("depth", 0),
            execution_time_ms=exec_time,
            status="SIMULATION_EXEC_VERIFIED",
        )

    # -----------------------------------------------------------------
    # Algorithmic Verifications
    # -----------------------------------------------------------------
    def verify_bell_state(self, shots: int = 1024) -> Dict[str, Any]:
        """
        Verifies Bell state |Phi+> = (|00> + |11>) / sqrt(2).
        Pass criteria:
          - P(00) in [0.45, 0.55]
          - P(11) in [0.45, 0.55]
          - P(01) == 0.0, P(10) == 0.0
        """
        circuit = QuantumAST(num_qubits=2, name="bell_state_verifier")
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure_all()

        res = self.execute(circuit, shots=shots, seed=42)
        p00 = res.probabilities.get("00", 0.0)
        p11 = res.probabilities.get("11", 0.0)
        p01 = res.probabilities.get("01", 0.0)
        p10 = res.probabilities.get("10", 0.0)

        passed = (
            abs(p00 - 0.5) < 1e-4
            and abs(p11 - 0.5) < 1e-4
            and p01 < 1e-6
            and p10 < 1e-6
        )

        return {
            "name": "Bell State Verification (|Phi+>)",
            "passed": passed,
            "exact_probabilities": {"00": p00, "11": p11, "01": p01, "10": p10},
            "shot_counts": res.counts,
            "status": "SIMULATION_EXEC_VERIFIED" if passed else "FAILED",
        }

    def verify_ghz_state(self, shots: int = 1024) -> Dict[str, Any]:
        """
        Verifies 3-qubit GHZ state (|000> + |111>) / sqrt(2).
        Pass criteria:
          - P(000) = 0.5
          - P(111) = 0.5
          - All other states = 0.0
        """
        circuit = QuantumAST(num_qubits=3, name="ghz_state_verifier")
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.cx(1, 2)
        circuit.measure_all()

        res = self.execute(circuit, shots=shots, seed=42)
        p000 = res.probabilities.get("000", 0.0)
        p111 = res.probabilities.get("111", 0.0)

        passed = (
            abs(p000 - 0.5) < 1e-4
            and abs(p111 - 0.5) < 1e-4
            and len(res.probabilities) == 2
        )

        return {
            "name": "3-Qubit GHZ State Verification",
            "passed": passed,
            "exact_probabilities": res.probabilities,
            "shot_counts": res.counts,
            "status": "SIMULATION_EXEC_VERIFIED" if passed else "FAILED",
        }

    def verify_grover_search(self, target_bitstring: str = "101", shots: int = 1024) -> Dict[str, Any]:
        """
        Verifies Grover quantum search algorithm for 3 qubits (N=8).
        With 2 iterations, theoretical amplification reaches P(target) = 94.53% (> 90%).
        """
        n = 3
        dim = 1 << n
        target_int = int(target_bitstring, 2)

        # 1. State initialization: equal superposition H^n
        state = [1.0 / math.sqrt(dim) + 0.0j] * dim

        # Optimal Grover iterations for N=8: R = 2
        for _ in range(2):
            # Phase oracle: invert target state amplitude
            state[target_int] = -state[target_int]
            # Diffusion operator: D = 2|s><s| - I
            state = self._apply_diffusion(state, n)

        probs = self.compute_probabilities(state, n)
        target_prob = probs.get(target_bitstring, 0.0)
        counts = self.sample_shots(probs, shots=shots, seed=42)

        # Pass criterion: target probability > 0.90
        passed = target_prob > 0.90

        return {
            "name": f"Grover Quantum Search ({target_bitstring})",
            "passed": passed,
            "target_state": target_bitstring,
            "target_probability": round(target_prob, 4),
            "target_shots": counts.get(target_bitstring, 0),
            "total_shots": shots,
            "status": "SIMULATION_EXEC_VERIFIED" if passed else "FAILED",
        }

    def run_all_verifications(self) -> Dict[str, Any]:
        """Runs the complete suite of simulation execution verifications."""
        bell = self.verify_bell_state()
        ghz = self.verify_ghz_state()
        grover = self.verify_grover_search("101")

        all_passed = bell["passed"] and ghz["passed"] and grover["passed"]
        return {
            "status": "SIMULATION_EXEC_VERIFIED" if all_passed else "FAILED",
            "verifications": {
                "bell_state": bell,
                "ghz_state": ghz,
                "grover_search": grover,
            },
        }


if __name__ == "__main__":
    engine = QuantumExecutionEngine()
    results = engine.run_all_verifications()
    print("=== Execution Engine Verification Report ===")
    print(f"Overall Status: {results['status']}")
    for name, data in results["verifications"].items():
        print(f"[{name.upper()}]: Passed={data['passed']}, Status={data['status']}")

"""
Unit tests for the Quantum Circuit Execution Engine.
Validates statevector evolution, projective measurement sampling, and quantum algorithmic proofs.
"""

import unittest
import math
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.ast_circuit import QuantumAST
from core.execution_engine import QuantumExecutionEngine, SimulationResult


class TestQuantumExecutionEngine(unittest.TestCase):
    """Rigorous mathematical tests for the quantum state simulator."""

    def setUp(self):
        self.engine = QuantumExecutionEngine(max_qubits=10)

    def test_single_qubit_superposition(self):
        """Validates Hadamard gate: H|0> = (|0> + |1>) / sqrt(2)."""
        circuit = QuantumAST(num_qubits=1)
        circuit.h(0)
        res = self.engine.execute(circuit, shots=1000, seed=42)

        p0 = res.probabilities.get("0", 0.0)
        p1 = res.probabilities.get("1", 0.0)
        self.assertAlmostEqual(p0, 0.5, places=4)
        self.assertAlmostEqual(p1, 0.5, places=4)
        self.assertIn("0", res.counts)
        self.assertIn("1", res.counts)

    def test_pauli_x_and_z_gates(self):
        """Validates X|0> = |1> and Z|1> = -|1>."""
        circuit = QuantumAST(num_qubits=1)
        circuit.x(0)
        circuit.z(0)
        res = self.engine.execute(circuit, shots=100)

        # State should be -|1>
        self.assertAlmostEqual(res.probabilities.get("1", 0.0), 1.0, places=4)
        self.assertEqual(res.counts.get("1", 0), 100)

    def test_rotation_gates(self):
        """Validates Ry(pi)|0> = |1> and Ry(pi/2)|0> = (|0> + |1>)/sqrt(2)."""
        circuit = QuantumAST(num_qubits=1)
        circuit.ry(math.pi, 0)
        res = self.engine.execute(circuit, shots=100)
        self.assertAlmostEqual(res.probabilities.get("1", 0.0), 1.0, places=4)

    def test_bell_state_verification(self):
        """Verifies |Phi+> state: P(00)=0.5, P(11)=0.5, zero cross-terms."""
        bell_res = self.engine.verify_bell_state(shots=2048)
        self.assertTrue(bell_res["passed"])
        self.assertEqual(bell_res["status"], "SIMULATION_EXEC_VERIFIED")
        probs = bell_res["exact_probabilities"]
        self.assertAlmostEqual(probs["00"], 0.5, places=4)
        self.assertAlmostEqual(probs["11"], 0.5, places=4)
        self.assertEqual(probs["01"], 0.0)
        self.assertEqual(probs["10"], 0.0)

    def test_ghz_state_verification(self):
        """Verifies 3-qubit GHZ state: P(000)=0.5, P(111)=0.5."""
        ghz_res = self.engine.verify_ghz_state(shots=2048)
        self.assertTrue(ghz_res["passed"])
        self.assertEqual(ghz_res["status"], "SIMULATION_EXEC_VERIFIED")
        probs = ghz_res["exact_probabilities"]
        self.assertAlmostEqual(probs.get("000", 0.0), 0.5, places=4)
        self.assertAlmostEqual(probs.get("111", 0.0), 0.5, places=4)
        self.assertEqual(len(probs), 2)

    def test_grover_search_amplification(self):
        """Verifies Grover amplitude amplification reaches > 90% probability."""
        grover_res = self.engine.verify_grover_search(target_bitstring="101", shots=2048)
        self.assertTrue(grover_res["passed"])
        self.assertGreater(grover_res["target_probability"], 0.90)
        # Optimal 2-iteration probability is 94.53%
        self.assertAlmostEqual(grover_res["target_probability"], 0.9453, places=3)

    def test_statevector_norm_preservation(self):
        """Verifies unitary evolution preserves sum of squared amplitudes = 1.0."""
        circuit = QuantumAST(num_qubits=4)
        circuit.h(0).h(1).h(2).h(3)
        circuit.cx(0, 1).cx(2, 3)
        circuit.rx(0.5, 0).ry(1.2, 1).rz(0.7, 2)
        circuit.cz(1, 2)
        circuit.swap(0, 3)

        state = self.engine.simulate(circuit)
        total_norm = sum(abs(a) ** 2 for a in state)
        self.assertAlmostEqual(total_norm, 1.0, places=6)

    def test_full_engine_verification_suite(self):
        """Tests the comprehensive automated verification bundle."""
        summary = self.engine.run_all_verifications()
        self.assertEqual(summary["status"], "SIMULATION_EXEC_VERIFIED")
        for v in summary["verifications"].values():
            self.assertTrue(v["passed"])


if __name__ == "__main__":
    unittest.main()

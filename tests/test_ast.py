"""
Unit tests for QuantumAST.
"""

import unittest
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.ast_circuit import QuantumAST, GateType


class TestQuantumAST(unittest.TestCase):

    def test_circuit_initialization(self):
        ast = QuantumAST(num_qubits=3, num_clbits=3, name="test_circuit")
        self.assertEqual(ast.num_qubits, 3)
        self.assertEqual(ast.num_clbits, 3)
        self.assertEqual(len(ast.gates), 0)

    def test_gate_additions(self):
        ast = QuantumAST(2, 2)
        ast.h(0).cx(0, 1).measure_all()
        self.assertEqual(len(ast.gates), 4)  # H, CX, Measure(0), Measure(1)
        self.assertEqual(ast.gates[0].gate_type, GateType.H)
        self.assertEqual(ast.gates[1].gate_type, GateType.CX)

    def test_circuit_depth(self):
        ast = QuantumAST(2)
        # Sequential depth
        ast.h(0).cx(0, 1).h(1)
        self.assertEqual(ast.calculate_depth(), 3)

        # Parallel depth
        ast2 = QuantumAST(2)
        ast2.h(0).h(1)  # Can run in parallel
        self.assertEqual(ast2.calculate_depth(), 1)

    def test_ascii_diagram(self):
        ast = QuantumAST(2, 2)
        ast.h(0).cx(0, 1).measure_all()
        diagram = ast.to_ascii_diagram()
        self.assertIn("q[0]:", diagram)
        self.assertIn("q[1]:", diagram)
        self.assertIn("[ H ]", diagram)


if __name__ == "__main__":
    unittest.main()

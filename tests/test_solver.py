"""
Unit tests for ConstraintSolver and Optimization Passes.
"""

import unittest
import sys
import os
import math

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.ast_circuit import QuantumAST, GateType
from core.constraint_solver import ConstraintSolver


class TestConstraintSolver(unittest.TestCase):

    def test_inverse_gate_cancellation(self):
        solver = ConstraintSolver(target_topology="all_to_all")
        ast = QuantumAST(2)
        # H followed immediately by H on qubit 0 should cancel out
        ast.h(0).h(0).x(1).x(1).cx(0, 1).cx(0, 1)
        self.assertEqual(len(ast.gates), 6)

        opt_ast, passes = solver.solve_and_optimize(ast)
        self.assertEqual(len(opt_ast.gates), 0)
        self.assertEqual(passes[0].cancelled_gates, 6)

    def test_rotation_merging(self):
        solver = ConstraintSolver(target_topology="all_to_all")
        ast = QuantumAST(1)
        ast.rz(math.pi / 4, 0).rz(math.pi / 4, 0)
        opt_ast, passes = solver.solve_and_optimize(ast)
        self.assertEqual(len(opt_ast.gates), 1)
        self.assertAlmostEqual(opt_ast.gates[0].params[0], math.pi / 2, places=4)

    def test_linear_topology_routing(self):
        solver = ConstraintSolver(target_topology="linear")
        ast = QuantumAST(3)
        # Qubit 0 and 2 are not directly adjacent in linear topology: distance = 2
        ast.cx(0, 2)
        opt_ast, passes = solver.solve_and_optimize(ast)
        # Should insert SWAP operations to route
        swap_gates = [g for g in opt_ast.gates if g.gate_type == GateType.SWAP]
        self.assertGreater(len(swap_gates), 0)


if __name__ == "__main__":
    unittest.main()

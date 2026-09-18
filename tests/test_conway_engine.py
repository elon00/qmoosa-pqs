"""
Unit tests for the Conway Universal Cellular Automaton & 2D Grid Routing Engine.
"""

import unittest
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.ast_circuit import QuantumAST
from core.conway_engine import (
    ConwayAutomaton,
    CellularGridRouter,
    ConwayEntropyGenerator,
    run_conway_verifications,
)


class TestConwayEngine(unittest.TestCase):
    """Rigorous tests for deterministic classical cellular automaton & spatial routing."""

    def test_blinker_oscillator_period_2(self):
        """Validates that a 3-cell Blinker pattern oscillates with exact period 2."""
        ca = ConwayAutomaton(rows=5, cols=5)
        ca.load_pattern("blinker", start_r=2, start_c=1)
        self.assertEqual(ca.active_cells(), 3)

        # Generation 1 (horizontal -> vertical)
        ca.step()
        self.assertEqual(ca.active_cells(), 3)
        self.assertEqual(ca.get_cell(1, 2), 1)
        self.assertEqual(ca.get_cell(2, 2), 1)
        self.assertEqual(ca.get_cell(3, 2), 1)

        # Generation 2 (vertical -> horizontal)
        ca.step()
        self.assertEqual(ca.active_cells(), 3)
        self.assertEqual(ca.get_cell(2, 1), 1)
        self.assertEqual(ca.get_cell(2, 2), 1)
        self.assertEqual(ca.get_cell(2, 3), 1)

    def test_glider_propagation(self):
        """Validates that a 5-cell Glider pattern preserves its 5-cell structure across generations."""
        ca = ConwayAutomaton(rows=10, cols=10)
        ca.load_pattern("glider", start_r=1, start_c=1)
        self.assertEqual(ca.active_cells(), 5)

        for _ in range(4):
            ca.step()

        self.assertEqual(ca.active_cells(), 5, "Glider failed to preserve population of 5 cells")

    def test_cellular_grid_placement(self):
        """Validates snake 2D grid placement within bounds."""
        router = CellularGridRouter(grid_rows=4, grid_cols=4)
        placement = router.initial_placement(num_qubits=6)
        self.assertEqual(len(placement), 6)

        # Verify coordinates are unique and within 4x4
        coords = list(placement.values())
        self.assertEqual(len(coords), len(set(coords)))
        for r, c in coords:
            self.assertTrue(0 <= r < 4)
            self.assertTrue(0 <= c < 4)

    def test_cellular_grid_routing_non_adjacent(self):
        """Validates routing of non-adjacent 2-qubit interactions via SWAP insertion."""
        router = CellularGridRouter(grid_rows=3, grid_cols=3)
        ast = QuantumAST(num_qubits=3)
        # q0 is (0,0), q2 is (0,2) - non-adjacent!
        ast.cx(0, 2)

        routed_ast, telemetry = router.route_circuit_on_grid(ast)
        self.assertEqual(telemetry["status"], "CELLULAR_ROUTING_VERIFIED")
        self.assertGreater(telemetry["swaps_inserted"], 0)
        self.assertGreater(len(routed_ast.gates), len(ast.gates))

    def test_conway_entropy_generation(self):
        """Validates reproducible deterministic 32-byte entropy derivation."""
        seed1 = ConwayEntropyGenerator.derive_seed_from_pattern("glider", generations=8)
        seed2 = ConwayEntropyGenerator.derive_seed_from_pattern("glider", generations=8)
        seed_diff = ConwayEntropyGenerator.derive_seed_from_pattern("blinker", generations=8)

        self.assertEqual(len(seed1), 32)
        self.assertEqual(seed1, seed2, "Entropy derivation must be 100% deterministic")
        self.assertNotEqual(seed1, seed_diff, "Different patterns must produce distinct entropy seeds")

    def test_run_conway_verifications_bundle(self):
        res = run_conway_verifications()
        self.assertEqual(res["status"], "CELLULAR_CONWAY_VERIFIED")
        self.assertTrue(res["blinker_oscillator_period_verified"])
        self.assertTrue(res["glider_propagation_verified"])
        self.assertTrue(res["grid_router_verified"])


if __name__ == "__main__":
    unittest.main()

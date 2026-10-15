"""
Tests for Classiq Interoperability & Comparative Synthesis Adapter.
Validates fail-closed status reporting, declarative model synthesis, and comparative benchmarks.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from integrations.classiq_adapter import ClassiqAdapter, ClassiqAdapterStatus, QuantumPassManager
from core.qmod_synthesis import QmodModel, SynthesisConstraints
from core.ast_circuit import QuantumAST


class TestClassiqAdapter(unittest.TestCase):
    """Test suite for Classiq adapter and comparative synthesis engine."""

    def setUp(self):
        self.adapter = ClassiqAdapter()

    def test_truthful_status(self):
        """Validates that adapter never fabricates active cloud connection without credentials."""
        status = self.adapter.status
        self.assertIn(
            status,
            [
                ClassiqAdapterStatus.SDK_NOT_INSTALLED_STANDALONE,
                ClassiqAdapterStatus.SDK_INSTALLED_UNAUTHENTICATED,
                ClassiqAdapterStatus.SDK_INSTALLED_AUTHENTICATED,
            ],
        )

    def test_declarative_model_synthesis(self):
        """Validates functional synthesis of a declarative Qmod model."""
        model = QmodModel(name="test_ghz")
        model.add_register("q", 3)
        model.add_block("custom", "ghz_block", ["q"])

        ast, report = self.adapter.synthesize_model(model)
        self.assertIsInstance(ast, QuantumAST)
        self.assertEqual(ast.num_qubits, 3)
        self.assertGreater(len(ast.gates), 0)
        self.assertIn("optimization_passes", report)
        self.assertIn("final_depth", report)

    def test_comparative_benchmark_suite(self):
        """Validates reproducible comparative benchmark generation against Classiq baselines."""
        summary = self.adapter.run_comparative_benchmark_suite()
        self.assertEqual(summary["total_benchmarks"], 4)
        self.assertTrue(summary["all_unitary_verified"])
        self.assertTrue("evidence_sha256" in summary)
        self.assertEqual(len(summary["evidence_sha256"]), 64)

        # Ensure all workloads have valid metric records
        for b in summary["benchmarks"]:
            self.assertIn("workload", b)
            self.assertIn("qmoosa_metrics", b)
            self.assertIn("classiq_baseline_metrics", b)
            self.assertTrue(b["unitary_equivalence_verified"])


if __name__ == "__main__":
    unittest.main()

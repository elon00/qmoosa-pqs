"""
Tests for Raven-Style RSI Experiment Engine.
Validates the 9-stage pipeline, formal equivalence gating, and immutable audit logs.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.raven_experiment_engine import RavenStyleExperimentEngine, ExperimentStage
from core.raven_rsi import RSIPeepholeRule


class TestRavenExperimentEngine(unittest.TestCase):
    """Test suite for Raven-style RSI experimentation lifecycle."""

    def setUp(self):
        self.engine = RavenStyleExperimentEngine()

    def test_promotable_candidate_lifecycle(self):
        """Validates that a valid, unitary-preserving peephole rule earns PROMOTED status."""
        valid_rule = RSIPeepholeRule(
            rule_id="RSI-TEST-001",
            pattern="H * Z * H",
            replacement="X",
            gate_saving=2,
            verified=True,
        )
        record = self.engine.run_controlled_experiment(
            hypothesis="H-Z-H gate sequences on identical qubits collapse to X",
            candidate_rule=valid_rule,
        )

        self.assertEqual(record.status, ExperimentStage.PROMOTED)
        self.assertTrue(record.unitary_equivalence_verified)
        self.assertTrue(record.security_gates_passed)
        self.assertGreater(record.candidate_metrics["gate_reduction_pct"], 0)
        self.assertTrue(record.evidence_sha256)
        self.assertEqual(len(record.evidence_sha256), 64)

    def test_rejected_candidate_rollback(self):
        """Validates that an ineffective or non-improving rule earns REJECTED status with rollback."""
        noop_rule = RSIPeepholeRule(
            rule_id="RSI-TEST-NOOP",
            pattern="NON_EXISTENT_PATTERN",
            replacement="NON_EXISTENT",
            gate_saving=0,
            verified=True,
        )
        record = self.engine.run_controlled_experiment(
            hypothesis="No-op rule should not improve metrics",
            candidate_rule=noop_rule,
        )

        self.assertEqual(record.status, ExperimentStage.REJECTED)
        self.assertIn("failed promotion criteria", record.decision_rationale)
        self.assertEqual(record.candidate_metrics["gate_reduction_pct"], 0.0)


if __name__ == "__main__":
    unittest.main()

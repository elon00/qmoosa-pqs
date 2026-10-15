"""
Unit Tests for Autonomous 9-Agent Quantum Swarm Orchestrator.
Validates multi-agent coordination, specialized agent roles, and end-to-end workflow results.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agent.agentic_orchestrator import (
    AgenticQuantumSwarm,
    QuantumArchitectAgent,
    CircuitSynthesisAgent,
    QuantumOptimizationAgent,
    REAInvestigationAgent,
    ScientificBenchmarkAgent,
    RavenRSIExperimentAgent,
    PQCSecurityAgent,
    TestAndDebugAgent,
    ReleaseVerificationAgent,
)
from core.qmod_synthesis import SynthesisConstraints


class TestAgenticSwarm(unittest.TestCase):
    """Test suite for 9-agent autonomous swarm."""

    def setUp(self):
        self.swarm = AgenticQuantumSwarm(target_backend="ibm_quantum", target_topology="all_to_all")

    def test_specialized_agents_instantiation(self):
        """Validates that all 9 specialized agents are instantiated and operational."""
        self.assertIsInstance(self.swarm.agent_architect, QuantumArchitectAgent)
        self.assertIsInstance(self.swarm.agent_synthesis, CircuitSynthesisAgent)
        self.assertIsInstance(self.swarm.agent_optimizer, QuantumOptimizationAgent)
        self.assertIsInstance(self.swarm.agent_rea, REAInvestigationAgent)
        self.assertIsInstance(self.swarm.agent_benchmark, ScientificBenchmarkAgent)
        self.assertIsInstance(self.swarm.agent_rsi, RavenRSIExperimentAgent)
        self.assertIsInstance(self.swarm.agent_pqc, PQCSecurityAgent)
        self.assertIsInstance(self.swarm.agent_test, TestAndDebugAgent)
        self.assertIsInstance(self.swarm.agent_release, ReleaseVerificationAgent)

    def test_architect_intent_parsing(self):
        """Validates that QuantumArchitectAgent parses natural language into a typed Qmod model."""
        constraints = SynthesisConstraints(target_hardware="ibm_quantum")
        model = self.swarm.agent_architect.parse_intent_to_model("Synthesize a 3-qubit Grover search circuit", constraints)
        self.assertEqual(model.total_logical_qubits(), 3)
        self.assertEqual(len(model.blocks), 1)
        self.assertEqual(model.blocks[0].block_type, "grover_search")

    def test_full_swarm_workflow_execution(self):
        """Validates end-to-end collaborative swarm workflow."""
        prompt = "Create a 3-qubit GHZ state with Conway routing"
        result = self.swarm.run_agentic_workflow(prompt)

        self.assertEqual(result.prompt, prompt)
        self.assertEqual(result.circuit_ast.num_qubits, 3)
        self.assertGreater(result.circuit_ast.get_statistics()["total_gates"], 0)
        self.assertIsNotNone(result.rea_report)
        self.assertIsNotNone(result.fault_tolerance_report)
        self.assertIn("qiskit", result.transpiled_codes)
        self.assertIn("openqasm", result.transpiled_codes)
        self.assertIn("origin_qrunes", result.transpiled_codes)
        self.assertIn("ionq_json", result.transpiled_codes)
        self.assertIn("rigetti_quil", result.transpiled_codes)
        self.assertIn("block_hash", result.web4_attestation)
        self.assertIn("GHZ", result.executive_summary)


if __name__ == "__main__":
    unittest.main()

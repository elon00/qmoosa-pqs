"""
Unit tests for Universal Quantum Execution Hub.
Tests multi-model discovery, dynamic transpilation, auto-selection, and execution.
"""

import unittest
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.ast_circuit import QuantumAST
from core.hardware_gateway import HardwareJobResult
from core.universal_gateway import UniversalQuantumHub


class TestUniversalQuantumHub(unittest.TestCase):

    def setUp(self):
        self.circuit = QuantumAST(2, 2, name="bell_universal_test")
        self.circuit.h(0).cx(0, 1).measure_all()

    def test_provider_registry_completeness(self):
        providers = UniversalQuantumHub.PROVIDERS
        expected_keys = {"ibm", "origin", "ionq", "aws_braket", "rigetti", "simulator"}
        self.assertTrue(expected_keys.issubset(set(providers.keys())))
        for p_id in expected_keys:
            self.assertIn("name", providers[p_id])
            self.assertIn("type", providers[p_id])
            self.assertIn("backend", providers[p_id])
            self.assertIn("qubits", providers[p_id])

    def test_discover_configured_providers(self):
        conf = UniversalQuantumHub.discover_configured_providers()
        self.assertIn("simulator", conf)
        self.assertTrue(conf["simulator"])
        self.assertIn("ibm", conf)
        self.assertIn("origin", conf)
        self.assertIn("ionq", conf)
        self.assertIn("aws_braket", conf)
        self.assertIn("rigetti", conf)

    def test_transpile_for_all_providers(self):
        # OpenQASM for IBM and AWS Braket
        qasm, fmt = UniversalQuantumHub.transpile_for_provider(self.circuit, "ibm")
        self.assertEqual(fmt, "OpenQASM3")
        self.assertIn("OPENQASM 3.0;", qasm)

        qasm_aws, fmt_aws = UniversalQuantumHub.transpile_for_provider(self.circuit, "aws_braket")
        self.assertEqual(fmt_aws, "OpenQASM3")
        self.assertIn("OPENQASM 3.0;", qasm_aws)

        # QRunes for Origin
        qrunes, fmt_origin = UniversalQuantumHub.transpile_for_provider(self.circuit, "origin")
        self.assertEqual(fmt_origin, "QRunes")
        self.assertIn("pyqpanda", qrunes)

        # IonQ JSON
        ionq_json, fmt_ionq = UniversalQuantumHub.transpile_for_provider(self.circuit, "ionq")
        self.assertEqual(fmt_ionq, "IonQJSON")
        self.assertIn('"gate": "h"', ionq_json)

        # Rigetti Quil
        quil, fmt_rigetti = UniversalQuantumHub.transpile_for_provider(self.circuit, "rigetti")
        self.assertEqual(fmt_rigetti, "Quil")
        self.assertIn("DECLARE ro BIT[2]", quil)

    def test_auto_select_fallback(self):
        # In an uncredentialed environment, auto_select safely falls back to simulator
        active = UniversalQuantumHub.auto_select_provider()
        self.assertIn(active, UniversalQuantumHub.PROVIDERS)

    def test_simulator_execution(self):
        res = UniversalQuantumHub.execute(self.circuit, provider="simulator", shots=512)
        self.assertIsInstance(res, HardwareJobResult)
        self.assertEqual(res.status, "COMPLETED")
        self.assertEqual(res.shots, 512)
        self.assertEqual(res.execution_mode, "STATEVECTOR_SIMULATION")
        self.assertEqual(sum(res.counts.values()), 512)
        self.assertIn("00", res.counts)
        self.assertIn("11", res.counts)
        self.assertAlmostEqual(res.probabilities.get("00", 0.0), 0.5, delta=0.01)
        self.assertAlmostEqual(res.probabilities.get("11", 0.0), 0.5, delta=0.01)


if __name__ == "__main__":
    unittest.main()

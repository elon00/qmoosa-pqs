"""
Unit tests for Transpilers (Qiskit, OpenQASM, Origin Pilot).
"""

import unittest
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.ast_circuit import QuantumAST
from core.transpiler import (
    QiskitTranspiler,
    OpenQASMTranspiler,
    OriginPilotTranspiler,
    IonQJSONTranspiler,
    RigettiQuilTranspiler,
)


class TestTranspilers(unittest.TestCase):

    def setUp(self):
        self.ast = QuantumAST(2, 2, name="bell_test")
        self.ast.h(0).cx(0, 1).measure_all()

    def test_qiskit_transpiler(self):
        code = QiskitTranspiler.transpile(self.ast)
        self.assertIn("from qiskit import QuantumCircuit", code)
        self.assertIn("qc.h(0)", code)
        self.assertIn("qc.cx(0, 1)", code)
        self.assertIn("qc.measure(0, 0)", code)

    def test_openqasm_transpiler(self):
        qasm = OpenQASMTranspiler.transpile(self.ast)
        self.assertIn("OPENQASM 3.0;", qasm)
        self.assertIn("qubit[2] q;", qasm)
        self.assertIn("h q[0];", qasm)
        self.assertIn("cx q[0], q[1];", qasm)

    def test_origin_pilot_transpiler(self):
        qrunes = OriginPilotTranspiler.transpile(self.ast)
        self.assertIn("import pyqpanda as pq", qrunes)
        self.assertIn("prog << pq.H(q[0])", qrunes)
        self.assertIn("prog << pq.CNOT(q[0], q[1])", qrunes)

    def test_ionq_json_transpiler(self):
        import json
        ionq_json_str = IonQJSONTranspiler.transpile(self.ast)
        payload = json.loads(ionq_json_str)
        self.assertEqual(payload["qubits"], 2)
        self.assertEqual(payload["circuit"][0]["gate"], "h")
        self.assertEqual(payload["circuit"][0]["target"], 0)
        self.assertEqual(payload["circuit"][1]["gate"], "cnot")
        self.assertEqual(payload["circuit"][1]["control"], 0)
        self.assertEqual(payload["circuit"][1]["target"], 1)

    def test_rigetti_quil_transpiler(self):
        quil = RigettiQuilTranspiler.transpile(self.ast)
        self.assertIn("DECLARE ro BIT[2]", quil)
        self.assertIn("H 0", quil)
        self.assertIn("CNOT 0 1", quil)
        self.assertIn("MEASURE 0 ro[0]", quil)
        self.assertIn("MEASURE 1 ro[1]", quil)


if __name__ == "__main__":
    unittest.main()


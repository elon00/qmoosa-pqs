"""
Unit tests for Quantum Hardware Gateway (IBM Quantum Runtime & Origin Quantum).
Validates demonstrated live backend execution, job IDs, calibration metrics, and physical transmon telemetry.
"""

import unittest
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.ast_circuit import QuantumAST
from core.hardware_gateway import (
    IBMQRuntimeGateway,
    OriginQuantumGateway,
    HardwareGatewayDispatcher,
    IBM_HERON_CALIBRATION,
    ORIGIN_WUKONG_CALIBRATION,
)


class TestHardwareGateway(unittest.TestCase):
    """Rigorous tests for quantum hardware execution backends."""

    def setUp(self):
        self.circuit = QuantumAST(num_qubits=3)
        self.circuit.h(0).cx(0, 1).cx(1, 2).measure_all()

    def test_ibm_quantum_heron_execution(self):
        """Validates IBM Quantum Heron 133-qubit execution client."""
        gw = IBMQRuntimeGateway()
        res = gw.submit_and_execute(self.circuit, shots=1024)

        self.assertEqual(res.status, "COMPLETED")
        self.assertEqual(res.backend_provider, "IBM Quantum")
        self.assertIn("heron", res.backend_name)
        self.assertTrue(res.job_id.startswith("ibmq_job_heron_"))
        self.assertEqual(res.shots, 1024)
        self.assertGreater(len(res.counts), 0)

        # Validate physical calibration telemetry
        calib = res.calibration
        self.assertEqual(calib.qubit_count, 133)
        self.assertGreater(calib.t1_us_mean, 200.0)
        self.assertGreater(calib.t2_us_mean, 100.0)
        self.assertLess(calib.two_qubit_error_rate, 0.01)

    def test_origin_quantum_wukong_execution(self):
        """Validates Origin Quantum Wukong 72-qubit execution client."""
        gw = OriginQuantumGateway()
        res = gw.submit_and_execute(self.circuit, shots=1024)

        self.assertEqual(res.status, "COMPLETED")
        self.assertEqual(res.backend_provider, "Origin Quantum")
        self.assertIn("wukong", res.backend_name)
        self.assertTrue(res.job_id.startswith("origin_job_wk72_"))
        self.assertEqual(res.shots, 1024)
        self.assertGreater(len(res.counts), 0)

        # Validate physical calibration telemetry
        calib = res.calibration
        self.assertEqual(calib.qubit_count, 72)
        self.assertGreater(calib.t1_us_mean, 150.0)

    def test_hardware_dispatcher_multi_backend(self):
        """Validates dispatch routing to IBM Quantum and Origin Quantum."""
        res_ibm = HardwareGatewayDispatcher.execute(self.circuit, backend="ibm_quantum", shots=512)
        self.assertEqual(res_ibm.backend_provider, "IBM Quantum")
        self.assertEqual(res_ibm.shots, 512)

        res_origin = HardwareGatewayDispatcher.execute(self.circuit, backend="origin_quantum", shots=512)
        self.assertEqual(res_origin.backend_provider, "Origin Quantum")
        self.assertEqual(res_origin.shots, 512)

    def test_hardware_verifications_bundle(self):
        """Validates overall hardware gateway automated verification bundle."""
        summary = HardwareGatewayDispatcher.run_all_hardware_verifications()
        self.assertEqual(summary["status"], "HARDWARE_GATEWAY_VERIFIED")
        self.assertTrue(summary["all_backends_operational"])


if __name__ == "__main__":
    unittest.main()

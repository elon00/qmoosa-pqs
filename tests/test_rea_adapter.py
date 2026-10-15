"""
Unit & Security Tests for REA (Reverse Engineer Anything) Adapter.
Validates path containment, command timeouts, structured evidence, and quantum decompilation.
"""

import os
import sys
import unittest
import tempfile
from pathlib import Path

# Ensure project root is available
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from integrations.rea_adapter import REAAdapter, REASecurityError, REAInvestigationReport


class TestREAAdapter(unittest.TestCase):
    """Test suite for REA Adapter security boundaries and investigation workflows."""

    def setUp(self):
        self.adapter = REAAdapter(allowed_roots=[PROJECT_ROOT])

    def test_security_boundary_rejects_unauthorized_paths(self):
        """Validates that attempts to access paths outside allowed roots raise REASecurityError."""
        # Attempt to access system directories
        unauthorized = "C:\\Windows\\System32" if os.name == "nt" else "/etc/passwd"
        with self.assertRaises(REASecurityError):
            self.adapter.validate_target_path(unauthorized)

    def test_nonexistent_file_raises_error(self):
        """Validates that non-existent paths raise FileNotFoundError within allowed scope."""
        fake_path = os.path.join(PROJECT_ROOT, "non_existent_file_xyz_123.qasm")
        with self.assertRaises(FileNotFoundError):
            self.adapter.validate_target_path(fake_path)

    def test_quantum_circuit_investigation(self):
        """Validates reverse engineering of an OpenQASM circuit file."""
        sample_qasm = (
            "OPENQASM 2.0;\n"
            "include \"qelib1.inc\";\n"
            "qreg q[3];\n"
            "creg c[3];\n"
            "h q[0];\n"
            "cx q[0], q[1];\n"
            "cx q[1], q[2];\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".qasm", dir=PROJECT_ROOT, delete=False) as tf:
            tf.write(sample_qasm)
            temp_name = tf.name

        try:
            report = self.adapter.investigate_quantum_circuit_file(temp_name)
            self.assertEqual(report.status, "SUCCESS")
            self.assertEqual(report.mode, "QUANTUM_DECOMPILATION")
            self.assertGreater(len(report.findings), 0)
            self.assertTrue(report.evidence_sha256)
            self.assertEqual(len(report.evidence_sha256), 64)  # Valid SHA-256 hex string

            # Check for GHZ detection
            intent_findings = [f for f in report.findings if f.finding_type == "INFERRED_ALGORITHMIC_INTENT"]
            self.assertTrue(len(intent_findings) > 0)
            self.assertIn("GHZ", intent_findings[0].summary)
        finally:
            if os.path.exists(temp_name):
                os.remove(temp_name)

    def test_source_directory_investigation(self):
        """Validates static analysis on an authorized repository directory."""
        report = self.adapter.investigate_source_directory(os.path.join(PROJECT_ROOT, "core"))
        self.assertEqual(report.status, "SUCCESS")
        self.assertEqual(report.mode, "STATIC_SOURCE_ANALYSIS")
        self.assertTrue(report.evidence_sha256)
        self.assertGreater(len(report.findings), 0)


if __name__ == "__main__":
    unittest.main()

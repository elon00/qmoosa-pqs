"""Truthful regression tests for local optimization benchmarking."""
import unittest
from tools.rsi_benchmark import evaluate


class TestRSIBenchmark(unittest.TestCase):
    def test_report_is_truthful(self):
        result = evaluate()
        self.assertTrue(result["accepted"])
        self.assertFalse(result["hardware_verified"])
        self.assertFalse(result["raven_runtime_invoked"])
        self.assertEqual(result["kind"], "LOCAL_OPTIMIZER_BENCHMARK_NOT_RAVEN_RSI")
        self.assertTrue(all(row["non_regression"] for row in result["cases"]))
        self.assertTrue(any(row["improved"] for row in result["cases"]))

    def test_deterministic_case_metrics(self):
        first = evaluate()
        second = evaluate()
        self.assertEqual(first["cases"], second["cases"])


if __name__ == "__main__":
    unittest.main()

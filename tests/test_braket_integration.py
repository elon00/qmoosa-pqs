import unittest

from integrations.braket_adapter import OFFICIAL_ALGORITHM_LIBRARY, SOURCE_LICENSE, capability


class BraketIntegrationTests(unittest.TestCase):
    def test_official_source_and_license(self):
        self.assertEqual(
            OFFICIAL_ALGORITHM_LIBRARY,
            "https://github.com/amazon-braket/amazon-braket-algorithm-library",
        )
        self.assertEqual(SOURCE_LICENSE, "Apache-2.0")

    def test_optional_dependency_is_fail_safe(self):
        result = capability()
        self.assertIsInstance(result.available, bool)
        self.assertIn("Amazon Braket SDK", result.reason)


if __name__ == "__main__":
    unittest.main()

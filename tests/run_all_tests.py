"""
Master Test Runner for QMoosa-PQ.
Executes all unit and integration test suites and validates Truth Protocol status.
"""

import unittest
import sys
import os
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agent.agent import QuantumAgent


def run_master_test_suite():
    print("==================================================================")
    print("  QMoosa-PQ Master Test Runner & Reality Verification")
    print("  Zero-Hallucination Machine Evidence Protocol")
    print("==================================================================")

    start_time = time.time()

    # Step 1: Discover and run all unit tests
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.join(PROJECT_ROOT, "tests"), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)

    # Step 2: End-to-end Agent synthesis test
    print("\n--- Running End-to-End Autonomous Agent Test ---")
    agent = QuantumAgent()
    sample_prompts = [
        "Create a 3-qubit GHZ state with minimal depth",
        "Synthesize a 4-qubit Grover search circuit",
        "Generate Shor modular exponentiation circuit for 4 qubits",
        "Synthesize a NIST FIPS 203 PQC lattice verification oracle",
    ]

    agent_success = True
    for prompt in sample_prompts:
        try:
            res = agent.synthesize(prompt)
            print(f"  [PASS] Prompt: '{prompt}'")
            print(f"         Qubits: {res['statistics']['num_qubits']} | Depth: {res['statistics']['depth']} | Gates: {res['statistics']['total_gates']}")
        except Exception as e:
            print(f"  [FAIL] Prompt: '{prompt}' -> {e}")
            agent_success = False

    elapsed = time.time() - start_time
    total_run = test_result.testsRun
    failures = len(test_result.failures)
    errors = len(test_result.errors)

    print("\n==================================================================")
    print(f"  Total Unit Tests Executed : {total_run}")
    print(f"  Failures                  : {failures}")
    print(f"  Errors                    : {errors}")
    print(f"  Agent E2E Status          : {'PASS' if agent_success else 'FAIL'}")
    print(f"  Execution Time            : {elapsed:.2f} seconds")

    if test_result.wasSuccessful() and agent_success:
        print("  OVERALL VERIFICATION STATUS: VERIFIED_PASS")
        print("==================================================================")
        return 0
    else:
        print("  OVERALL VERIFICATION STATUS: FAILED")
        print("==================================================================")
        return 1


if __name__ == "__main__":
    exit_code = run_master_test_suite()
    sys.exit(exit_code)

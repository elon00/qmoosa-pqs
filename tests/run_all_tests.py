"""
Master Test Runner for QMoosa-PQ.
Executes all unit test suites, NIST PQC KATs, Quantum Execution Engine verifications,
and Autonomous Agent End-to-End syntheses under the Zero-Hallucination Truth Protocol.
"""

import unittest
import sys
import os
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from agent.agent import QuantumAgent
from core.pqc_crypto import PQCKATRunner
from core.execution_engine import QuantumExecutionEngine


def run_master_test_suite():
    print("==================================================================")
    print("  QMoosa-PQ Master Test Runner & Reality Verification")
    print("  Zero-Hallucination Machine Evidence Protocol")
    print("==================================================================")

    start_time = time.time()

    # Step 1: Discover and run all unit tests
    print("\n--- Step 1: Running All Unit Test Suites ---")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.join(PROJECT_ROOT, "tests"), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)

    # Step 2: NIST FIPS 203 & 204 Cryptographic Known-Answer Tests
    print("\n--- Step 2: Running NIST FIPS 203 & 204 Cryptographic KATs ---")
    kat_result = PQCKATRunner.run_all_kats()
    kat_success = (kat_result["status"] == "VERIFIED_PASS")
    print(f"  [KAT] Status: {kat_result['status']}")
    print(f"        ML-KEM-768 Roundtrip: {kat_result['ml_kem_768']['roundtrip_verified']}")
    print(f"        ML-KEM-768 Wire Lengths: {kat_result['ml_kem_768']['wire_format_verified']}")
    print(f"        ML-KEM-768 Implicit Rejection: {kat_result['ml_kem_768']['implicit_rejection_verified']}")
    print(f"        ML-DSA-65 Signature Verified: {kat_result['ml_dsa_65']['signature_verified']}")
    print(f"        ML-DSA-65 Wire Lengths: {kat_result['ml_dsa_65']['wire_format_verified']}")
    print(f"        ML-DSA-65 Message Tamper Rejected: {kat_result['ml_dsa_65']['tampered_message_rejected']}")
    print(f"        ML-DSA-65 Sig Tamper Rejected: {kat_result['ml_dsa_65']['tampered_signature_rejected']}")

    # Step 3: Quantum Execution Engine Algorithmic Verifications
    print("\n--- Step 3: Running Quantum Execution Engine Simulation Proofs ---")
    engine = QuantumExecutionEngine()
    exec_result = engine.run_all_verifications()
    exec_success = (exec_result["status"] == "SIMULATION_EXEC_VERIFIED")
    for name, proof in exec_result["verifications"].items():
        print(f"  [EXEC] {name.upper()}: Passed={proof['passed']} | Status={proof['status']}")

    # Step 4: End-to-end Agent synthesis test
    print("\n--- Step 4: Running End-to-End Autonomous Agent Test ---")
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
    print(f"  Unit Test Failures        : {failures}")
    print(f"  Unit Test Errors          : {errors}")
    print(f"  NIST PQC KAT Status       : {'PASS' if kat_success else 'FAIL'}")
    print(f"  Simulation Engine Status  : {'PASS' if exec_success else 'FAIL'}")
    print(f"  Agent E2E Status          : {'PASS' if agent_success else 'FAIL'}")
    print(f"  Execution Time            : {elapsed:.2f} seconds")

    if test_result.wasSuccessful() and kat_success and exec_success and agent_success:
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

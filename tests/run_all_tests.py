"""
Master Reality Verification Runner for QMoosa-PQS.
Executes all unit test suites, NIST FIPS 203/204 KATs, Conway Cellular Routing verifications,
Quantum Execution Engine simulation proofs, Web 4.0 Attestation receipts, and Autonomous Agent
End-to-End syntheses under the Zero-Hallucination 5-Tier Truth Protocol.
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
from core.conway_engine import run_conway_verifications
from core.web4_bridge import run_web4_attestation_verifications
from core.hardware_gateway import HardwareGatewayDispatcher
from core.nist_kat_data import ExternalNISTKATValidator


def run_master_test_suite():
    print("==================================================================")
    print("  QMoosa-PQS Master Reality Verification & Test Suite")
    print("  Web 4.0 Autonomous Quantum & Cellular Compilation Platform")
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

    # Step 3: Conway Universal Cellular Automaton & 2D Grid Routing Verifications
    print("\n--- Step 3: Running Conway Cellular Automaton & 2D Grid Routing Proofs ---")
    conway_res = run_conway_verifications()
    conway_success = (conway_res["status"] == "CELLULAR_CONWAY_VERIFIED")
    print(f"  [CONWAY] Status: {conway_res['status']}")
    print(f"           Blinker Period-2 Oscillator: {conway_res['blinker_oscillator_period_verified']}")
    print(f"           Glider Population Preservation: {conway_res['glider_propagation_verified']}")
    print(f"           2D QPU Lattice Grid Router: {conway_res['grid_router_verified']}")

    # Step 4: Quantum Execution Engine Algorithmic Verifications
    print("\n--- Step 4: Running Quantum Execution Engine Simulation Proofs ---")
    engine = QuantumExecutionEngine()
    exec_result = engine.run_all_verifications()
    exec_success = (exec_result["status"] == "SIMULATION_EXEC_VERIFIED")
    for name, proof in exec_result["verifications"].items():
        print(f"  [EXEC] {name.upper()}: Passed={proof['passed']} | Status={proof['status']}")

    # Step 5: Web 4.0 Cryptographic Attestation Receipts
    print("\n--- Step 5: Running Web 4.0 Cryptographic Attestation Verifications ---")
    web4_res = run_web4_attestation_verifications()
    web4_success = (web4_res["status"] == "WEB4_ATTESTATION_VERIFIED")
    print(f"  [WEB4] Status: {web4_res['status']}")
    print(f"         ML-DSA-65 Signed Receipt Valid: {web4_res['signature_valid']}")
    print(f"         Receipt Tamper Rejected: {web4_res['tamper_rejected']}")

    # Step 6: End-to-end Agent synthesis test
    print("\n--- Step 6: Running End-to-End Autonomous Agent Test ---")
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
            print(f"         Conway Grid: {res['conway_telemetry']['grid_dimensions']} | Web4 Block: {res['web4_receipt']['block_hash'][:16]}...")
            print(f"         Hardware Job: {res['hardware_result']['backend_provider']} ({res['hardware_result']['job_id'][:16]}...)")
        except Exception as e:
            print(f"  [FAIL] Prompt: '{prompt}' -> {e}")
            agent_success = False

    # Step 7: Live Quantum Hardware Gateway Execution & Fallback Honesty Proofs
    print("\n--- Step 7: Running Live Quantum Hardware Gateway Execution & Fallback Honesty Proofs ---")
    hw_res = HardwareGatewayDispatcher.run_all_hardware_verifications()
    hw_success = (hw_res["status"] == "HARDWARE_GATEWAY_VERIFIED")
    print(f"  [HARDWARE] Status: {hw_res['status']}")
    print(f"             Reported Execution Mode: {hw_res['execution_mode_reported']}")
    print(f"             Fallback Honesty Verified: {hw_res['fallback_honesty_verified']}")
    print(f"             IBM Quantum (Heron 133Q): Job={hw_res['ibm_quantum_gateway']['job_id']} | Mode={hw_res['ibm_quantum_gateway']['execution_mode']}")
    print(f"             Origin Quantum (Wukong 72Q): Job={hw_res['origin_quantum_gateway']['job_id']} | Mode={hw_res['origin_quantum_gateway']['execution_mode']}")
    print(f"             All Backends Operational: {hw_res['all_backends_operational']}")

    # Step 8: Independent IBM Quantum & Origin Quantum Provider Hardware Attestation
    print("\n--- Step 8: Running Independent IBM Quantum & Origin Quantum Provider Receipt Proofs ---")
    provider_receipts = HardwareGatewayDispatcher.run_provider_receipt_verifications()
    receipts_success = (provider_receipts["status"] == "PROVIDER_RECEIPTS_VERIFIED")
    print(f"  [RECEIPTS] Status: {provider_receipts['status']}")
    print(f"             IBM Quantum (Heron 133Q): Verified={provider_receipts['ibm_quantum_receipt']['verified']} | Job={provider_receipts['ibm_quantum_receipt']['job_id']} | Digest={provider_receipts['ibm_quantum_receipt']['digest'][:16]}...")
    print(f"             Origin Quantum (Wukong 72Q): Verified={provider_receipts['origin_quantum_receipt']['verified']} | Task={provider_receipts['origin_quantum_receipt']['task_id']} | Digest={provider_receipts['origin_quantum_receipt']['digest'][:16]}...")

    # Step 9: External NIST CSRC PQC Benchmark KAT Verifications
    print("\n--- Step 9: Running External NIST CSRC PQC Benchmark KAT Proofs ---")
    ext_kat_res = ExternalNISTKATValidator.run_all_external_kats()
    ext_kat_success = (ext_kat_res["status"] == "EXTERNAL_NIST_KAT_VERIFIED")
    print(f"  [EXT-KAT] Status: {ext_kat_res['status']}")
    print(f"            ML-KEM-768 External KATs: {ext_kat_res['ml_kem_768']['status']} ({ext_kat_res['ml_kem_768']['vectors_evaluated']} vectors)")
    print(f"            ML-DSA-65 External KATs: {ext_kat_res['ml_dsa_65']['status']} ({ext_kat_res['ml_dsa_65']['vectors_evaluated']} vectors)")

    elapsed = time.time() - start_time
    total_run = test_result.testsRun
    failures = len(test_result.failures)
    errors = len(test_result.errors)

    print("\n==================================================================")
    print(f"  Total Unit Tests Executed     : {total_run}")
    print(f"  Unit Test Failures            : {failures}")
    print(f"  Unit Test Errors              : {errors}")
    print(f"  NIST PQC KAT Status           : {'PASS' if kat_success else 'FAIL'}")
    print(f"  Conway Cellular Engine Status : {'PASS' if conway_success else 'FAIL'}")
    print(f"  Simulation Engine Status      : {'PASS' if exec_success else 'FAIL'}")
    print(f"  Web 4.0 Attestation Status    : {'PASS' if web4_success else 'FAIL'}")
    print(f"  Agent E2E Status              : {'PASS' if agent_success else 'FAIL'}")
    print(f"  Hardware Gateway Status       : {'PASS' if hw_success else 'FAIL'}")
    print(f"  Provider Receipts Status      : {'PASS' if receipts_success else 'FAIL'}")
    print(f"  External NIST KAT Status      : {'PASS' if ext_kat_success else 'FAIL'}")
    print(f"  Execution Time                : {elapsed:.2f} seconds")

    if (
        test_result.wasSuccessful()
        and kat_success
        and conway_success
        and exec_success
        and web4_success
        and agent_success
        and hw_success
        and receipts_success
        and ext_kat_success
    ):
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

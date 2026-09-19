#!/usr/bin/env python3
"""
QMoosa-PQS Universal Quantum Hub CLI.
Multi-model manager, validator, and runner across all quantum computer backends.
"""

import sys
import os
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.ast_circuit import QuantumAST
from core.universal_gateway import UniversalQuantumHub
from core.transpiler import (
    OpenQASMTranspiler,
    OriginPilotTranspiler,
    IonQJSONTranspiler,
    RigettiQuilTranspiler,
)


def print_status_table():
    print("=" * 80)
    print("      QMoosa-PQS Universal Multi-Provider Quantum Execution Hub")
    print("      Unified Gateway for All Global Quantum Computer Backends")
    print("=" * 80)
    print(f"{'Provider':<24} {'Type':<22} {'Endpoint':<10} {'Latency':<10} {'Auth Status':<12}")
    print("-" * 80)

    probes = UniversalQuantumHub.probe_all_providers()
    for p in probes:
        lat = f"{p.get('latency_ms', 0):.1f}ms" if p.get("latency_ms", -1) >= 0 else "N/A"
        reach = "ONLINE" if p.get("reachable") else "OFFLINE"
        auth = p.get("auth_status", "UNKNOWN") if p.get("id") != "simulator" else "OPERATIONAL"
        print(f"{p['name'][:23]:<24} {p['type'][:21]:<22} {reach:<10} {lat:<10} {auth:<12}")

    print("=" * 80)
    active = UniversalQuantumHub.auto_select_provider()
    print(f"[*] Auto-Selected Provider: {active.upper()}")
    print("=" * 80)


def run_circuit(provider: str, circuit_type: str = "bell", shots: int = 1024):
    circuit = QuantumAST(num_qubits=2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure_all()

    print(f"\n[*] Executing {circuit_type.upper()} Circuit on Provider: {provider.upper()} (Shots: {shots})...")
    res = UniversalQuantumHub.execute(circuit, provider=provider, shots=shots)

    print(f"  [+] Job / Task ID    : {res.job_id}")
    print(f"  [+] Backend Provider : {res.backend_provider}")
    print(f"  [+] Backend Name     : {res.backend_name}")
    print(f"  [+] Execution Mode   : {res.execution_mode}")
    print(f"  [+] Authenticated    : {res.authenticated}")
    print(f"  [+] Execution Time   : {res.execution_time_ms:.2f} ms")
    print(f"  [+] Measured Counts  : {res.counts}")
    print(f"  [+] Probabilities    : {res.probabilities}")
    print("=" * 80)


def transpile_all():
    circuit = QuantumAST(num_qubits=2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure_all()

    print("=" * 80)
    print("  QMoosa-PQS Universal Quantum Transpilation Matrix (2-Qubit Bell State)")
    print("=" * 80)

    print("\n--- [1] IBM Quantum / AWS Braket (OpenQASM 3.0) ---")
    print(OpenQASMTranspiler.transpile(circuit))

    print("\n--- [2] Origin Quantum Wukong (QRunes) ---")
    print(OriginPilotTranspiler.transpile(circuit))

    print("\n--- [3] IonQ Trapped Ion (Native Gate JSON) ---")
    print(IonQJSONTranspiler.transpile(circuit))

    print("\n--- [4] Rigetti Quantum Cloud (Quil 3.0) ---")
    print(RigettiQuilTranspiler.transpile(circuit))
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Universal Multi-Provider Quantum Hub")
    parser.add_argument("--status", action="store_true", help="Display status of all quantum computer APIs")
    parser.add_argument("--run", action="store_true", help="Execute test circuit on selected/auto provider")
    parser.add_argument("--provider", default="auto", choices=["auto", "ibm", "origin", "ionq", "aws_braket", "rigetti", "simulator"], help="Target provider")
    parser.add_argument("--transpile", action="store_true", help="Show circuit compilation across all quantum languages")
    parser.add_argument("--shots", type=int, default=1024, help="Shot count")

    args = parser.parse_args()

    if args.transpile:
        transpile_all()
    elif args.run:
        run_circuit(args.provider, shots=args.shots)
    else:
        print_status_table()


if __name__ == "__main__":
    main()

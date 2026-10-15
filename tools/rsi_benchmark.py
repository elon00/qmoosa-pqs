"""Deterministic optimization benchmark; NOT a Raven runtime or autonomous RSI."""
import hashlib
import json
import platform
import subprocess
from pathlib import Path

from core.ast_circuit import QuantumAST
from core.constraint_solver import ConstraintSolver


def cases():
    a = QuantumAST(3, name="inverse_pairs")
    a.h(0).h(0).x(1).x(1).cx(0, 2).cx(0, 2).h(2)
    b = QuantumAST(2, name="nontrivial")
    b.h(0).cx(0, 1).measure_all()
    return [a, b]


def git_sha():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def evaluate():
    rows = []
    for circuit in cases():
        baseline = circuit.get_statistics()
        optimized, passes = ConstraintSolver().solve_and_optimize(circuit)
        candidate = optimized.get_statistics()
        non_regression = (
            candidate["total_gates"] <= baseline["total_gates"]
            and candidate["depth"] <= baseline["depth"]
        )
        improved = (
            candidate["total_gates"] < baseline["total_gates"]
            or candidate["depth"] < baseline["depth"]
        )
        rows.append({
            "case": circuit.name,
            "baseline": {"gates": baseline["total_gates"], "depth": baseline["depth"]},
            "candidate": {"gates": candidate["total_gates"], "depth": candidate["depth"]},
            "non_regression": non_regression,
            "improved": improved,
            "passes": [p.name for p in passes],
        })
    all_safe = all(r["non_regression"] for r in rows)
    useful = any(r["improved"] for r in rows)
    report = {
        "schema_version": 1,
        "kind": "LOCAL_OPTIMIZER_BENCHMARK_NOT_RAVEN_RSI",
        "git_sha": git_sha(),
        "python": platform.python_version(),
        "accepted": bool(all_safe and useful),
        "hardware_verified": False,
        "raven_runtime_invoked": False,
        "cases": rows,
    }
    report["evidence_sha256"] = hashlib.sha256(
        json.dumps(report, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return report


if __name__ == "__main__":
    print(json.dumps(evaluate(), sort_keys=True, indent=2))

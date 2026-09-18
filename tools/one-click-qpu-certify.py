#!/usr/bin/env python3
"""One-click fail-closed QPU certification runner.

This runner NEVER fabricates provider evidence. It can execute software gates
and, when credentials are configured, invoke the provider adapter. A 10/10
certificate is emitted only after provider-issued execution evidence and
independent receipt verification are present.
"""
import json, os, subprocess, sys, hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "qpu-certification"
ART.mkdir(parents=True, exist_ok=True)

report = {
    "schema": "qmoosa.qpu.certification.v1",
    "started_at": datetime.now(timezone.utc).isoformat(),
    "repo": "elon00/qmoosa-pqs",
    "canonical_control_plane": "elon00/bountyhunter-os",
    "status": "BLOCKED",
    "gates": {},
}

def gate(name, passed, evidence):
    report["gates"][name] = {"status": "PASS" if passed else "FAIL", "evidence": evidence}
    return passed

def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return p.returncode == 0, (p.stdout + "\n" + p.stderr)[-12000:]

# 1. Software gates
ok, out = run([sys.executable, "-m", "unittest", "discover", "-s", "tests"])
gate("software_tests", ok, out)

# 2. Credential presence is NOT execution proof.
provider = os.getenv("QMOOSA_QPU_PROVIDER", "origin").lower()
if provider not in ("origin", "ibm"):
    gate("provider_selection", False, "QMOOSA_QPU_PROVIDER must be origin or ibm")
else:
    gate("provider_selection", True, provider)

# 3. Require evidence produced by a provider-aware execution command.
evidence_path = ART / "provider-execution.json"
if not evidence_path.exists():
    gate("provider_execution", False,
         "Missing provider-execution.json. Run the authenticated provider execution step.")
else:
    try:
        ev = json.loads(evidence_path.read_text())
        required = ["provider", "provider_job_id", "backend", "status",
                    "result", "shots", "circuit_sha256"]
        missing = [k for k in required if k not in ev]
        valid_id = bool(ev.get("provider_job_id")) and not str(ev.get("provider_job_id","")).startswith(("ibmq_job_", "origin_job_"))
        result_ok = isinstance(ev.get("result"), dict) and sum(ev["result"].values()) == ev.get("shots")
        passed = not missing and valid_id and ev.get("status") in ("COMPLETED","SUCCESS") and result_ok
        gate("provider_execution", passed, {
            "missing": missing,
            "provider_job_id_is_provider_issued": valid_id,
            "terminal_status": ev.get("status"),
            "result_shots_match": result_ok
        })
    except Exception as e:
        gate("provider_execution", False, f"Invalid evidence: {type(e).__name__}: {e}")

# 4. Independent digest verification.
receipt = ART / "provider-receipt.json"
if receipt.exists():
    try:
        data=json.loads(receipt.read_text())
        declared=data.pop("digest", "")
        canonical=json.dumps(data, sort_keys=True, separators=(",",":")).encode()
        actual=hashlib.sha3_512(canonical).hexdigest()
        gate("receipt_integrity", actual == declared, {"digest_verified": actual == declared})
    except Exception as e:
        gate("receipt_integrity", False, f"Invalid receipt: {e}")
else:
    gate("receipt_integrity", False, "Missing provider-receipt.json")

mandatory = ["software_tests","provider_selection","provider_execution","receipt_integrity"]
report["status"] = "CERTIFIED_10_OF_10" if all(report["gates"][g]["status"]=="PASS" for g in mandatory) else "BLOCKED"
report["finished_at"] = datetime.now(timezone.utc).isoformat()
out = ART / "qpu-certification-report.json"
out.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
sys.exit(0 if report["status"]=="CERTIFIED_10_OF_10" else 2)

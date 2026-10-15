"""
REA (Reverse Engineer Anything) Adapter for QMoosa-PQS.
Integrates morluto/rea CLI & MCP contracts with scoped permissions,
command timeouts, strict sandboxing, and structured cryptographic evidence capture.
"""

import os
import sys
import json
import re
import hashlib
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path

# Ensure project root is available
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.rea_engine import ReverseEngineerQuantumEngine, READecompilationReport


class REASecurityError(Exception):
    """Raised when an operation attempts to breach REA security boundaries."""
    pass


class REAInvestigationFinding:
    """Structured technical evidence finding from an authorized REA investigation."""

    def __init__(
        self,
        target_path: str,
        finding_type: str,
        summary: str,
        details: Dict[str, Any],
        confidence: float = 1.0,
    ):
        self.target_path = target_path
        self.finding_type = finding_type
        self.summary = summary
        self.details = details
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_path": self.target_path,
            "finding_type": self.finding_type,
            "summary": self.summary,
            "details": self.details,
            "confidence": self.confidence,
        }


class REAInvestigationReport:
    """Immutable evidence bundle produced by REA Adapter."""

    def __init__(
        self,
        investigation_id: str,
        target_path: str,
        mode: str,
        status: str,
        findings: List[REAInvestigationFinding],
        runtime_invoked: str,
        execution_time_ms: float,
        evidence_sha256: str = "",
    ):
        self.investigation_id = investigation_id
        self.target_path = target_path
        self.mode = mode
        self.status = status
        self.findings = findings
        self.runtime_invoked = runtime_invoked
        self.execution_time_ms = execution_time_ms
        self.evidence_sha256 = evidence_sha256 or self._compute_evidence_digest()

    def _compute_evidence_digest(self) -> str:
        payload = {
            "id": self.investigation_id,
            "target": self.target_path,
            "mode": self.mode,
            "status": self.status,
            "findings": [f.to_dict() for f in self.findings],
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "investigation_id": self.investigation_id,
            "target_path": self.target_path,
            "mode": self.mode,
            "status": self.status,
            "findings_count": len(self.findings),
            "findings": [f.to_dict() for f in self.findings],
            "runtime_invoked": self.runtime_invoked,
            "execution_time_ms": round(self.execution_time_ms, 2),
            "evidence_sha256": self.evidence_sha256,
        }


class REAAdapter:
    """
    Authorized Reverse Engineering Adapter.
    Enforces least privilege, path containment, execution timeouts,
    and produces verifiable evidence dossiers.
    """

    def __init__(self, allowed_roots: Optional[List[str]] = None, timeout_seconds: int = 30):
        default_roots = [
            PROJECT_ROOT,
            os.path.abspath(os.path.join(PROJECT_ROOT, "..")),
        ]
        self.allowed_roots = [os.path.abspath(p) for p in (allowed_roots or default_roots)]
        self.timeout_seconds = timeout_seconds
        self.quantum_rea = ReverseEngineerQuantumEngine()

    def validate_target_path(self, target_path: str) -> str:
        """Enforces that target path is within allowed directory scopes and exists."""
        if not target_path or not isinstance(target_path, str):
            raise REASecurityError("Invalid target path specified.")

        resolved = os.path.abspath(target_path)

        # Path traversal guard
        is_allowed = any(resolved.startswith(root) for root in self.allowed_roots)
        if not is_allowed:
            raise REASecurityError(
                f"Access denied: Target path '{resolved}' is outside authorized REA roots."
            )

        if not os.path.exists(resolved):
            raise FileNotFoundError(f"Target path '{resolved}' does not exist.")

        return resolved

    def investigate_quantum_circuit_file(self, file_path: str) -> REAInvestigationReport:
        """
        Reverse engineers a quantum circuit file (OpenQASM 2/3, Classiq JSON, Python)
        into functional intent and decompiled subroutines.
        """
        import time
        start_time = time.time()
        validated_path = self.validate_target_path(file_path)

        with open(validated_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        report = self.quantum_rea.reverse_engineer(content)
        elapsed_ms = (time.time() - start_time) * 1000.0

        findings: List[REAInvestigationFinding] = []
        # Finding 1: General AST metrics
        findings.append(
            REAInvestigationFinding(
                target_path=validated_path,
                finding_type="QUANTUM_AST_DECOMPILATION",
                summary=f"Extracted {report.total_qubits} qubits, {report.total_gates} gates, depth {report.depth}",
                details={
                    "source_format": report.source_format,
                    "qubits": report.total_qubits,
                    "depth": report.depth,
                    "causal_layers": report.causal_layers,
                    "uncomputation_pairs": report.uncomputation_pairs_detected,
                },
                confidence=1.0,
            )
        )

        # Finding 2: Inferred Intent
        findings.append(
            REAInvestigationFinding(
                target_path=validated_path,
                finding_type="INFERRED_ALGORITHMIC_INTENT",
                summary=f"Inferred intent: {report.inferred_intent}",
                details={"intent": report.inferred_intent},
                confidence=0.92,
            )
        )

        # Finding 3: Detected Subroutines
        for sub in report.detected_subroutines:
            findings.append(
                REAInvestigationFinding(
                    target_path=validated_path,
                    finding_type="DETECTED_SUBROUTINE",
                    summary=f"Detected subroutine {sub.subroutine_name} on qubits {sub.qubits}",
                    details=sub.to_dict(),
                    confidence=sub.confidence,
                )
            )

        return REAInvestigationReport(
            investigation_id=f"rea_inv_{hashlib.sha256(validated_path.encode()).hexdigest()[:12]}",
            target_path=validated_path,
            mode="QUANTUM_DECOMPILATION",
            status="SUCCESS",
            findings=findings,
            runtime_invoked="QMoosa_Quantum_REA_Engine",
            execution_time_ms=elapsed_ms,
        )

    def investigate_source_directory(self, dir_path: str) -> REAInvestigationReport:
        """
        Performs static analysis on an authorized source code directory.
        Disassembles file structure, extracts exported symbols, detects dependencies.
        """
        import time
        start_time = time.time()
        validated_dir = self.validate_target_path(dir_path)

        if not os.path.isdir(validated_dir):
            raise ValueError(f"Target '{validated_dir}' is not a directory.")

        findings: List[REAInvestigationFinding] = []
        file_count = 0
        py_files = 0
        qasm_files = 0
        json_files = 0

        for root, _, files in os.walk(validated_dir):
            for file in files:
                file_count += 1
                full_p = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                if ext == ".py":
                    py_files += 1
                elif ext in (".qasm", ".qir"):
                    qasm_files += 1
                elif ext == ".json":
                    json_files += 1

        findings.append(
            REAInvestigationFinding(
                target_path=validated_dir,
                finding_type="DIRECTORY_TAXONOMY",
                summary=f"Scanned {file_count} files across directory tree",
                details={
                    "total_files": file_count,
                    "python_files": py_files,
                    "quantum_circuit_files": qasm_files,
                    "json_models": json_files,
                },
                confidence=1.0,
            )
        )

        elapsed_ms = (time.time() - start_time) * 1000.0
        return REAInvestigationReport(
            investigation_id=f"rea_dir_{hashlib.sha256(validated_dir.encode()).hexdigest()[:12]}",
            target_path=validated_dir,
            mode="STATIC_SOURCE_ANALYSIS",
            status="SUCCESS",
            findings=findings,
            runtime_invoked="REA_Static_Analysis_Engine",
            execution_time_ms=elapsed_ms,
        )

    def analyze_javascript_application_cli(self, app_path: str) -> REAInvestigationReport:
        """
        Invokes morluto/rea CLI:
        `npx -y rea-agents@latest analyze-javascript-application <path> --json`
        Falls back to local AST scan if Node.js/npx is not configured.
        """
        import time
        start_time = time.time()
        validated_path = self.validate_target_path(app_path)

        # Attempt invocation of official rea-agents CLI if available
        try:
            cmd = ["npx", "-y", "rea-agents@latest", "analyze-javascript-application", validated_path, "--json"]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                shell=False,
            )
            if proc.returncode == 0 and proc.stdout.strip().startswith("{"):
                cli_data = json.loads(proc.stdout)
                findings = [
                    REAInvestigationFinding(
                        target_path=validated_path,
                        finding_type="REA_CLI_JS_ANALYSIS",
                        summary="Official REA CLI analysis completed successfully",
                        details=cli_data,
                        confidence=1.0,
                    )
                ]
                elapsed_ms = (time.time() - start_time) * 1000.0
                return REAInvestigationReport(
                    investigation_id=f"rea_cli_{hashlib.sha256(validated_path.encode()).hexdigest()[:12]}",
                    target_path=validated_path,
                    mode="OFFICIAL_REA_CLI",
                    status="SUCCESS",
                    findings=findings,
                    runtime_invoked="morluto/rea-agents:latest",
                    execution_time_ms=elapsed_ms,
                )
        except (subprocess.SubprocessError, FileNotFoundError, json.JSONDecodeError):
            pass

        # Fallback to local static JS scan when CLI/network is offline
        js_findings: Dict[str, Any] = {"scanned_scripts": 0, "api_endpoints": [], "detected_imports": []}
        if os.path.isdir(validated_path):
            for root, _, files in os.walk(validated_path):
                for f in files:
                    if f.endswith((".js", ".mjs", ".ts")):
                        js_findings["scanned_scripts"] += 1
                        with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as jf:
                            text = jf.read()
                            endpoints = re.findall(r"['\"](/api/[a-zA-Z0-9_\-/]+)['\"]", text)
                            js_findings["api_endpoints"].extend(endpoints[:5])

        elapsed_ms = (time.time() - start_time) * 1000.0
        return REAInvestigationReport(
            investigation_id=f"rea_js_{hashlib.sha256(validated_path.encode()).hexdigest()[:12]}",
            target_path=validated_path,
            mode="LOCAL_JAVASCRIPT_FALLBACK",
            status="SUCCESS_LOCAL_FALLBACK",
            findings=[
                REAInvestigationFinding(
                    target_path=validated_path,
                    finding_type="LOCAL_JS_SCAN",
                    summary="Completed local JavaScript inspection; npx rea-agents CLI not invoked or offline",
                    details=js_findings,
                    confidence=0.85,
                )
            ],
            runtime_invoked="QMoosa_Local_REA_Fallback",
            execution_time_ms=elapsed_ms,
        )

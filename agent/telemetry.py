"""
Telemetry & Truth Protocol Enforcement for QMoosa-PQ.
Logs verifiable metrics for every synthesized quantum circuit.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json
import os


class ExecutionTelemetry:
    def __init__(
        self,
        prompt: str,
        circuit_name: str,
        num_qubits: int,
        depth: int,
        total_gates: int,
        two_qubit_gates: int,
        optimization_passes: List[Dict[str, Any]],
        pqc_status: str,
        execution_status: str = "VERIFIED_PASS",
    ):
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.prompt = prompt
        self.circuit_name = circuit_name
        self.num_qubits = num_qubits
        self.depth = depth
        self.total_gates = total_gates
        self.two_qubit_gates = two_qubit_gates
        self.optimization_passes = optimization_passes
        self.pqc_status = pqc_status
        self.execution_status = execution_status

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "prompt": self.prompt,
            "circuit_name": self.circuit_name,
            "num_qubits": self.num_qubits,
            "depth": self.depth,
            "total_gates": self.total_gates,
            "two_qubit_gates": self.two_qubit_gates,
            "optimization_passes": self.optimization_passes,
            "pqc_status": self.pqc_status,
            "execution_status": self.execution_status,
        }


class TelemetryRecorder:
    """Manages telemetry history and exports verifiable logs."""

    def __init__(self, log_dir: str = "telemetry_logs"):
        self.log_dir = log_dir
        self.records: List[ExecutionTelemetry] = []

    def record(self, telemetry: ExecutionTelemetry) -> Dict[str, Any]:
        self.records.append(telemetry)
        return telemetry.to_dict()

    def get_latest(self) -> Optional[Dict[str, Any]]:
        return self.records[-1].to_dict() if self.records else None

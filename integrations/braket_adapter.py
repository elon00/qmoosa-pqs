"""Optional Amazon Braket integration for QMoosa-PQS.

Amazon Braket is an optional algorithm/provider layer. QMoosa core remains
provider-neutral and BountyHunter OS remains the final reality authority.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any

OFFICIAL_ALGORITHM_LIBRARY = "https://github.com/amazon-braket/amazon-braket-algorithm-library"
OFFICIAL_SDK_DOCS = "https://docs.aws.amazon.com/braket/"
SOURCE_LICENSE = "Apache-2.0"

@dataclass(frozen=True)
class BraketCapability:
    available: bool
    reason: str
    library: str = OFFICIAL_ALGORITHM_LIBRARY
    license: str = SOURCE_LICENSE

def capability() -> BraketCapability:
    try:
        import braket  # type: ignore
    except ImportError:
        return BraketCapability(False, "Amazon Braket SDK is not installed")
    return BraketCapability(True, f"Amazon Braket SDK available ({getattr(braket, '__version__', 'unknown')})")

def make_bell_circuit() -> Any:
    try:
        from braket.circuits import Circuit  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install requirements-braket.txt for Braket circuit generation.") from exc
    return Circuit().h(0).cnot(0, 1)

def run_on_device(circuit: Any, device_arn: str, shots: int = 1024) -> Any:
    if not device_arn:
        raise ValueError("device_arn is required")
    try:
        from braket.aws import AwsDevice  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install requirements-braket.txt for Braket device execution.") from exc
    # Deliberately no simulator fallback.
    return AwsDevice(device_arn).run(circuit, shots=shots)

def normalize_task_metadata(task: Any) -> dict[str, Any]:
    task_id = getattr(task, "id", None)
    if not task_id:
        raise ValueError("Provider task object did not expose a provider-issued id")
    return {
        "provider": "Amazon Braket",
        "provider_task_id": str(task_id),
        "device_arn": str(getattr(task, "device_arn", "")),
        "status": str(getattr(task, "state", "UNKNOWN")),
        "physical_execution_claim": False,
    }

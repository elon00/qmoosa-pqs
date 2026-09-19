"""Optional Amazon Braket integration for QMoosa-PQS.

This module deliberately keeps Amazon Braket optional. QMoosa core remains
provider-neutral; Braket is an algorithm/device adapter, not the certification
authority. Physical-QPU claims still require provider-issued evidence and the
BountyHunter OS gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


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
    """Report whether the optional Braket SDK is installed."""
    try:
        import braket  # type: ignore  # optional dependency
    except ImportError:
        return BraketCapability(False, "Amazon Braket SDK is not installed")
    version = getattr(braket, "__version__", "unknown")
    return BraketCapability(True, f"Amazon Braket SDK available ({version})")


def make_bell_circuit() -> Any:
    """Create a canonical Bell circuit using the Braket SDK.

    Raises a clear error instead of silently falling back to QMoosa's simulator.
    """
    try:
        from braket.circuits import Circuit  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Amazon Braket SDK is required for Braket circuit generation. "
            "Install the optional Braket integration dependencies."
        ) from exc
    return Circuit().h(0).cnot(0, 1)


def run_on_device(circuit: Any, device_arn: str, shots: int = 1024) -> Any:
    """Submit a circuit to an explicitly selected Braket device.

    The caller must provide a real device ARN. No simulator fallback is used.
    The returned object is the Braket SDK quantum-task handle/result path and
    must be independently verified before it can be classified as physical QPU
    execution by BountyHunter OS.
    """
    if not device_arn:
        raise ValueError("device_arn is required")
    try:
        from braket.aws import AwsDevice  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Amazon Braket SDK is required for device execution."
        ) from exc
    device = AwsDevice(device_arn)
    return device.run(circuit, shots=shots)


def normalize_task_metadata(task: Any) -> dict[str, Any]:
    """Extract provider metadata without inventing identifiers."""
    task_id = getattr(task, "id", None)
    if not task_id:
        raise ValueError("Provider task object did not expose a provider-issued id")
    return {
        "provider": "Amazon Braket",
        "provider_task_id": str(task_id),
        "device_arn": str(getattr(task, "device_arn", "")),
        "status": str(getattr(task, "state", "UNKNOWN")),
        "physical_execution_claim": False,
        "certification_note": (
            "Provider metadata is evidence input only; BountyHunter OS must "
            "independently verify task state/result before certification."
        ),
    }

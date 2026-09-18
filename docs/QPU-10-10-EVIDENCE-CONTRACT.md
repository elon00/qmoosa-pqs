# QPU 10/10 Evidence Contract

This document is the QMoosa-PQS workload-side contract consumed by the BountyHunter OS canonical control plane.

## Hardware proof is not the same as gateway success
A gateway may reach a provider endpoint or authenticate without proving a physical QPU result. A locally generated job ID, simulator counts, calibrated emulation, or a provider HTTP 200 response is insufficient.

## Required provider evidence
- provider-issued job/task identifier
- provider-reported backend/device
- provider-reported lifecycle state
- provider-returned final result
- observed result shot count matching the requested count
- circuit hash matching the submitted circuit artifact
- timestamp and provider API version
- non-secret evidence receipt
- cryptographic digest over the canonical receipt

## Fail-closed rules
- Never generate a provider job ID and call it provider evidence.
- Never use local QuantumExecutionEngine counts as a physical-QPU result.
- Never set PHYSICAL_CLOUD_EXECUTED until the provider result has been retrieved and validated.
- Provider authentication without successful execution remains pending.
- Submission without a terminal result remains pending.
- Missing receipt remains pending/failed.

## IBM Quantum REST requirements
The current IBM Quantum Compute Service REST documentation requires an authenticated bearer token and Service-CRN for job calls, and documents the sequence: submit job, use the returned job ID to inspect status, then retrieve final results. QMoosa-PQS must preserve that provider-issued ID and retrieve the provider result rather than substituting simulator output.

## Certification handoff
QMoosa-PQS emits observations and evidence. BountyHunter OS decides the final certification state. The only valid 10/10 terminal state is CERTIFIED_10_OF_10 after all mandatory evidence gates and independent verification pass.
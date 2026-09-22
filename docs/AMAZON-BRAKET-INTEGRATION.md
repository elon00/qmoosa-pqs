# Amazon Braket Integration

QMoosa-PQS uses the official Amazon Braket Algorithm Library as an optional
algorithm/provider integration.

Official sources:
- https://github.com/amazon-braket/amazon-braket-algorithm-library
- https://docs.aws.amazon.com/braket/
- https://github.com/amazon-braket/amazon-braket-examples

Reality rules:
1. An imported Braket algorithm is not hardware proof.
2. A Braket simulator result is simulation evidence.
3. A provider task ID proves submission/identity only; it does not alone prove physical completion.
4. Physical certification requires provider terminal state, provider result, exact circuit identity, shot integrity, device identity, and independent re-query.
5. QMoosa must never silently fall back to its local simulator while claiming Braket execution succeeded.

Execution tiers:
- PR/CI: local simulator + adapter tests.
- Integration: Braket managed simulator.
- Hardware proof: explicitly selected Braket QPU + provider evidence.
- Certification: BountyHunter OS independently verifies the evidence bundle.

The Braket dependency remains optional to preserve QMoosa's lightweight core.

# Amazon Braket Integration

QMoosa-PQS uses the official Amazon Braket Algorithm Library as an **optional
algorithm/provider integration**, not as the core architecture or certification
authority.

## Official sources

- Algorithm Library: https://github.com/amazon-braket/amazon-braket-algorithm-library
- Braket documentation: https://docs.aws.amazon.com/braket/
- Braket examples: https://github.com/amazon-braket/amazon-braket-examples

## Architecture

```
QMoosa Agent / AST
       |
       v
Algorithm Registry
       |
       +--> Amazon Braket algorithms
       |
       +--> Qiskit / other adapters
       |
       v
Canonical circuit
       |
       v
Provider adapter
       |
       v
Amazon Braket simulator OR QPU
       |
       v
Provider task/result evidence
       |
       v
BountyHunter OS verification
```

## Reality rules

1. Braket algorithms are reusable algorithm implementations; importing them does
   not prove hardware execution.
2. A local Braket simulator result is classified as simulation.
3. A Braket task ID is evidence of a submitted task, not by itself proof that a
   physical QPU completed it.
4. Physical certification requires provider-returned terminal state, result
   data, exact circuit identity, shot integrity, device identity, and an
   independent provider re-query.
5. QMoosa must never silently replace failed Braket execution with its local
   simulator while claiming the Braket path succeeded.

## Why optional?

The official library depends on the Braket SDK plus scientific/quantum packages.
Keeping it optional protects the lightweight QMoosa core and avoids making AWS
credentials or cloud dependencies mandatory for ordinary CI.

## Recommended execution tiers

- **PR/CI:** local QMoosa simulator + Braket adapter unit tests.
- **Integration:** Braket managed simulator.
- **Hardware proof:** explicitly selected Braket QPU + provider evidence.
- **Certification:** BountyHunter OS independently verifies the evidence bundle.

This separation lets QMoosa use mature algorithms without becoming locked to one
provider.

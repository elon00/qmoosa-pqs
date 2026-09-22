# QMoosa-PQS

Quantum compilation, cellular-automaton, simulation, provider-gateway and post-quantum cryptography research in Python.

[![CI](https://github.com/elon00/qmoosa-pqs/actions/workflows/ci.yml/badge.svg)](https://github.com/elon00/qmoosa-pqs/actions/workflows/ci.yml)
[![Status](https://img.shields.io/badge/Status-Research%20Prototype-orange.svg)](TRUTH_PROTOCOL.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Current status

**RESEARCH / PRODUCTION-QUALITY SOFTWARE PROTOTYPE — LIVE PHYSICAL-QPU EXECUTION NOT VERIFIED BY REPOSITORY-ONLY EVIDENCE**

QMoosa-PQS contains working classical compilation/simulation code, provider submission adapters, Conway cellular-automaton experiments, and application-layer ML-KEM/ML-DSA implementations/tests.

The repository deliberately separates these evidence classes:

| Capability | Current evidence |
|---|---|
| Quantum AST / optimizer / transpilers | Repository-tested software |
| Conway B3/S23 engine | Deterministic classical computation, repository-tested |
| Statevector / shot simulation | Local simulation, repository-tested |
| ML-KEM-768 / ML-DSA-65 | Application-layer integration and wire/invariant tests; application is not FIPS-validated |
| PQC deterministic vectors | Repository-defined regression seeds; **not official NIST KAT/ACVP files** |
| IBM / Origin provider adapters | HTTPS submission adapters plus offline calibrated-emulation fallback |
| Live cloud submission | May occur only with valid provider credentials; a successful submission is **not** a completed QPU result |
| Physical-QPU execution | Requires provider terminal state, provider-returned counts/result, circuit/shot integrity and provider API re-query |
| Checked-in provider receipt JSON | Repository-supplied fixtures with local SHA3-512 integrity checks; **not provider-signed or independently verified** |
| GitHub Pages | Static/demo web interface; not a live QPU execution service |

## Evidence rule

A physical-QPU claim requires all of the following for the exact run:

1. provider authentication succeeds;
2. provider issues a real job/task ID;
3. provider reports terminal success;
4. result data is fetched from the provider;
5. the physical backend identity is recorded;
6. requested circuit and shot count match;
7. an independent provider API re-query reproduces the terminal state/result;
8. the evidence bundle identifies the exact repository commit.

Until those conditions are met, the project reports either:

- `OFFLINE_CALIBRATED_EMULATION`; or
- `CLOUD_SUBMISSION_ACCEPTED_RESULT_NOT_FETCHED`.

Neither status means physical-QPU execution is verified.

## Security improvements

Provider HTTPS uses the system trust store with certificate and hostname verification enabled. The gateway no longer falls back to an unverified TLS context.

The direct provider adapters also no longer return local simulator counts as if they were completed provider results.

See [SECURITY.md](SECURITY.md).

## Quick start

Requirements:

- Python 3.11+

```bash
git clone https://github.com/elon00/qmoosa-pqs.git
cd qmoosa-pqs
python tests/run_all_tests.py
```

Run the local web demo:

```bash
python web/server.py --port 8088
```

## Optional provider credentials

Do not commit credentials.

```bash
export IBMQ_TOKEN="..."
export ORIGIN_API_KEY="..."
```

Credentials allow the adapters to attempt provider submission. Current direct gateway submission alone is deliberately classified as **submission observed, result not fetched**.

For live certification work, use the fail-closed lifecycle/evidence tooling and inspect every provider-issued artifact.

## What the test suite proves

The repository test suite covers, among other things:

- AST and optimizer behavior
- transpiler output
- Conway cellular rules and routing experiments
- statevector and measurement simulation
- ML-KEM / ML-DSA integration behavior
- tamper rejection
- offline-emulation honesty
- provider adapter failure behavior
- repository receipt integrity
- evidence-gate behavior

Passing these tests is engineering evidence. It is **not**:

- proof of physical QPU execution;
- a third-party quantum-provider attestation;
- an independent security audit;
- NIST/FIPS validation of this application;
- a scientific peer-review result;
- a production certification.

## PQC vector provenance

`core/nist_kat_data.py` historically used “external NIST KAT” terminology. The actual seeds are repository-defined deterministic seeds, so the current code explicitly reports:

`REPOSITORY_DEFINED_NOT_OFFICIAL_NIST_KAT`

The checks still validate useful FIPS-referenced wire sizes, deterministic behavior, round trips and tamper properties.

## Hardware receipt provenance

Files under `hardware_telemetry/*provider_receipt.json` are retained as repository evidence fixtures.

Their SHA3-512 values are **local integrity digests**. A locally reproducible digest can detect repository-file modification, but it does not prove that IBM Quantum or Origin Quantum signed or issued the file.

The validator therefore reports:

- local/internal consistency; and
- `externally_verified: false`.

## Architecture

```text
prompt / circuit
    |
    v
agent + AST
    |
    +--> Conway classical routing experiments
    |
    +--> optimizer / transpilers
    |
    +--> local statevector simulation
    |
    +--> PQC receipt/integrity experiments
    |
    +--> optional provider submission adapters
              |
              +--> no credentials -> calibrated emulation
              |
              +--> accepted submission -> wait for separate result/re-query evidence
```

Important components:

- `core/ast_circuit.py`
- `core/constraint_solver.py`
- `core/conway_engine.py`
- `core/execution_engine.py`
- `core/hardware_gateway.py`
- `core/qpu_adapter.py`
- `core/pqc_crypto.py`
- `core/nist_kat_data.py`
- `core/transpiler.py`
- `tests/`
- `tools/one-click-qpu-certify.py`

## Truth protocol

See [TRUTH_PROTOCOL.md](TRUTH_PROTOCOL.md).

The governing rule is simple: **submission is not execution, simulation is not hardware, and repository-generated evidence is not independent provider evidence.**

## Production boundary

Before presenting QMoosa-PQS as production quantum infrastructure, require:

1. provider-supported SDK/API integrations pinned to current provider specifications;
2. completed result retrieval and provider re-query tests;
3. provenance-sealed evidence from real physical-QPU jobs;
4. independent security review;
5. secrets management and rotation;
6. observability, retry/idempotency, rate-limit and incident handling;
7. reproducible releases and dependency/security scanning;
8. workload-specific performance characterization.

## License

MIT. See [LICENSE](LICENSE).

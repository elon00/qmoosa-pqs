# QMoosa-PQS Truth Protocol

Last reviewed: 2026-09-22

## Core rule

**Simulation is not hardware. Submission is not execution. Repository-generated evidence is not independent provider evidence.**

Every public status must state the strongest evidence actually obtained for that exact execution.

## Evidence states

### SOFTWARE_TESTED

Repository tests validate a software behavior such as AST construction, optimization, transpilation, cellular rules, simulation, or cryptographic integration.

This does not prove physical QPU execution or independent security.

### OFFLINE_CALIBRATED_EMULATION

A local simulator executes the circuit using repository-defined/calibrated hardware-profile parameters.

Required fields:

- `authenticated: false`
- `execution_mode: OFFLINE_CALIBRATED_EMULATION`

Never call this a hardware result.

### CLOUD_SUBMISSION_ACCEPTED_RESULT_NOT_FETCHED

The provider endpoint accepted a submission and returned a provider job/task identifier, but this adapter has not yet fetched a terminal provider result.

This status proves at most **submission acceptance**. It does not prove:

- that the job ran on a physical QPU;
- that it completed successfully;
- that local counts came from the provider.

Provider counts must remain absent until fetched from the provider.

### PHYSICAL_QPU_VERIFIED

This status may be emitted only when the evidence bundle contains all of:

1. authenticated provider request;
2. provider-issued job/task ID;
3. terminal provider success state;
4. provider-returned measurement result;
5. physical backend identity;
6. requested circuit hash/integrity evidence;
7. shot-count integrity;
8. independent provider API re-query of the completed job;
9. exact source commit/release provenance.

If any gate is missing, physical-QPU verification is blocked.

## Receipt rule

Checked-in JSON that says `provider=IBM` or `provider=Origin` is not automatically provider-issued.

A repository-computed SHA3-512 digest proves local file integrity only. It is not a provider signature.

Current `ProviderReceiptValidator` therefore distinguishes:

- `internally_consistent`
- `externally_verified`

and keeps `externally_verified=false` until a provider re-query/signature/provenance path is implemented.

## TLS rule

All provider HTTPS connections must use the operating system trust store with hostname and certificate validation.

The code must never silently set:

- `CERT_NONE`
- `check_hostname = False`
- an unverified SSL context

for provider credentials or evidence retrieval.

## Cryptographic claim rule

QMoosa-PQS contains application-layer ML-KEM-768 and ML-DSA-65 implementation/tests.

Allowed wording:

- FIPS 203/204 referenced
- wire-size invariant tested
- sign/verify or encaps/decaps integration tested
- tamper case rejected by repository tests

Not allowed without external evidence:

- FIPS validated module
- NIST certified application
- independently audited cryptographic implementation
- whole-system quantum safety

## Vector provenance rule

The deterministic seeds in `core/nist_kat_data.py` are repository-defined regression seeds.

They are **not** official NIST KAT/ACVP response files. Test output must report:

`REPOSITORY_VECTOR_CHECKS_PASS`

not `EXTERNAL_NIST_KAT_VERIFIED`.

If official ACVP/KAT files are later imported, record the exact source, version/hash, expected outputs and parsing procedure separately.

## Conway rule

Conway B3/S23 is a deterministic classical cellular automaton used for experiments such as routing, layout, repeatability and state evolution.

It is not quantum hardware and is not a cryptographic primitive.

## Web receipt rule

ML-DSA signing or ML-KEM encapsulation can make a repository receipt tamper-evident/authenticated by the key used.

It does not make the receipt:

- decentralized;
- provider-issued;
- independently audited;
- proof of physical-QPU execution.

## CI rule

Green CI means the repository checks executed successfully on that commit.

It does not certify:

- live QPU execution;
- scientific validity beyond the tested assertions;
- production readiness;
- legal/regulatory compliance;
- independent security.

## Production gate

QMoosa-PQS should remain a research/prototype platform until it has:

- current provider-supported integrations;
- terminal result polling/retrieval;
- independent re-query evidence;
- strict secret management;
- independent security review;
- monitoring and incident response;
- release/rollback procedures;
- workload-specific reliability/performance evidence.

## Machine-readable outcomes

Preferred statuses:

- `SOFTWARE_TESTED`
- `SIMULATION_EXEC_VERIFIED`
- `OFFLINE_CALIBRATED_EMULATION`
- `CLOUD_SUBMISSION_ACCEPTED_RESULT_NOT_FETCHED`
- `REPOSITORY_RECEIPTS_INTERNALLY_CONSISTENT`
- `REPOSITORY_VECTOR_CHECKS_PASS`
- `BLOCKED_LIVE_QPU_EVIDENCE_MISSING`
- `PHYSICAL_QPU_VERIFIED` only when every physical evidence gate passes

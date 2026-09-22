# Security Policy

## Project status

QMoosa-PQS is research/prototype software. Physical-QPU execution and provider-issued evidence must be verified independently for each run.

## Reporting

Report security-sensitive issues privately through GitHub security reporting when available. Do not place provider tokens, API keys, private credentials, user data, or exploitable service details in public issues.

Include:

- affected commit
- affected component/provider
- reproduction steps
- expected and actual behavior
- security impact
- suggested mitigation when known

## High-risk areas

Extra review is required for:

- TLS/provider API handling
- provider credentials
- job lifecycle and result provenance
- cryptographic implementations
- receipt/evidence generation
- claims that distinguish simulation from physical hardware

## TLS

Provider clients must use normal certificate and hostname verification. Disabling TLS certificate validation is prohibited.

## Evidence boundary

A repository-local digest is not a provider signature. A job submission response is not a completed physical-QPU execution. A simulator result is never substituted for a provider-returned result.

## Secrets

Never commit IBM, Origin, AWS Braket, IonQ or other provider credentials.

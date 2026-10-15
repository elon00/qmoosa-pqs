# QMoosa-PQS: Classiq + REA + evidence-gated RSI blueprint

## Provenance and authorization
- Owned deployment target: `elon00/qmoosa-pqs`.
- Reference REA project: `morluto/rea` (MIT; verify license/third-party notices for every imported file).
- Classiq's SDK is a separate quantum-programming provider, not part of REA.
- This PR integrates a **local deterministic benchmark harness only**. It does not invoke Raven, Classiq, REA, a QPU, or paid APIs. Never claim otherwise.
- REA must be limited to software owned by the operator, open-source software, or specifically authorized analyses. Never bypass authentication, DRM, paid feature gates, or provider access controls.

## Target architecture
```
UI / REST API / MCP client
    -> scoped policy/auth/quotas + audit log
    -> planner/orchestrator with per-tool permissions
       -> QuantumIR (validated AST + typed gates + measurement semantics)
          -> compiler pass manager
          -> constraint optimization (gate count, depth, ancilla budget, topology)
          -> equivalent-circuit checker -> simulator comparison
          -> optional Classiq adapter (pinned SDK, credentials, explicit consent)
          -> optional Qiskit/backend adapters (separate simulator / QPU types)
       -> REA MCP subprocess adapter (pinned official package, sandbox, timeout)
          -> locally owned/authorized target -> evidence dossier
       -> experiment manager ("Raven-style", NO runtime claimed)
          -> hypothesis -> isolated patch/worktree -> unit and quantum-equivalence tests
          -> repeatable baseline/candidate benchmark -> promotion policy -> PR for review
       -> ML-KEM/ML-DSA key management/attestation
    -> immutable CI evidence report
```

## Delivery phases
1. Inventory actual source, licenses, dependency lockfiles, security advisories, API contracts, workflow status. Make an SBOM. Mark absent integrations as MISSING.
2. Define QuantumIR schemas: register bounds, supported gates, negative examples, classical-control semantics; reject unsupported gates rather than silently approximating.
3. Add real Classiq SDK adapter as **optional**. Isolate imports; configure provider auth from secrets; validate quantum semantics on reference circuits; record backend identity, depth, two-qubit count, runtime, cost.
4. Add REA as a pinned optional MCP service. Follow official `npx rea-agents setup` guidance only with configuration approval. Execute local authorized analyses under least privilege with timeouts, strict paths and read-only defaults. Collect per-finding source hashes and limitations.
5. Implement controlled RSI experimentation; do NOT permit agents to rewrite policy, approval checks, secret handling, quality gates or their own success criteria. Use sandboxed worktrees, reproducible seeds, independent test harness, signed/immutable scoring rules, human-reviewed PR promotion.
6. Implement differential testing against trusted quantum simulator and property-based tests; check unitary equivalence up to global phase on bounded unitary circuits, and compare shot distributions with statistical tolerances when measured.
7. Real QPU: only use provider APIs with credential authorization and explicitly approved budget. Require terminal provider status, result download, backend identity, independent re-query, shot/circuit hash integrity. No provider access required for local engineering gates.
8. Add threat modeling, license compliance, secret scanning, SAST, dependency scanning, provenance and signed releases, telemetry, backup/rollback and SLO dashboards.

## RSI experiment acceptance
An optimization candidate can be marked `PROMOTABLE` only if:
- exact benchmark dataset and harness versions, seed, commit and environment are recorded;
- all baseline and candidate tests pass; no important security, reliability or quantum-equivalence regression;
- performance is measured on held-out circuits with repeated runs, effect size and variability;
- candidate meets objective-specific thresholds (for example median two-qubit gate reduction >= 5% on applicable circuits while no correctness regression);
- no new paid operation, untrusted code execution or deployment is triggered automatically;
- human reviewer approves merge.

`tools/rsi_benchmark.py` is intentionally just an illustrative local comparison against current `ConstraintSolver`. Its `accepted` result is **NOT** evidence of an actual self-improving agent or equivalent circuit semantics. Do not promote using this harness alone.

## Exact scorecard — 100 points, not a claimed score
- Compiler correctness and quantum equivalence: 20
- Optimization quality versus reproducible baselines: 15
- Agent autonomy with bounded permissions: 10
- REA integration and licensed, authorized evidence: 10
- Classiq interoperability verified on version-pinned SDK: 10
- RSI evaluation/held-out reproducibility: 10
- Security/PQC and supply chain validation: 10
- CI/CD and incident operations: 5
- Physical QPU lifecycle and independent evidence: 5
- User experience/docs/accessibility: 5

**Score** = sum of substantiated earned points. A missing test report, missing licensed integration or unknown runtime status gets zero for that criterion, not an assumed pass. No score of 100 until every criterion has independent, reviewable evidence. Score is an internal rubric, not a Classiq or NIST certification.

## Hard stop conditions
- Never deploy mainnet, incur QPU/cycles/API cost, mint tokens or send x402 payments without explicit approval.
- Never label mock/simulation as real hardware or repository-local vectors as official NIST KAT.
- Never auto-merge self-generated code solely because a model says it is better.
- Never paste API keys into issues, logs, prompts or repository files.
- Do not invent benchmarks, benchmark wins, RSI iterations, provider receipts or audit results.

# Evidence, Findings, and Repair

Use this contract to prevent pattern matches, source inspection, local fixes, and release proof from
being blurred together.

## Contents

1. Evidence levels
2. Severity, confidence, and evidence
3. Finding lifecycle
4. Audit-and-repair authorization
5. Required finding record

## Evidence levels

| Level | Meaning | Acceptable evidence |
|---|---|---|
| `E0 signal` | Suspicious pattern only | Search/scanner hit, name-based suspicion, incomplete trace |
| `E1 traced` | Failure path or violated invariant is proven in source/configuration | Complete caller-to-impact trace, schema/policy/configuration proof |
| `E2 reproduced` | Failure is exercised deterministically below the full UI runtime | Focused failing test, API request, harness, job invocation, migration rehearsal |
| `E3 runtime-proven` | Failure or success is observed in the actual controlled product runtime | Browser, simulator, app, service, or worker run with captured artifacts |
| `E4 external-proven` | Behavior is proven across a real external boundary | Deployed environment, real provider, physical device, signed/release artifact |

Apply these rules:

- Never report `E0` as a confirmed finding. Discard it or place it in a clearly separated
  investigation backlog.
- Allow direct security, policy, or data-integrity violations to be confirmed at `E1` when the
  violated invariant and reachability are explicit. Do not claim exploitability or runtime impact
  that still depends on unverified state.
- Do not call UI behavior, notification delivery, provider state, native permissions, or lifecycle
  behavior runtime-proven below `E3`.
- Do not infer `E4` from mocks, local builds, or controlled test environments.

## Keep severity, confidence, and evidence separate

Severity describes impact:

- **Critical**: data loss, security/privacy exposure, harmful output, irreversible corruption, or a
  core product journey/value proposition completely failing for reachable users.
- **High**: a common journey produces wrong, stale, inaccessible, or unrecoverable behavior.
- **Medium**: a realistic edge condition fails or degrades with a recovery path.
- **Low**: limited latent risk, weak diagnostics, or minor usability degradation.

Confidence describes certainty:

- **High**: repeatedly reproduced or supported by an unambiguous complete trace with no
  contradictory evidence.
- **Medium**: strong trace or one clear reproduction, but one material boundary remains untested.
- **Low**: incomplete trace or ambiguous observation. Investigate further before treating it as a
  release blocker.

Evidence level describes where proof stops. Never increase confidence merely because severity would
be high if the candidate were true.

Do not infer business criticality merely because the user selected a feature for audit. When the
feature's product centrality or reach is unknown, use High at most unless data loss, security,
privacy, harmful output, or irreversible impact independently justifies Critical.

Every Critical and High finding must:

- Be at least `E1`.
- Have its complete path re-read by the primary auditor.
- State any missing `E2-E4` proof.
- Include a deterministic regression oracle.

## Finding lifecycle

Use precise states:

- `candidate`
- `confirmed`
- `repair in progress`
- `fixed locally`
- `runtime-verified locally`
- `deployed unverified`
- `deployed verified`
- `partially addressed`
- `blocked`
- `refuted`
- `accepted risk`

Do not use `fixed` without a proof boundary. A committed change is not deployed; a deployed change
is not automatically provider-, device-, or release-verified.

## Audit-and-repair authorization

Treat an audit request as read-only. Enter repair only when the user explicitly asks to fix,
implement, resolve, remediate, or get confirmed findings sorted.

For each authorized repair:

1. Preserve the failing input, state, command, or scenario.
2. Add the narrowest useful automated regression oracle.
3. Implement the smallest fix that restores the feature contract.
4. Verify the expected failure path, not just the happy path.
5. Run checks proportional to the blast radius.
6. Rerun the original reproduction.
7. Record the exact resulting proof boundary.

Do not bundle unrelated cleanup with the repair. Do not deploy, alter providers, mutate live data,
send communications, process payments, or perform destructive actions unless separately
authorized.

## Required finding record

Record:

- Stable finding ID and concise title.
- Status, severity, confidence, and evidence level.
- Affected promise and user intent.
- Exact locations and complete execution path.
- Expected and actual behavior.
- Reachability, frequency, and affected users.
- Root cause.
- Deterministic reproduction and regression oracle.
- Evidence artifacts.
- Smallest production-safe repair.
- Verification performed and missing.
- Local, runtime, deployed, provider/device, and release states.

---
name: production-gap-auditor
description: >
  Audits broad whole-product and production-readiness gaps across multiple critical journeys,
  integrations, data boundaries, runtime states, deployment surfaces, and operational controls.
  Use for codebase-wide audits, production readiness, "tests pass but users complain", broad
  bug sweeps, release-risk investigations, and explicit audit-and-fix requests. Prefer
  feature-gap-auditor when the user names one bounded feature, screen, or workflow.
---

# Production Gap Auditor

Find the broad gaps between what a product claims, what its code and configuration implement, and
what users and operators actually experience. Do not confuse a pattern sweep with an audit or a
successful build with production proof.

## Operating Contract

1. Default to **Audit mode**: inspect and report without changing code.
2. Enter **Audit-and-repair mode** only when the user explicitly asks to fix, resolve, implement,
   or get findings sorted.
3. Scope by critical journeys and trust boundaries, not raw file count.
4. Treat static scanners as candidate generators only.
5. Require runtime evidence for runtime claims.
6. Separate local source, test, artifact, controlled runtime, deployed, provider/device, and
   release proof.

Read [evidence-and-repair.md](references/evidence-and-repair.md) for the required evidence ladder,
severity/confidence rules, finding lifecycle, and repair loop.

Read [platform-risk-checklists.md](references/platform-risk-checklists.md) after detecting the
product's runtimes. Apply only the relevant platform sections.

Read [runtime-verification.md](references/runtime-verification.md) whenever the audited product has
an observable UI, API, worker, notification, provider, or native behavior.

Use [patterns-by-language.md](references/patterns-by-language.md) and
`scripts/scan_candidates.py` for broad candidate generation. Never report their raw output as
findings.

## Mode Selection

### Full mode

Cover the highest-risk critical journeys and trust boundaries, then investigate and verify
candidates deeply. State any excluded surfaces.

### Quick mode

Reduce breadth, never evidence quality:

1. Perform brief reconnaissance and risk ranking.
2. Select at most five investigation targets. Make each target one critical journey or one
   related candidate cluster; do not treat five as a required finding count.
3. Trace and verify each selected target.
4. Exercise at least one real critical journey when the product has an observable runtime.
5. Report the deliberately limited coverage.

Never skip verification merely because the user asked for a quick audit.

## Phase 1: Reconstruct the Product Contract

Read repository instructions before other work. Then inspect whichever sources exist:

- Product docs, README, onboarding, UI copy, app/store or marketing claims.
- Routes, API schemas, database schemas, permissions, policies, and feature flags.
- Package/build manifests, environment documentation, deployment and release configuration.
- Tests, fixtures, harnesses, runbooks, readiness reports, and incident history.
- Background jobs, queues, webhooks, notifications, provider integrations, migrations, and
  rollback paths.

Record:

- What users and operators are supposed to accomplish.
- The 5-10 most important user or operational journeys.
- Entry points and output surfaces.
- Product runtimes: web, API, mobile, desktop, CLI, worker, serverless, AI, or mixed.
- Trust boundaries: authentication, authorization, ownership, money, regulated data, providers,
  generated outputs, and destructive actions.
- External dependencies and proof surfaces.
- Contradictions between claimed behavior and implementation.

## Phase 2: Define Risk-Weighted Coverage

Do not promise to audit “everything” based on repository size. Build a coverage plan that
prioritizes:

1. Core value journeys.
2. Security, privacy, money, entitlement, data-integrity, and irreversible boundaries.
3. Recent regressions, hotfixes, reverts, incidents, and high-churn areas.
4. Cross-layer integrations and background behavior.
5. Runtime states existing tests do not exercise.

Useful Git signals include recent hotfixes/reverts, high-churn production files, newly introduced
flags or migrations, and code changed since the last known release. Exclude generated, vendored,
fixture, snapshot, build-output, and dependency trees unless they are themselves the artifact
under audit.

Record included journeys, excluded surfaces, and why the chosen coverage is the best use of the
available time.

## Phase 3: Generate Candidates

Run the deterministic scanner when Python 3 is available:

```bash
python3 <skill-dir>/scripts/scan_candidates.py <repo-root> --format text
```

Use repository-native linters, typecheckers, schema tools, route inventories, dependency tooling,
and framework diagnostics where available. Supplement them with targeted `rg` searches from
[patterns-by-language.md](references/patterns-by-language.md).

Generate candidates across:

- Silent failures and misleading fallbacks.
- Incomplete or unreachable implementations.
- Frontend/backend/provider/schema/event/environment contract gaps.
- State, cache, concurrency, transaction, migration, and data-lifecycle failures.
- Loading, empty, error, cancellation, retry, and navigation dead ends.
- Authentication, authorization, ownership, rate-limit, webhook, and validation gaps.
- Unbounded work, lifecycle leaks, blocking work, and scale failures.
- Missing or misleading operational visibility.
- Release, configuration, deep-link, notification, permission, upgrade, and rollback gaps.
- Tests that encode only happy-path mechanics.

For each candidate, find the user or operator action that reaches it. Discard candidates with no
credible impact path or retain them only as unconfirmed `E0` signals outside the findings.

## Phase 4: Deep Trace the Highest-Risk Candidates

For every candidate likely to become a finding:

1. Start from the user action, system event, request, job, migration, deploy, or provider callback.
2. Follow the complete path through presentation, state, service, API, persistence, asynchronous
   work, external dependencies, and final feedback.
3. Identify the exact failure state and what the user or operator sees.
4. Check retry, timeout, idempotency, cancellation, rollback, reconciliation, and cleanup.
5. Check permissions, ownership, entitlements, flags, environment, version, and release state.
6. Check existing monitoring and whether it would distinguish failure from empty or normal state.
7. Identify the smallest deterministic reproduction and regression oracle.

Do not infer behavior from file names, function names, types, or grep output.

## Phase 5: Exercise Critical Journeys

Build a scenario matrix using [runtime-verification.md](references/runtime-verification.md).
Exercise applicable critical journeys with the safest available browser, simulator, device, API,
worker, harness, or repository-native tooling.

At minimum consider:

- First use and empty state.
- Happy path.
- Invalid and partial state.
- Slow, failed, offline, and stale dependencies.
- Retry, duplicate delivery, and concurrency.
- Reload, restart, background/resume, upgrade, and migration.
- Sign-out, account switch, permissions, ownership, entitlement, and flag changes.
- Locale, timezone, DST, units, large data, accessibility, and responsive layouts.
- Provider outage, webhook replay, expired credentials, and delayed background work.

Capture semantic UI or response state plus screenshots, console/network/application logs, traces,
job output, crash data, or database effects as appropriate. Reset state between scenarios.

When runtime access is unavailable, continue with source and focused test evidence, mark the audit
`static-only` for those surfaces, and list the exact missing proof. Never replace execution with a
mental walkthrough.

## Phase 6: Verify, Repair When Authorized, and Regress

Assign severity, confidence, and evidence level separately using
[evidence-and-repair.md](references/evidence-and-repair.md). Independently re-read and verify every
Critical and High finding.

In Audit-and-repair mode:

1. Preserve a deterministic reproduction.
2. Add the smallest useful failing test or automated scenario.
3. Apply the narrowest production-safe fix.
4. Run relevant tests, typechecks, lint, builds, migrations, and security checks.
5. Rerun the original failure and neighboring critical scenarios.
6. Update the finding to the exact proven state.

Do not deploy, mutate production data, alter external providers, send real communications, execute
real payments, or perform destructive account actions without explicit authorization.

## Phase 7: Report

Use the repository's audit convention when present. Otherwise write
`production-gap-audit-YYYY-MM-DD.md` only when a durable report is requested or clearly useful;
answer verbally when that is what the user asked for.

Include:

- Product contract, runtimes, critical journeys, and trust boundaries.
- Risk-weighted scope and explicit exclusions.
- Journey/scenario coverage matrix.
- Findings grouped by severity with stable IDs, status, confidence, evidence level, exact
  locations, expected vs actual behavior, reproduction, root cause, regression oracle,
  recommendation, and artifacts.
- Claimed-vs-actual capability matrix.
- Positive patterns worth retaining.
- Verification performed and not performed.
- Separate local, artifact, runtime, deployed, provider/device, and release proof.
- Recommended remediation order.

For a verbal audit, compress this to: readiness verdict, confirmed findings, journey/runtime
coverage, and exclusions or blocked proof. Include full matrices only when materially useful.

Do not classify the absence of a specific vendor, `/health` route, logging library, or architectural
pattern as a finding until it is relevant to the detected runtime and traced to a concrete risk.

## Completion Gate

Do not call the audit complete until:

- Every finding is at least `E1 traced`.
- Every Critical and High finding is independently verified.
- Every included critical journey has scenario coverage or an explicit blocked reason.
- Runtime claims have runtime evidence.
- Quick mode still meets the same evidence rules for its reduced scope.
- Audit-and-repair work reruns the original reproduction after each fix.
- The report states exactly what was excluded and what remains unverified.

## Optional Parallel Work

Use subagents only when permitted and when architecture, UI/runtime, integration/data, and
test/evidence surfaces can be investigated independently. Give each agent a bounded surface and raw
artifacts. Verify Critical and High claims yourself, deduplicate shared root causes, and maintain
one authoritative coverage matrix.

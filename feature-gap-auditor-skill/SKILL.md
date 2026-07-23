---
name: feature-gap-auditor
description: >
  Audits one named feature, screen, workflow, calculation, integration, or user promise by
  tracing its real execution path and, when observable at runtime, exercising it with browser,
  simulator, device, API, or harness automation. Use for "audit this feature", "is this flow
  actually working?", feature-gap investigations, suspicious product logic, claimed-vs-actual
  behavior, and requests to audit and fix one bounded capability. Prefer production-gap-auditor
  for a broad whole-product or production-readiness sweep.
---

# Feature Gap Auditor

Find where one specific feature betrays its promise to a real user. Treat static inspection as
candidate generation and runtime evidence as the standard for user-visible behavior.

## Operating Contract

1. Keep scope anchored to the named feature and its direct dependencies.
2. Default to **Audit mode**: inspect and report without changing code.
3. Enter **Audit-and-repair mode** only when the user explicitly asks to fix, implement, resolve,
   or get the confirmed findings sorted.
4. Never claim runtime, deployed, provider, device, or release proof from source inspection alone.
5. Prefer fewer reproduced findings over a long list of pattern matches.

Read [evidence-and-repair.md](references/evidence-and-repair.md) for the required evidence ladder,
finding states, severity rules, and repair loop.

Read [runtime-verification.md](references/runtime-verification.md) whenever the promise is visible
or behaviorally observable in a UI, API, background job, notification, provider, or native
integration. Runtime verification is required for runtime claims; it is not an optional polish
step.

Read [domain-contracts.md](references/domain-contracts.md) only when the feature models regulated
or relationship-heavy concepts such as legal roles, medical relationships, financial ownership,
permissions, entitlements, representation, provenance, or generated trust surfaces.

## Phase 1: Define the Feature Contract

### Establish the boundary

Record in the report or working audit artifact:

- Feature name and narrow scope.
- User intent and expected outcome.
- Entry points and output surfaces.
- Direct UI, state, service, persistence, job, provider, and export dependencies.
- Relevant user states, roles, entitlements, permissions, locales, and devices.
- Explicit exclusions.

If the request is ambiguous, choose the narrowest useful slice and state the assumption. Do not
expand into a whole-product sweep.

### Read product truth

Read repository instructions first, then relevant specs, UI copy, onboarding, routes, API
contracts, schemas, tests, release/readiness docs, and recent changes. Treat contradictions
between docs, UI, tests, and implementation as a contract ambiguity; do not silently select the
most convenient source.

For Sonopeace mobile or admin flows, inspect `docs/flows.json`, `docs/app-features.md`, and the
applicable harness/readiness guidance when present.

### Build a promise checklist

Extract 5-15 concrete, falsifiable promises with their sources. Include persistence, freshness,
permissions, failure recovery, and downstream use where applicable. Example:

> A saved notification time survives restart and replaces the previously scheduled notification.

Every later finding and verification scenario must map to at least one promise.

## Phase 2: Trace the Real Execution Path

For each entry point:

1. Start at the user action, system event, or background trigger.
2. Follow UI state, handlers, stores, services, API calls, persistence, jobs, provider calls, and
   the eventual refresh or output.
3. Identify the authoritative source for every material value.
4. Trace fallback, cache, invalidation, retry, timeout, cancellation, and reconciliation behavior.
5. Trace permissions, authentication, ownership, entitlements, flags, environment, and version
   gates.
6. Trace the same value through edit surfaces, validation, derived state, prompts or automation,
   exports, audit logs, proofs/fingerprints, and tests.
7. Identify the user's recovery path for every failure boundary.

Use repository search tools such as `rg` to locate terms, then read immediate callers and
consumers. A search hit is never a finding by itself.

## Phase 3: Generate and Rank Candidates

Probe for broken promises in these categories:

- Invalid or misleading product logic.
- Collected context or settings that do not affect the result.
- Missing-data defaults presented as real or personalized data.
- Stale state after mutation, restart, sign-out, account switch, disconnect, or revocation.
- Frontend/backend/provider contract mismatches.
- Optimistic success without rollback or reconciliation.
- Loading, empty, error, cancellation, and retry dead ends.
- Permission, ownership, entitlement, or feature-flag mismatches.
- Notification, background, deep-link, lifecycle, timezone, locale, unit, and DST failures.
- Missing observability on critical transitions.
- Tests that prove serialization or happy paths while accepting a false product contract.
- Domain, perspective, provenance, or derived trust-surface failures when applicable.

Rank candidates by:

`impact × likelihood × reach × irreversibility × evidence strength`

Discard or retain as `E0 candidate` anything not traced to a concrete user-visible or operational
impact.

## Phase 4: Build and Execute the Scenario Matrix

Create scenarios from the promise checklist before declaring the feature reliable. Select every
applicable row from [runtime-verification.md](references/runtime-verification.md), including:

- First use or empty state.
- Happy path.
- Invalid or partial input.
- Slow, failed, and offline dependencies.
- Retry, duplicate submission, and concurrency.
- Reload, restart, background/resume, and upgrade.
- Sign-out, account switch, entitlement change, and permission denial/revocation.
- Stale data and provider failure.
- Locale, timezone, DST, units, large data, and accessibility variants.

For each scenario, record setup, action, expected result, actual result, artifacts, cleanup, and
status: `passed`, `failed`, `blocked`, `not applicable`, or `unverified`.

For user-visible features, launch and exercise the product with the safest available browser,
simulator, device, API, or repository harness. Capture screenshots or semantic UI state plus
console, network, application, crash, or job evidence as applicable. Reset state between scenarios.

If runtime access is unavailable, continue with source and focused test evidence, label the audit
`static-only`, and list the exact missing proof. Do not mentally simulate a flow and call it tested.

## Phase 5: Verify Findings and Repair When Authorized

For every reported finding:

1. Trace the complete source-to-impact path.
2. Reproduce it with the strongest safe evidence available.
3. Record severity, confidence, and evidence level separately.
4. Provide a deterministic regression oracle.
5. Check whether existing tests accept the broken contract.

In Audit-and-repair mode, process confirmed findings in risk order:

1. Preserve the reproduction.
2. Add the smallest useful failing regression test or automated scenario.
3. Implement the narrowest production-safe fix.
4. Run blast-radius-appropriate tests, typechecks, lint, builds, and migrations.
5. Rerun the original scenario and relevant neighboring scenarios.
6. Update the finding to the exact proven state, such as `fixed locally` or
   `runtime-verified locally`.

Do not mutate live data, execute real payments or outbound messages, alter external providers, or
deploy unless the user has explicitly authorized that action.

## Phase 6: Report

Use the repository's audit convention when one exists. Otherwise write
`feature-gap-audit-[feature-slug].md` only when the user requested or would clearly benefit from a
durable report; answer verbally when that is what they asked for.

Include:

- Feature contract and source conflicts.
- Scope and explicit exclusions.
- Scenario coverage matrix.
- Findings with stable IDs, status, severity, confidence, evidence level, exact locations,
  expected vs actual behavior, reproduction, root cause, regression oracle, recommendation, and
  artifacts.
- Claimed-vs-actual capability matrix.
- Verification performed and not performed.
- Separate local, runtime, deployed, provider/device, and release proof.
- Smallest next slice for unresolved findings.

For a verbal audit, compress this to: verdict, confirmed findings, evidence/runtime coverage, and
unverified boundaries. Include full matrices only when they materially help the user.

## Completion Gate

Do not call the audit complete until:

- Every reported finding is at least `E1 traced`; `E0` signals are excluded or clearly separated.
- Every Critical or High finding has been independently re-read and verified.
- Every applicable critical promise has a scenario status.
- User-visible reliability claims have controlled runtime proof or are explicitly marked
  `static-only`.
- Audit-and-repair work reruns the original reproduction after the fix.
- The report states exactly what remains unverified.

## Optional Parallel Work

Use subagents only when permitted and when UI, state, backend, native/provider, and test surfaces
can be investigated independently. Give each agent a bounded surface and raw artifacts. Verify all
Critical and High claims yourself, deduplicate root causes, and preserve one authoritative coverage
matrix.

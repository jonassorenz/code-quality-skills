# Runtime Verification

## Contents

1. Runtime selection
2. Safe setup
3. Scenario matrix
4. Platform execution
5. Evidence and completion

## Runtime selection

Classify each promise by the strongest applicable runtime:

| Surface | Preferred execution |
|---|---|
| Web UI | Repository test harness, Playwright/browser automation, or controlled browser |
| iOS/macOS | Repository harness or Xcode simulator automation; physical device for device-only claims |
| Android | Repository harness, emulator automation, or physical device for device-only claims |
| API/service | Real local/test service plus HTTP/client calls and logs |
| Worker/job/webhook | Direct job invocation, queue/harness, replay-safe fixture, and resulting state |
| CLI | Built artifact or source command in an isolated fixture |
| Provider integration | Sandbox/test provider first; real provider only when authorized |

If `bug-hunter` or equivalent runtime-QA automation is installed, it may drive the UI breadth-first.
The auditor still owns the feature contract, code trace, evidence level, and post-fix regression.

## Safe setup

Before interaction:

1. Read repository launch and test guidance.
2. Identify the exact source revision, build, environment, flags, and account state.
3. Prefer disposable local/test data and sandbox providers.
4. Define a reset strategy for state, caches, app data, queues, and fixtures.
5. Identify observable channels: semantic/accessibility tree, screenshots, network, console,
   application logs, crash logs, jobs, database effects, and provider events.
6. Record actions that are prohibited without separate authorization: real payments, real outbound
   messages, destructive live-data changes, provider reconfiguration, and production deploys.

Do not use a stale already-running build without proving its revision.

## Scenario matrix

Select every applicable scenario; do not run irrelevant rows mechanically.

| Dimension | Scenarios |
|---|---|
| Baseline | first use, empty state, normal happy path, returning user |
| Input | missing, partial, malformed, boundary, large, Unicode, locale-specific |
| Dependency | slow, timeout, offline, server error, malformed response, stale response |
| Repetition | double submit, retry, duplicate callback, idempotent replay |
| Concurrency | two tabs/devices/users, overlapping refresh and mutation |
| Lifecycle | reload, cold start, warm start, background/resume, upgrade/migration |
| Identity | sign-out, account switch, expired session, deleted or disabled account |
| Access | permission denied, permission revoked, ownership change, role change |
| Commercial | entitlement grant/revoke, purchase pending/cancelled/refunded, flag change |
| Time | timezone change, DST boundary, clock skew, quiet hours, delayed job |
| Presentation | narrow/wide, keyboard, screen reader semantics, font scaling, theme |
| External | provider outage, expired credentials, webhook replay, delayed delivery |

For each scenario record:

- Promise and scenario ID.
- Setup and source/build identity.
- Exact actions or command.
- Expected behavior.
- Actual behavior.
- Artifact paths or trace identifiers.
- Cleanup/reset performed.
- `passed`, `failed`, `blocked`, `not applicable`, or `unverified`.

## Platform execution

### Web

Verify direct navigation and reload, browser back/forward, responsive widths, keyboard-only use,
focus order, semantic names, session expiry, multiple tabs, network failure, console errors, and
request/response behavior. Use screenshots together with semantic state; pixel evidence alone can
miss inaccessible controls.

### Mobile and desktop

Verify cold/warm launch, restart persistence, background/resume, permission denial/revocation,
deep links, notifications, offline transitions, keyboard or system back behavior, font scaling,
theme, rotation/resizing where supported, upgrade/migration, and crash logs. Do not claim physical
sensor, notification-delivery, purchase, or provider proof from a simulator when the boundary
requires a real device or account.

### APIs, workers, and providers

Verify non-success responses, timeouts, retries, idempotency, cancellation, concurrency, partial
writes, transaction rollback, job replay, poison messages, delayed work, signature validation,
rate limits, and observable final state. Use sandbox/test providers unless real-provider activity
is explicitly authorized.

## Evidence and completion

Capture the smallest evidence bundle that proves behavior:

- Source revision and runtime/build identity.
- Input/state fixture.
- Actions or command.
- Expected and actual result.
- Semantic UI/response plus screenshot where visual behavior matters.
- Relevant logs, network, crash, job, or persistence effects with secrets redacted.

Runtime verification is complete only when the scenario can be repeated from a known state. If a
required driver, credential, device, environment, or provider is unavailable, mark the scenario
blocked and name the exact missing proof. Never replace it with a mental walkthrough.

In Quick mode, reduce the number of journeys and variants. Keep the same reset, evidence, and
truth-labeling requirements.

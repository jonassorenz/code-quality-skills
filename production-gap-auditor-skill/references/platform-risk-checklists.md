# Platform Risk Checklists

## Contents

1. Common trust boundaries
2. Web
3. Mobile
4. Desktop and CLI
5. APIs, workers, and serverless
6. AI and generated output
7. Deployment and release
8. Contextual severity

Apply only the sections relevant to the detected product. These are investigation prompts, not
automatic findings.

## Common trust boundaries

- Authentication, session expiry, authorization, ownership, tenant isolation, and account switch.
- Input validation at the authoritative boundary.
- Money, entitlement, subscription, refund, and cancellation state.
- Regulated or sensitive data collection, access, retention, export, deletion, and logging.
- Cache/source-of-truth consistency and invalidation.
- Timeout, retry, cancellation, idempotency, deduplication, and reconciliation.
- Partial writes, transaction boundaries, migrations, rollback, and cleanup.
- Feature flags, environment configuration, secret handling, and version skew.
- Provider contracts, webhook verification/replay, credential expiry, and outages.
- Structured, privacy-safe observability that distinguishes failure from valid empty state.

## Web

- Direct-route authorization, reload, deep links, back/forward, and expired sessions.
- Server/client rendering differences and hydration failures.
- Optimistic mutations with rollback and cache reconciliation.
- Multiple tabs, stale forms, duplicate submits, and navigation during requests.
- Responsive layout, keyboard access, focus management, semantic labels, contrast, and zoom.
- CSP/CORS/cookie settings evaluated in the actual authentication architecture.
- Non-success responses including validation, rate limit, auth, timeout, and unavailable states.
- Client/server API shapes checked against actual handlers or generated contracts.

## Mobile

- Cold/warm start, background/resume, process death, app restart, and upgrade migration.
- Permission request, denial, revocation, limited access, and settings return.
- Offline/online transitions, queued writes, conflict resolution, and stale persisted stores.
- Deep links, push notification routing, local scheduling, timezone/DST, and quiet hours.
- Account switch/sign-out clearing sensitive cached data.
- Purchase pending/cancelled/refunded and server-authoritative entitlement.
- Font scaling, screen reader semantics, theme, rotation, keyboard/system back, safe areas.
- Simulator versus physical-device versus provider proof clearly separated.

## Desktop and CLI

- Window lifecycle, reopen, multi-window state, file permissions, sandboxing, and upgrades.
- File import/export cancellation, partial output, atomic writes, and collision behavior.
- Keychain/credential storage and account switching.
- Signals, exit codes, stdin/stdout/stderr contracts, non-interactive use, and interrupted commands.
- Paths containing spaces, Unicode, missing permissions, large files, and concurrent invocations.
- Signed/notarized/release artifact distinguished from a source build.

## APIs, workers, and serverless

- Route inventory and authoritative auth/ownership middleware.
- Request validation, error contracts, pagination, limits, timeouts, and cancellation.
- Transactions, consistency, concurrent updates, idempotency keys, and safe retries.
- Queue visibility timeouts, poison messages, dead-letter handling, replay, and alerting.
- Cron overlap, clock skew, delayed jobs, and missed schedules.
- Webhook signature, timestamp, replay defense, deduplication, and ordering.
- Cold starts, ephemeral filesystem assumptions, runtime limits, and partial execution.
- Health/readiness checks only where the deployment architecture consumes them.

## AI and generated output

- Structured user/domain context reaches the model or generator before generation.
- Source provenance, freshness, permissions, and tenant isolation.
- Prompt injection and untrusted-content boundaries.
- Schema validation, tool authorization, and destructive-action confirmation.
- Unsupported confidence, hallucinated facts, unsafe precision, and missing uncertainty.
- Cache/fingerprint invalidation when prompts, sources, policy, model, or domain relationships change.
- Evaluation fixtures cover harmful and misleading outputs, not merely valid serialization.
- Generated artifacts retain the context and provenance needed for review.

## Deployment and release

- CI checks the artifact and configuration actually released.
- Environment variables, migrations, flags, and provider configuration are version-compatible.
- Rollback does not conflict with forward-only data/schema changes.
- Backups and restore procedures are exercised where data loss is material.
- Monitoring and alerts target critical journeys and background work, not only process uptime.
- Source, local build, signed artifact, deployed revision, provider state, device state, and
  store/release state are proven separately.

## Contextual severity

Do not automatically report:

- Absence of a particular monitoring vendor.
- Absence of `/health` in mobile, static, desktop, or architecture-managed serverless products.
- `localStorage` use without evaluating threat model and token properties.
- Wildcard CORS on an intentionally public, credential-free resource.
- Missing pagination on a provably bounded dataset.
- Swallowed optional analytics errors that cannot affect product state.

Trace the architecture, reachability, user impact, and existing compensating controls first. Record
deliberate trade-offs as accepted risk when the decision and evidence support it.

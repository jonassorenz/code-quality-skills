---
name: feature-gap-auditor
description: >
  Performs deep audits of a specific feature, capability, screen, workflow, or user promise to
  find gaps between what the feature appears to offer and what it actually delivers. Use this
  skill whenever the user asks to audit a feature, inspect whether a feature is actually working,
  investigate suspicious product logic, probe edge cases, validate a core feature, find feature
  gaps, compare claimed behavior to real behavior, or dig into one area instead of the whole
  product. Trigger on phrases like "audit this feature", "is this feature actually working?",
  "dig deeper into this flow", "feature gap", "logic behind this", "does this make sense for
  users?", "what else like this is broken?", or when a screenshot/output suggests product logic
  may be technically valid but user-invalid.
---

# Feature Gap Auditor

You are performing a feature gap audit. Your job is to find where one specific feature fails to
deliver its promise to a real user, even if the code compiles, tests pass, and each local function
looks reasonable in isolation.

This is narrower than a production gap audit. Do not sweep the whole product unless the feature
requires it. Stay anchored to the named feature, workflow, screen, recommendation, calculation,
integration, or user-facing promise.

Think like a user and product owner first, then like an engineer. A user does not care that a
weighted average or API response is technically valid. They care whether the result is sensible,
fresh, explainable, recoverable, and aligned with their situation.

The core question: **What promise does this feature make, and where can that promise break?**

---

## Phase 1: Define Feature Contract

Before reading implementation details, establish what the feature is supposed to do.

### 1.1 Identify the feature boundary

Write down, in your thinking:
- Feature name or capability being audited.
- User intent: what the user is trying to accomplish.
- Product promise: what the UI, copy, docs, onboarding, or surrounding architecture implies.
- Entry points: screens, buttons, routes, notifications, background jobs, API endpoints, CLI commands.
- Output surfaces: UI cards, recommendations, alerts, persisted settings, sync state, emails, reports.
- Users affected: first-time users, power users, paid users, admins, partners, shift workers, missing-data users, etc.

If the feature boundary is ambiguous, choose the narrowest useful slice and state that assumption.

### 1.2 Read local guidance first

Read relevant local instructions before auditing:
- Root `AGENTS.md`
- Nearest subdirectory `AGENTS.md`
- Feature docs, specs, flow inventories, README, route docs, API contracts
- Existing audit or readiness docs if directly relevant

For Sonopeace specifically, inspect `docs/flows.json`, `docs/app-features.md`, and harness/readiness docs when a user-visible mobile/admin flow is involved.

### 1.3 Build a feature promise checklist

Extract 5-15 concrete promises from docs, UI copy, tests, types, and code structure. Good checklist items are specific:
- "User sees a bedtime target only when enough data supports it."
- "Setting saves and survives restart."
- "Connected wearable state matches provider reality."
- "Notification fires at the chosen local time."
- "Payment state cannot show active access until entitlement is real."

This checklist drives the rest of the audit.

### 1.4 Identify the domain model and relationship contract

For features that model real-world roles, legal/medical/financial/accounting concepts, permissions,
entitlements, ownership, workflow state, or regulated user promises, explicitly map the domain
relationships before trusting the UI.

Write down:
- Primary entities: the things that actually exist in the user's world.
- Roles vs entities: which labels are attributes, which are standalone records, and which are
  relationships between records.
- Required relationships: ownership, representation, client/opponent, payer/beneficiary,
  guardian/dependent, provider/patient, admin/member, source/derived output, or similar.
- Perspective: who the product is acting for, speaking to, optimizing for, or protecting.
- Neutral/third-party actors: courts, witnesses, auditors, support staff, regulators, processors,
  or observers that must not be treated as ordinary primary entities.
- Valid unresolved states: what can be draft/unknown, what must block readiness/export/action, and
  what must be marked clearly to the user.

If the feature collapses different real-world concepts into one enum, table, picker, string field,
or generic "party/user/item" list, treat that as a high-risk area until proven otherwise.

---

## Phase 2: Trace Real Execution Path

Trace the feature end to end. Do not infer from names.

For each entry point:
1. Start at user action or background trigger.
2. Follow UI state, handlers, stores/hooks/services, API calls, persistence, background work, and display refresh.
3. Identify source of truth for every important value.
4. Identify stale/cache/fallback behavior.
5. Identify permissions, entitlements, feature flags, provider state, and environment requirements.
6. Identify recovery path when something fails.
7. Trace the same value through every trust boundary: creation, edit screens, persistence,
   validation, derived status, prompts/AI calls, background jobs, exports/reports, audit logs,
   readiness/proof fingerprints, and tests.

Use `rg` aggressively. Read immediate callers and consumers before making claims.

Useful searches:
```bash
rg -n "featureName|screen title|button text|field_name|apiEndpoint" .
rg -n "catch|fallback|default|stale|isLoading|setTimeout|retry|TODO|FIXME|mock|placeholder" relevant/path
rg -n "enabled|flag|premium|entitlement|permission|auth|role|policy" relevant/path
rg -n "role|type|kind|status|relationship|owner|client|side|represents|represented|belongsTo|parentId|sourceId" relevant/path
rg -n "fingerprint|proof|ready|complete|validated|export|manifest|prompt|AI|copyBlock|audit" relevant/path
```

---

## Phase 3: Find Feature Gaps

Look for feature-specific broken promises. Each candidate must be traced to what a real user sees.

### 3.1 Invalid product logic

Code produces valid data that is nonsensical for the user:
- Recommendations at impossible times or impossible amounts.
- Scores, debt, targets, or statuses with fake precision.
- Weighted averages that ignore schedule, context, locale, timezone, DST, currency, units, or user type.
- Confidence labels that reflect number of inputs instead of input quality.
- "Best" language applied to low-confidence or stale data.

### 3.2 Missing context and personalization

Feature claims personalization but uses generic fallback:
- Default values presented as user-specific guidance.
- Missing health/provider data treated as zero or normal.
- Onboarding answers collected but not used.
- Settings exist but do not influence output.
- Shift, travel, accessibility, locale, or edge schedules ignored.

### 3.3 State and freshness gaps

Feature state lies or drifts:
- Cached value survives after source changes.
- Store persists stale state across sign-out, account switch, provider disconnect, or app restart.
- Data refresh happens only on mount, not after relevant mutations.
- "Connected", "active", "synced", or "ready" shown without live/proven source.
- Optimistic UI has no rollback or reconciliation.

### 3.4 End-to-end integration gaps

Pieces exist but do not complete the feature:
- UI calls service but result never displayed.
- Backend returns shape UI does not expect.
- Events emitted but no listener updates user-visible state.
- Notification scheduled from old settings.
- Background sync writes data but derived feature never recalculates.
- Feature gate checks client state but server entitlement differs.

### 3.5 Failure and recovery gaps

User gets stuck or misled:
- Spinner or disabled button with no timeout/retry.
- Errors logged but not surfaced.
- Empty state hides backend/provider failure.
- Partial setup looks complete.
- Validation blocks action without explaining recovery.
- Offline path accepts changes but never syncs or warns.

### 3.6 Observability gaps

Team would not know feature is failing:
- No structured logs around critical transitions.
- No audit event for user-impacting state change.
- No metric for recommendation generation, notification scheduling, sync failure, entitlement mismatch, or stale-data display.
- Errors include sensitive data or omit diagnostic context.

### 3.7 Domain-model and relationship gaps

The feature stores data, but the model cannot represent the user's real situation:
- Real-world relationships are flattened into labels: "solicitor", "barrister", "witness",
  "court", "client", "admin", "guardian", or "provider" are stored as peers of the thing they
  should relate to.
- The UI asks for a role but not "for whom", "owned by whom", "acting for whom", "paid by whom",
  "approved by whom", or "source for what".
- The model has an optional relationship field but no validation that the referenced record exists,
  has the right type, or belongs to the same scope.
- A neutral or third-party actor can be treated as an adversary, customer, owner, patient, payer,
  account holder, or other primary actor.
- Draft/unresolved records look complete, active, ready, or safe.
- Legacy/default records are silently classified as "other" without a review surface before
  downstream use.

This is a feature gap even when CRUD works and the database schema is internally consistent.

### 3.8 Perspective and side-of-record gaps

The feature cannot answer whose side it is on:
- The app stores a client/user/account/member but does not link that person/entity to the thing the
  feature is acting on.
- The product collects persona, role, or onboarding context but does not connect it to the feature's
  source of truth.
- Recommendations, drafts, alerts, summaries, or workflow actions omit whether they are for the user,
  the counterparty, a dependent, a client, an admin, or a neutral reviewer.
- "Supporting", "opposing", "recommended", "risk", "ready", or "complete" is displayed without
  specifying the relevant perspective.
- The same data could be correct for one side and harmful for another.

For legal/litigation workflows specifically, audit claimant/defendant or equivalent sides, client
side, opponent side, solicitor/attorney, barrister/advocate/counsel, witness/expert, court/tribunal,
and instructing relationships as separate concepts.

### 3.9 Derived trust-surface gaps

The feature's raw data may be wrong or incomplete, but derived surfaces still treat it as safe:
- Completeness or readiness checks count "any value present" instead of "valid value for the
  user's workflow".
- Proofs, fingerprints, cache keys, ETags, or stale-state invalidation omit semantically material
  fields.
- Exports, manifests, reports, emails, copy blocks, or audit logs flatten structured relationships
  into a comma-separated list or omit them entirely.
- AI prompts, recommendations, scoring, or automation receive generic text but not the structured
  context required to produce safe output.
- Background jobs and generated artifacts persist metadata after generation, but did not provide
  that metadata to the generator.

When a feature has a trust claim ("ready", "GO", "reviewed", "client-safe", "court-ready",
"active", "verified", "synced", "complete"), trace every field that should invalidate that claim.

### 3.10 Test-suite semantic gaps

Passing tests can hide a broken feature contract:
- Tests assert labels, serialization, CRUD, or happy-path rendering but not real-world validity.
- Tests prove a relationship field round-trips but not that it is required, editable, role-correct,
  or used downstream.
- Tests assert "complete" or "ready" from minimal fixtures that would be invalid in a real workflow.
- Prompt tests check generic instructions/source bundles but not user-specific context.
- Export/proof tests check files exist or hashes change for obvious fields while omitting
  relationship, perspective, permission, entitlement, or context fields.

If focused tests pass while the audited promise is still false, report that as evidence: "the suite
accepts the broken contract." Recommend the smallest regression tests that would fail today.

---

## Phase 4: Verify Before Reporting

Do not report speculative gaps as facts. Verify strongest findings by reading code and, when practical, running the feature or tests.

Verification options:
- Focused unit/service/store tests.
- Typecheck/lint for edited or inspected areas when changes are made.
- Browser/simulator/device proof for UI, notifications, native health, payments, auth, routing, and background behavior.
- Live database/API inspection only through sanctioned project tools and only when needed.
- Harness/readiness commands when repository guidance requires them.
- Negative/semantic proof: construct or identify an invalid real-world state, then verify whether
  the feature accepts it, displays it as complete/ready, sends it into prompts/jobs, or exports it
  without warnings.
- Invalidation proof: change a semantically material relationship/context field and verify whether
  caches, readiness, proofs, generated artifacts, and exports become stale or blocked.

If verification is impossible, label finding as "needs runtime proof" and explain exactly what proof is missing.

---

## Phase 5: Report

Create a feature-specific audit report unless the user only asks for a verbal answer.

Preferred filename:
- `feature-gap-audit-[feature-slug].md` in project root, or
- project convention path such as `docs/audits/feature-gap-audit-[feature-slug].md` when audits already live there.

If updating an existing audit, preserve prior findings and add status: `open`, `partially addressed`, `refuted`, or `fixed`.

### Report template

```markdown
# Feature Gap Audit: [Feature Name]
**Date**: [date]
**Scope**: [specific screens/services/flows audited]
**Feature promise**: [one-sentence user-facing promise]

## Executive Summary
[2-4 sentences. Say whether feature is reliable, risky, partially working, or blocked by missing proof.]

## Feature Contract
| Promise | Expected behavior | Source |
|---------|-------------------|--------|
| [promise] | [expected] | [docs/UI/code/test] |

## Findings

### [Severity] [Finding Title]
- **Status**: open / partially addressed / refuted / fixed
- **Location**: `file:line`
- **User intent**: [what user is trying to do]
- **What happens instead**: [specific user-visible failure]
- **Why it matters**: [business/user impact]
- **Root cause**: [implementation or product logic issue]
- **How to verify**: [manual or automated reproduction]
- **Recommended fix**: [smallest production-safe fix]
- **Evidence**: [code path, data path, screenshots, logs, test output]

## Claimed vs Actual
| Capability | Actual status | Notes |
|------------|---------------|-------|
| [capability] | working / partial / broken / unverified | [details] |

## Domain Model / Trust Surface Matrix
| Concept or relationship | Captured at input? | Persisted? | Editable later? | Validated? | Used in prompts/jobs? | Included in proof/export? |
|-------------------------|--------------------|------------|-----------------|------------|-----------------------|---------------------------|
| [entity/relationship] | yes/no/partial | yes/no/partial | yes/no/partial | yes/no/partial | yes/no/partial | yes/no/partial |

## Verification Performed
- [commands, runtime checks, screenshots, logs]

## Verification Not Performed
- [what remains unproven and why]

## Recommended Next Slice
[smallest next implementation or proof step]
```

### Severity

- **Critical**: Core feature promise fails, causes data loss/security exposure, or gives harmful/misleading guidance in common use.
- **High**: Common user path produces wrong, stale, or incomplete result users will notice.
- **Medium**: Realistic edge case breaks or feature degrades without clear recovery.
- **Low**: Latent risk, weak observability, unclear copy, or unlikely edge case.

---

## Output Rules

- Lead with findings, not process.
- Separate "code appears correct" from "feature is proven in runtime."
- Separate "fixed locally" from "shipped/deployed/released."
- Use exact file and line references.
- State confidence for each finding when evidence is incomplete.
- Call out when tests pass but only prove storage, rendering, or happy-path mechanics rather than
  the user/product contract.
- Keep scope tight. If you discover adjacent product-wide risk, record it as a follow-up unless it directly breaks the audited feature.
- Do not soften user-impacting failures. If a feature can recommend nonsense, call it a feature gap even when the algorithm is internally consistent.

---

## When To Use Subagents

Use subagents when the feature spans multiple independent surfaces:
- UI/screen agent
- Store/state agent
- Backend/API/database agent
- Native/integration agent
- Test/evidence agent

After subagents report, verify important claims yourself by reading code. Deduplicate findings. Prefer fewer, well-proven findings over a long list of pattern matches.

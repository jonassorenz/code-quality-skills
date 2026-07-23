# Domain and Trust-Surface Contracts

Load this reference only for regulated, relationship-heavy, or generated-output features.

## Model real-world entities and relationships

Map:

- Primary entities that exist in the user's world.
- Roles that are attributes versus standalone entities.
- Relationships such as ownership, representation, client/opponent, payer/beneficiary,
  guardian/dependent, provider/patient, admin/member, source/derived output, and approver/action.
- Perspective: whom the product is acting for, speaking to, optimizing for, or protecting.
- Neutral actors such as courts, auditors, experts, support staff, regulators, and processors.
- Scope boundaries: tenant, case, household, account, organization, provider, or jurisdiction.
- Valid draft/unknown states and which actions they must block.

Treat a generic enum, string, picker, or “party/user/item” table as high risk when it collapses
concepts that drive permissions, recommendations, generated content, money, or legal responsibility.

## Trace relationship validity

Verify:

- The referenced entity exists and belongs to the same allowed scope.
- Its type is valid for the selected relationship.
- The relationship is required where downstream safety depends on it.
- Users can create, review, edit, and intentionally leave it unresolved.
- Legacy/default records are surfaced for review rather than silently classified.
- Neutral actors cannot be treated as ordinary owners, adversaries, customers, patients, payers,
  or beneficiaries.
- Permission and entitlement checks use authoritative server-side relationships where applicable.

## Preserve perspective

Trace whose side or interest every output represents. Flag outputs such as “supporting,”
“opposing,” “recommended,” “risk,” “complete,” or “ready” when they omit the relevant user,
client, counterparty, dependent, patient, payer, administrator, or neutral reviewer.

For legal workflows, model claimant/defendant or equivalent sides, client side, opponent side,
solicitor/attorney, barrister/advocate/counsel, witness/expert, court/tribunal, and instructing
relationships separately.

For medical workflows, distinguish patient, dependent, guardian, clinician, organization, payer,
data source, and recommendation recipient.

For financial workflows, distinguish owner, account holder, payer, beneficiary, approver,
counterparty, currency, jurisdiction, and source of truth.

## Audit derived trust surfaces

Trace semantically material fields into:

- Completeness, readiness, eligibility, confidence, and risk calculations.
- Cache keys, stale-state invalidation, fingerprints, proofs, and ETags.
- AI prompts, recommendations, scores, and automation.
- Background jobs and generated artifacts.
- Exports, manifests, reports, emails, copy blocks, and audit logs.

Flag cases where:

- “Any value present” is treated as a valid relationship.
- Structured relationships are flattened or omitted downstream.
- Metadata is saved after generation but was not provided to the generator.
- Changing a material relationship does not invalidate derived output.
- An unresolved or stale record still appears active, safe, verified, or complete.

## Semantic test requirements

Do not accept a round-trip or rendering test as proof of a domain contract. Add or recommend tests
that prove:

- Invalid cross-scope and role-incompatible relationships are rejected.
- Required relationships block readiness/action when absent.
- Users can correct unresolved or legacy records.
- Perspective-specific outputs change when perspective changes.
- Prompts/jobs receive the structured context they require.
- Exports and proofs include material relationships.
- Changing a material field invalidates caches and generated outputs.

If existing focused tests pass while these invariants are false, record that the suite accepts the
broken contract.

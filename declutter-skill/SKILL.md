---
name: declutter
description: Finds and removes unnecessary code and unnecessary complexity across a codebase — dead code, duplication, over-abstraction, speculative generality, config and dependency rot — then verifies the build stays green. Use this skill whenever the user wants to clean up, simplify, slim down, or declutter a codebase or project, reduce technical debt, remove dead/unused/redundant code, prune bloat, fix over-engineering, or do a code quality or hygiene sweep. Trigger on phrases like "declutter", "clean up this codebase", "remove dead code", "too complex", "over-engineered", "simplify this project", "code bloat", "slop", "technical debt", "redundant code", "prune", "tidy up", or "this codebase is a mess" — even when the user doesn't say exactly what should go. For diagnosing why a specific subsystem is broken (not cleaning it up), use whats-wrong instead; for polishing style in code that was just written, use code-simplifier instead.
---

# Declutter

Code is a liability, not an asset. Every line costs reading, searching, compiling, testing, and understanding — forever. This skill hunts two kinds of rot:

1. **Code that does nothing** — dead files, unused exports, orphan config, dependencies nobody imports. Pure cost, zero value.
2. **Code that costs more than it's worth** — duplicated logic, abstractions serving one caller, options nobody sets, layers that only pass things through. It *works*, but every future change pays a tax on it.

The counterweight: some complexity is load-bearing. A system that handles genuinely messy requirements will have genuinely intricate parts, and flattening those creates bugs, not clarity. The core skill you're applying here is telling the difference — removal should leave the codebase saying the same things with fewer moving parts, never saying fewer things.

## The one rule

**Never delete or flatten code you can't explain.** For every candidate, you must be able to say in one sentence why it's safe to remove and why the codebase is better without it. If the sentence is "it looks unused" or "it seems too abstract," you don't have evidence yet — you have a hunch. Hunches go in the report, not the diff. Removing code someone deliberately kept is far worse than leaving clutter behind, because it destroys trust in every future cleanup.

## Workflow

Five phases: **Scope → Hunt → Verify → Propose → Execute**. The phases are the same whether you're sweeping a whole codebase or one module — only the scale changes.

---

### Phase 1: Scope

Before hunting anything, establish the terrain. Skipping this is how false positives happen.

**Clarify the ask.** Full-codebase sweep, a scoped area ("the auth module"), or a specific concern ("I think we have lots of duplicate utilities")? Scope code analysis to what they asked for, but always read intent documentation repo-wide — plans can live anywhere.

**Check git state.** A clean tree is strongly preferred — removals are much easier to review and revert from a clean baseline. If there are uncommitted changes, ask the user to commit or stash first; if they say proceed anyway, note it and be extra careful not to entangle your changes with theirs.

**Detect the project.** Read the manifests (`package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, `Package.swift`, etc.) and extract:
- Entry points — `main`, `bin`, `scripts`, `exports`. Alive by definition.
- Framework — Next.js, Rails, Django, Expo... each has conventions for invoking code without explicit imports (routes, pages/, lifecycle hooks, registered handlers). Know these *before* flagging anything.
- Build, typecheck, and test commands — you'll need them in Phase 5.
- Source root(s) and what to exclude: node_modules, build output, generated code, vendor dirs.

**Check available tooling.** Language tooling finds candidates far more reliably than grep. See `references/hunt-playbooks.md` for the per-language tool table. If a tool isn't installed, don't install anything without asking — grep-based fallback still catches most real issues.

**Read the intent docs.** Read `README.md`, `CLAUDE.md`, `AGENTS.md`, plus any `ROADMAP`, `TODO`, `PLAN`, `MIGRATION`, `ARCHITECTURE`, or `CHANGELOG` files. Build a **protected list**: anything documented as planned, intended, in-progress, or deliberately kept. This list overrides everything you find later. Scan the names of other `.md` files and read any whose names suggest code intent. If a specific candidate is ambiguous later, come back and read more docs at that point rather than front-loading everything.

**Size up the codebase** — rough file and line counts. This drives the Hunt strategy below.

---

### Phase 2: Hunt

You're looking for five categories of rot. The detection recipes per category and per language live in `references/hunt-playbooks.md` — read it before starting.

| # | Category | The smell |
|---|----------|-----------|
| 1 | **Dead code** | Unused files, exports, functions, variables, imports; unreachable branches; commented-out blocks |
| 2 | **Duplication** | Copy-pasted logic, parallel utility implementations, types defined in multiple places |
| 3 | **Over-abstraction** | Interfaces/classes with one implementation and no second in sight, pass-through wrappers, indirection that hides a one-liner |
| 4 | **Speculative generality** | Config options never set, parameters always passed the same value, "flexible" machinery used one way, feature-flag debris |
| 5 | **Config & dependency rot** | Zombie config for tools no longer used, unused dependencies, unreferenced env vars, duplicated config values |

**Adaptive execution — match the strategy to the size:**

- **Small** (scoped request, or under ~100 source files): hunt yourself, one focused pass, category by category.
- **Large**: spawn parallel subagents — one per category above — as **read-only hunters**. Each writes its findings to `DECLUTTER-N-<category>.md` in the project root (or a `.declutter/` scratch dir you create), with `file:line`, evidence, and confidence per finding. Then you merge and dedupe their lists.

Do not let parallel agents modify code. Parallel writers are where cleanup skills go to die: overlapping edits, merge conflicts, and half-applied changes that break the build in ways nobody can attribute. Hunting parallelizes beautifully — it's independent and read-only. Fixing does not, because every change must be verified against the build in a known order. Fan out for the search, line up single-file for the surgery.

For large hunts, give each agent: the project context from Phase 1 (stack, source root, exclusions, entry points, available tools), the protected list, its category's playbook section, and the instruction to search the *full* repo when checking references — something unused in one module is often imported by a sibling.

---

### Phase 3: Verify

Every candidate passes through a gate before it reaches the report. The gate is different for the two kinds of rot.

**For removals** (categories 1, 5 — "this does nothing"), check each candidate against ALL of these. Any failure demotes it to "flagged":

1. **Zero references confirmed** — grep with multiple patterns (bare name, qualified `Class.method`, string forms) returns nothing outside the definition. Use LSP find-references when available — it sees namespacing and type-level references grep can't.
2. **Not on the protected list** — no doc mentions intent to keep or use it.
3. **Not public API** — not exported from a package boundary (`exports` field, `__all__`, podspec, etc.) that external consumers might use.
4. **Not dynamically referenced** — no bracket-notation access, `getattr`, string-based registries, DI containers, plugin systems, config files naming it.
5. **Not framework-invoked** — not a route handler, lifecycle hook, page component, event listener, serializer, test fixture, decorator target, or CLI registration.
6. **No intent comments nearby** — no TODO / "keep" / "needed for" / "will use" within a few lines.
7. **Not a contract requirement** — not a method an interface/protocol requires even if never called directly.

While verifying, note what each dead candidate *calls* — you'll need it for cascade detection in Phase 5 (a helper used only by a dead function becomes dead itself).

**For simplifications** (categories 2, 3, 4 — "this costs more than it's worth"), apply a different test: **sketch the simpler version.** Concretely — the consolidated function, the inlined call, the deleted layer. Then ask:

- Is the simpler version obviously easier to understand for someone who has seen neither? If you have to *argue* it's simpler, it isn't — flag it instead.
- Does the abstraction earn its keep? Two similar call sites is usually fine to leave duplicated (the rule of three); an interface with one implementation is fine *if* a second is genuinely imminent (check the protected list).
- Is this complexity load-bearing? Validation at trust boundaries (user input, network responses, external APIs) is not defensive clutter — it's the job. A "redundant" check that guards a real failure mode stays.
- Would removing it delete information? Error messages, logging context, and type specificity are often hidden value in verbose code.

**Confidence levels** — every verified finding gets one:

- **HIGH** — implement on approval. Obvious, verifiable: exact duplicates, unused imports, compiler-flagged dead code, commented-out blocks, unused deps.
- **MEDIUM** — implement only if the build and tests verify it. Similar-but-not-identical consolidations, abstractions whose second implementation "might" exist.
- **LOW** — report only, never implement without explicit per-item approval. Anything touching public APIs, dynamic dispatch, or domain knowledge you don't have.

---

### Phase 4: Propose

Present the plan *before touching code*, organized for decision-making:

```
## Declutter Plan

Found **N actionable items** and **M flagged for your judgment** across K files.

### Quick wins (high confidence, low risk)
- Delete `src/api/v1.ts` — nothing imports it, not a route, no docs mention it
- Consolidate 3 copies of `formatDate()` → keep `utils/date.ts`, delete the rest
- Remove 8 unused imports across 5 files
- Drop `lodash` from dependencies — zero imports anywhere

### Bigger efforts (worth it, but need care)
- Collapse `BaseRepository` + its single impl `UserRepository` → plain functions;
  the interface exists for a plugin system that was never built
- `SettingsContext` stores 14 values, 9 are only ever read in one component
  each → move state next to its consumers

### Dangerous simplifications (need your explicit call)
- `hashWithSalt()` has zero callers BUT is named in the v2 migration plan — keep?
- `legacyCheckout()` looks dead but the payments webhook may invoke it by
  string name — verify with someone who knows the integration

### Flagged, not touching
- [LOW-confidence items with the reason each is ambiguous]
```

"Go ahead" means quick wins only. Bigger efforts and dangerous items need explicit per-item approval. Respect a "just do 1 and 3" scope instantly — the full sweep is a default, not an obligation.

---

### Phase 5: Execute

**Order of operations** — this order minimizes breakage and makes failures attributable:

1. **Removals first** (dead code, unused deps, zombie config) — deleting rarely conflicts with anything.
2. **Structural changes** (consolidating duplicates, moving types to shared modules) — these touch imports across the codebase.
3. **Simplifications** (collapsing abstractions, inlining wrappers) — these touch the most existing logic.

**Work in small batches** of 3–5 related items (e.g., a dead file plus the helpers only it used). After each batch:

1. **Cascade check** — from your Phase 3 dependency notes, did anything become newly dead? A helper used only by what you just removed goes into the next batch.
2. **Clean the wounds** — remove leftover blank lines, empty files, dangling re-exports, now-empty barrels (`index.ts` that re-exports nothing).
3. **Verify the build** — run the typecheck/build command from Phase 1. If it fails, the last batch ate something alive: revert the batch, bisect it, move the culprit to "flagged."

Only proceed to the next batch on green. **After all batches, run the full test suite.** If tests fail, identify the removal from the diff, revert just that change, and flag it.

If you're deleting a dependency, also grep for it in config files, build scripts, and CI workflows before removing it from the manifest — deps used only by tooling don't show up in source imports.

---

### Phase 6: Report

Close with a short, honest summary:

```
## Declutter Complete

Removed N items across K files (~X lines):
- 2 dead files deleted, 5 unused functions, 8 unused imports
- 3 duplicate utilities consolidated into utils/date.ts
- 1 abstraction collapsed (BaseRepository)
- lodash removed from dependencies

Build: passing · Tests: passing (or: no test suite found)
Still flagged for you: 3 items (see above)
```

If anything was skipped or reverted mid-flight, say so plainly — a cleanup that silently dropped items is worse than no cleanup.

---

## Edge cases that bite

- **Dynamic imports** — `import(variable)`, `importlib.import_module()` won't appear in static search. Check for dynamic import patterns before declaring a module dead.
- **String-registered code** — DI containers, plugin registries, service locators. Registered ≠ imported.
- **Monorepos** — "unused" in one package may be imported by a sibling. Always search the whole repo.
- **Build-time references** — webpack loaders, Babel plugins, codegen configs reference files grep thinks are orphans.
- **Re-export chains** — intermediate barrels look unused when they're the public API surface.
- **Feature flags & conditional compilation** — disabled in dev may mean live in production.
- **Ugly but stable** — working code that's rarely touched and merely inelegant is often fine to leave. Churn has a cost too; don't manufacture diffs for their own sake. When in doubt, list it under "flagged" with the note "cosmetic only."

## What this skill is not

- **Not a bug hunt.** If the user wants to know why a subsystem is broken or mediocre, that's a diagnosis job (`whats-wrong`), not a cleanup.
- **Not a style pass.** Formatting, naming preferences, and polishing freshly-written code belong to `code-simplifier` or a formatter. Declutter removes and consolidates; it doesn't repaint.
- **Not a rewrite.** If the honest answer to "what would simpler look like?" is "a different architecture," say that in the report — don't start one.

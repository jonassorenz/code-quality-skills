# Hunt Playbooks

Detection recipes for each category of rot, plus the per-language tooling table. Read this before Phase 2. When hunting a large codebase with parallel agents, give each agent its category's section verbatim plus the project context.

**Contents**
- Language tooling table
- Playbook 1: Dead code
- Playbook 2: Duplication
- Playbook 3: Over-abstraction
- Playbook 4: Speculative generality
- Playbook 5: Config & dependency rot
- Findings file format (for parallel agents)

---

## Language tooling table

Check what's installed before choosing a detection strategy (`which <tool>` or `npx <tool> --version`). Compiler/linter output understands scope and semantics; grep doesn't. Don't install tools without asking the user — every recipe below has a manual fallback.

| Stack | Dead code | Duplication | Dependencies | Types/imports |
|-------|-----------|-------------|--------------|----------------|
| TypeScript/JS | `tsc --noUnusedLocals --noUnusedParameters --noEmit`, `npx knip` | `npx jscpd`, grep for known util names | `npx depcheck`, knip | `npx madge --circular` (cycles), eslint `no-unused-vars` |
| Python | `vulture .`, `pyflakes .` | `pylint --disable=all --enable=duplicate-code` | `pipreqs` diff vs manifest | `import-linter`, `pydeps` |
| Rust | `cargo check` warnings (`dead_code`), `cargo-udeps` | `cargo clippy` (partial) | `cargo-udeps`, `cargo-machete` | clippy lints |
| Go | `staticcheck ./...` (U1000), `go vet` | `dupl` | `go mod tidy` diff | `gopls` references |
| Swift | `xcodebuild` warnings (`unused`, `never used`), periphery | manual | manual | index-store via periphery |
| Ruby | `debride`, coverband (runtime) | `flay` | `bundle clean` manual | manual |

If the project uses something else, spend two minutes researching the ecosystem's standard dead-code and lint tooling before falling back to grep.

**Grep-based fallback** (works anywhere): prioritize with git history —

```bash
git log --diff-filter=M --name-only --since="6 months ago" --pretty=format:"" | sort -u
```

Files NOT in this list haven't been touched recently — old untouched files accumulate rot fastest. Triage, not verdict: stable-and-referenced old code is alive.

---

## Playbook 1: Dead code

**What you're finding:** unused files, unused exports, unused internal functions, unused variables/constants, unused imports, unreachable code, commented-out code blocks.

**With tooling:** run the dead-code tool for the stack, parse output into a candidate list. Compiler candidates start at high confidence but still need the Phase 3 verification gate — the compiler doesn't know about your docs or dynamic dispatch.

**Manually:**

1. Start with the oldest untouched files (git triage above). For each, list exported symbols, then grep each symbol repo-wide: bare name, `Module.symbol`, string forms. Definition-site-only = candidate.
2. Orphan files: for each source file, grep `import.*filename|from.*filename|require.*filename`. Zero inbound + not an entry point / route / config = strong candidate.
3. Commented-out code: multi-line comment blocks containing code syntax (function defs, assignments, control flow). Distinguish from documentation comments — you want blocks that were once live.
4. Unreachable code: after unconditional `return`/`throw`/`break`, inside branches like `if (false)` or impossible condition combinations.

**Also record:** what each candidate imports or calls. This feeds cascade detection later — dead code often hides more dead code behind it.

**Priority order for a full sweep** (biggest wins first): unused files → unused exports → unused internal functions → unused variables → unused imports → commented-out code.

---

## Playbook 2: Duplication

**What you're finding:** the same logic implemented in multiple places.

Forms it takes:

- **Copy-pasted functions** — same body, maybe renamed. Search for distinctive lines from one implementation across the repo.
- **Parallel utilities** — `formatDate` in three files, each slightly different. Grep for high-risk name stems: `format`, `parse`, `validate`, `build`, `convert`, `normalize`, `sanitize`, `slug`, `truncate`, `debounce`.
- **Duplicate type definitions** — same interface/struct/type defined in multiple files instead of shared. Grep for `interface User`, `type Config`, struct names.
- **Repeated call patterns** — the same 4-line fetch-and-handle-error sequence in every API function (candidate for one helper), the same auth check in every handler (candidate for middleware).
- **Near-duplicates with drift** — copies that have diverged slightly. These are the dangerous ones: somebody fixed a bug in one copy. Note *which* copy looks newer/correct.

**The judgment call:** consolidation is only a win when the copies are doing the same job for the same reason. Two similar functions serving different domains ("format date for display" vs "format date for filename") will drift apart — merging them creates a coupling problem worse than the duplication. When copies have already drifted, the finding is "reconcile the drift, then consolidate," which is a bigger effort — say so.

**Rule of three:** two instances is often coincidence, three is a pattern. Don't flag pairs unless they're exact duplicates or long.

---

## Playbook 3: Over-abstraction

**What you're finding:** indirection that costs more than it saves.

Forms it takes:

- **Single-implementation abstractions** — interface/base class/protocol with exactly one implementation, and no second on any roadmap (check the protected list!). The interface file, the impl file, the DI wiring: three things to read where one function would do.
- **Pass-through layers** — functions/methods that just call another with the same arguments and add nothing (no validation, no transformation, no error handling). `function getUser(id) { return userService.getUser(id); }`
- **Wrapper-for-wrapper** — a "service" that's a thin class over a library call, a hook that returns one useState, a "manager" that delegates everything.
- **Premature generalization** — a recursive tree-walking config resolver where the config has never had more than one level; a plugin architecture with one plugin.
- **Barrel explosion** — `index.ts` files that re-export hundreds of symbols, forcing readers through an extra hop and hiding what's actually public.

**The test:** for each candidate, write the one-sentence answer to "what would I lose by inlining this?" If the honest answer is "a file hop," it's rot. If it's "the seam we'd use to swap implementations when X lands" and X is in the docs, it's protected — move on.

**Careful:** abstraction boundaries that match real architectural seams (API client layer, database access layer, platform adapters in cross-platform apps) earn their keep even with one implementation today — they're where change is expected to arrive. Flag these rather than collapsing them.

---

## Playbook 4: Speculative generality

**What you're finding:** machinery built for variation that never came.

Forms it takes:

- **Parameters always passed the same value** — `render(items, { sort: true })` at every call site, or a `mode` argument that's always `"default"`. Grep the call sites; if N of N agree, the parameter is a lie.
- **Config options never set** — settings with defaults that nothing ever overrides, env vars with one value in every environment file.
- **Feature-flag debris** — flags that have been permanently on (or off) for months. `if (flags.newCheckout)` where `newCheckout` shipped last year. Both the flag lookup AND the dead branch are rot.
- **Unused type parameters** — generics instantiated with exactly one type everywhere.
- **Over-complete CRUD** — update and delete endpoints for entities that are only ever created and read.
- **Switch statements with one real case.**

**The test:** count actual variations in the code and config. Zero or one variation = candidate. Before flagging, check the intent docs — a planned second variation is a reason to keep.

**Note:** generality at a *public* boundary (an SDK, a published package, a plugin API consumed externally) is different — consumers you can't see may use it. Those go to "flagged," never auto-removed.

---

## Playbook 5: Config & dependency rot

**What you're finding:** project-level clutter outside source files.

- **Unused dependencies** — for each dep in the manifest, grep imports/requires across source AND check build scripts, config files, and CI workflows (deps used only by tooling are still used). `depcheck` / `cargo-machete` automate the source half.
- **Zombie config** — config files for tools no longer present: a Jest config in a Vitest project, `.eslintrc` after migrating to Biome, CI config for a service you no longer use. Cross-reference every config file against the manifest and docs.
- **Unreferenced env vars** — vars in `.env.example` / env schema that never appear in code (grep the var name). Also the reverse: vars referenced in code but missing from the example file (that's a bug, note it separately).
- **Duplicated config values** — the same constant (a URL, a timeout, a bucket name) hardcoded in multiple files instead of one config module.
- **Dead scripts** — package.json scripts pointing at files that no longer exist, CI jobs testing things that were deleted.
- **Stale build config** — bundler aliases for deleted directories, tsconfig paths pointing nowhere, ignore-files listing paths that don't exist.

**Careful:** some config is intentionally unused-in-code (editor settings, gitattributes, licensing). And a dependency with zero imports might be a peer requirement or a runtime plugin — check the docs of anything unfamiliar before flagging it as unused. When unsure, flag; dependency removal breaks builds in ways that only show up at install/deploy time.

---

## Findings file format (parallel agents)

Each hunter agent writes one file: `DECLUTTER-N-<category>.md` (N = category number), in the project root or the scratch dir you designate. Unique filenames — other agents are writing concurrently.

```markdown
# Findings: <category>

## HIGH confidence
- `path/to/file.ts:42` — <what> — <evidence: "zero references repo-wide (grep: foo, Module.foo, 'foo')">
  Suggested action: <delete / consolidate into X / inline>

## MEDIUM confidence
- `path:line` — <what> — <evidence + why it's not certain>
  Suggested action: <...> — verify with <build/tests/specific check>

## LOW confidence (report only)
- `path:line` — <what> — <why it needs human judgment>

## Notes
- <cascade hints: "helper X is only called by dead function Y">
- <tools that were unavailable and what they would have caught>
```

Instruct agents to be **read-only**: no source modifications, no file moves. Evidence is mandatory per finding — "seems unused" without the grep patterns tried is not a finding, it's a rumor.

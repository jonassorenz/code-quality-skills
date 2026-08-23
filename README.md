# Code Quality Skills

A cross-agent collection of production-focused code quality, runtime QA, and audit skills.

## Included Skills

| Skill | Description |
|-------|-------------|
| `declutter` | Finds and removes unnecessary code and complexity — dead code, duplication, over-abstraction, speculative generality, config/dependency rot — with verified, build-safe execution |
| `production-gap-auditor` | Risk-weighted whole-product audit with static tracing, runtime scenarios, evidence levels, and optional verified repair |
| `feature-gap-auditor` | Deep audit of one feature promise from source through controlled runtime, with optional verified repair |
| `compliance-audit` | GDPR/HIPAA/privacy audit for consent, PHI/PII, retention, erasure, portability, breach, and user-data handling |
| `whats-wrong` | Focused subsystem diagnosis for auth, payments, notifications, search, onboarding, and similar product areas |
| `bug-hunter` | Runtime QA that drives a live app with computer-use or browser automation and reports bugs with evidence |

> `declutter` replaces the retired `slop-remover`, `dead-code-removal`, and `complexity-audit` skills, consolidating them into a single hunt → verify → propose → execute pipeline.

## Installation

These skills are plain `SKILL.md` files with YAML frontmatter — they work with any agent framework that supports skills (Claude Code, Gemini CLI, Codex, Cursor, Copilot CLI, etc.).

### Install via npx (any agent)

```bash
# List available skills
npx code-quality-skills list

# Install one skill (defaults to Claude, user scope)
npx code-quality-skills install bug-hunter

# Install to a different agent
npx code-quality-skills install declutter --agent gemini
npx code-quality-skills install production-gap-auditor --agent cursor

# Install to project scope instead of user scope
npx code-quality-skills install declutter --scope project

# Install everything
npx code-quality-skills install-all --agent claude
```

**Supported agents:** `claude`, `agents`, `gemini`, `codex`, `cursor`, `copilot`
**Scopes:** `user` (default, global) or `project` (local `.{agent}/skills/`)

> Prefer not to install from npm? The same CLI runs directly from GitHub:
> `npx github:jonassorenz/code-quality-skills install <skill>`

### Install via Claude Code CLI

For Claude Code specifically, you can also use the bundled `.skill` packages:

```bash
claude install-skill https://raw.githubusercontent.com/jonassorenz/code-quality-skills/main/bug-hunter-skill/bug-hunter.skill
claude install-skill https://raw.githubusercontent.com/jonassorenz/code-quality-skills/main/declutter-skill/declutter.skill
claude install-skill https://raw.githubusercontent.com/jonassorenz/code-quality-skills/main/compliance-audit-skill/compliance-audit.skill
claude install-skill https://raw.githubusercontent.com/jonassorenz/code-quality-skills/main/feature-gap-auditor-skill/feature-gap-auditor.skill
claude install-skill https://raw.githubusercontent.com/jonassorenz/code-quality-skills/main/production-gap-auditor-skill/production-gap-auditor.skill
claude install-skill https://raw.githubusercontent.com/jonassorenz/code-quality-skills/main/whats-wrong-skills/whats-wrong.skill
```

### Manual install

Each subdirectory is a standalone skill. Copy the skill's folder into your agent's skills directory:

| Agent | User scope | Project scope |
|-------|------------|---------------|
| Claude Code | `~/.claude/skills/<name>/` | `.claude/skills/<name>/` |
| Agents-compatible | `~/.agents/skills/<name>/` | `.agents/skills/<name>/` |
| Gemini CLI | `~/.gemini/skills/<name>/` | `.gemini/skills/<name>/` |
| Codex | `~/.codex/skills/<name>/` | `.codex/skills/<name>/` |
| Cursor | `~/.cursor/skills/<name>/` | `.cursor/skills/<name>/` |
| Copilot CLI | `~/.copilot/skills/<name>/` | `.copilot/skills/<name>/` |

> Refer to each skill's `SKILL.md` for usage details.

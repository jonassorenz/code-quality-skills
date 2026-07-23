# Candidate Search Patterns

Use searches only to generate `E0` candidates. Trace reachability and user impact before reporting
anything.

Prefer the deterministic scanner:

```bash
python3 <skill-dir>/scripts/scan_candidates.py <repo-root> --format text
```

It excludes dependency, generated, build, fixture, snapshot, and test trees by default. Pass
`--include-tests` only when auditing test semantics.

## Safe fallback searches

Use `rg` with explicit file scopes and exclusions. These commands avoid unsupported lookarounds.

```bash
rg -n -U --pcre2 'catch\s*\([^)]*\)\s*\{\s*\}|\.catch\s*\(\s*\(\s*\)\s*=>\s*\{\s*\}\s*\)' src app lib server
rg -n 'TODO|FIXME|HACK|XXX|NOCOMMIT|STOPSHIP|NotImplemented|not implemented' src app lib server
rg -n 'fallback|default|stale|retry|timeout|rollback|reconcile|idempot|dedup' src app lib server
rg -n 'isLoading|loading|spinner|pending|disabled|empty state|Something went wrong' src app
rg -n 'localStorage|Access-Control-Allow-Origin|allowOrigin|skipAuth|noAuth|AllowAnonymous|rate.?limit' src app server
rg -n 'setInterval|setTimeout|addEventListener|subscribe|WebSocket|useEffect' src app lib server
rg -n 'process\.env|import\.meta\.env|os\.environ|os\.getenv|env::var|System\.getenv' .
rg -n 'webhook|callback|redirect_uri|redirectUri|oauth|deep.?link|notification|entitlement|permission' src app server
```

Adjust directories to the repository. Exclude `node_modules`, vendored code, generated output,
coverage, snapshots, fixtures, and build directories.

## Language-specific candidates

### JavaScript and TypeScript

```bash
rg -n -U --pcre2 'catch\s*\([^)]*\)\s*\{\s*(?:console\.(?:log|warn|error)\([^;]*\);?\s*)?\}' src app server
rg -n 'Promise\.all|forEach\(.*async|map\(.*async|void [A-Za-z_$].*\(' src app server
rg -n 'useEffect|addEventListener|removeEventListener|subscribe|unsubscribe|AbortController' src app
```

Read the whole function. Logging-only catches can still update state or deliberately isolate optional
telemetry. Async collection patterns are not automatically incorrect.

### Python

```bash
rg -n -U --pcre2 'except(?:\s+[^:\n]+)?\s*:\s*(?:#.*\n\s*)?pass\b' .
rg -n 'NotImplementedError|TODO|FIXME|session\.commit|session\.rollback|transaction' .
```

### Go

```bash
rg -n 'TODO|FIXME|panic\("not implemented"\)|_\s*=\s*[^=]' --glob '*.go'
rg -n 'go func|defer |context\.WithTimeout|BeginTx|Rollback|Commit' --glob '*.go'
```

Never infer an ignored error from proximity alone; read the containing statement and control flow.

### Rust

```bash
rg -n 'todo!\(|unimplemented!\(|let _ =|\.ok\(\)|\.unwrap\(\)' --glob '*.rs'
rg -n 'transaction|commit|rollback|spawn|timeout' --glob '*.rs'
```

Exclude tests before judging `unwrap()`.

### Java and Kotlin

```bash
rg -n -U --pcre2 'catch\s*\([^)]*\)\s*\{\s*\}' --glob '*.java' --glob '*.kt'
rg -n 'UnsupportedOperationException|NotImplementedException|TODO|FIXME' --glob '*.java' --glob '*.kt'
```

### Swift

```bash
rg -n 'try\?|try!|fatalError\(|TODO|FIXME|Task\s*\{|NotificationCenter|Timer\.' --glob '*.swift'
rg -n '@AppStorage|UserDefaults|Keychain|scenePhase|onOpenURL|UNUserNotificationCenter' --glob '*.swift'
```

### SQL and schemas

```bash
rg -n 'ON DELETE|FOREIGN KEY|REFERENCES|BEGIN|COMMIT|ROLLBACK|CREATE INDEX|UNIQUE' --glob '*.sql'
rg -n 'SELECT \*' --glob '*.sql'
```

Do not claim an unbounded query merely because a SQL line lacks `LIMIT`; inspect the full query,
caller constraints, cursor/pagination strategy, and dataset bounds.

---
name: audit
description: "Audit a project for compliance with the standards in docs/project-standards.md. Use this skill whenever the user asks to audit, check, or validate a project against standards — including phrases like 'does this project comply', 'check project standards', 'what's missing', 'run the audit', or '/audit'. Always invoke this when the user wants a compliance report for any repository."
---

# Project Standards Audit

Systematically check a project against the standards defined in `docs/project-standards.md` and produce a structured compliance report.

## Invocation

- `/audit` — audit the current working directory
- `/audit <path>` — audit the project at the given path

## Standards Reference

The full standards live in `docs/project-standards.md` (relative to THIS repo, not the target project). Read it fresh at the start of each audit so the check is always up to date. The standards currently cover five areas:

1. README.md
2. docs/PURPOSE.md
3. .gitignore
4. Justfile
5. .github/workflows/ci.yml

## Audit Process

### Step 1 — Resolve the target

If a path was given, use it. Otherwise use the current working directory. State the project being audited at the top of your report.

### Step 2 — Read the standards

Read `docs/project-standards.md` from THIS repo (the skills repo at the path you were invoked from). Do this before reading target files so you have the current standard in mind.

### Step 3 — Check each area

For each of the five areas below, check whether the file exists and whether its contents satisfy every requirement in the standard. Use Read for small files; for larger files (CI workflow, etc.) focus on the specific things the standard calls out.

**README.md**
- File exists
- Has project name and one-sentence description
- Lists prerequisites (runtime versions, required environment variables)
- Has a quickstart command (`just dev` or equivalent)
- Links to `docs/PURPOSE.md`
- States a license

**docs/PURPOSE.md**
- File exists
- Has a "problem being solved" section (1–3 paragraphs)
- Explicitly lists non-goals
- States the intended audience or users

**.gitignore**
- File exists
- Covers language/runtime artifacts (build output, `__pycache__`, `node_modules`, `target/`, etc.) — check what languages the project uses and verify relevant entries are present
- Ignores `.env` and `.env.*` variants
- Ignores IDE directories (`.idea/`, `.vscode/`)
- Ignores OS files (`.DS_Store`, `Thumbs.db`)
- Ignores local-only config (e.g., `settings.local.json`)

**Justfile**
- File exists
- Has a header comment `# <project-name> — <one-line description>`
- `default` recipe is first and uses exactly `@just --list`
- Has all required recipes: `install`, `check`, `lint`, `fix`, `typecheck`, `test`, `clean`, `fresh`
- For runnable apps (not libraries): also has `run` and `dev`
- For containerized apps: also has `docker-build`, `docker-run`, `docker-push`
- For deployable apps: also has `deploy` (and `deploy-staging` if staging exists)
- `check` depends on `lint typecheck test` (may omit `test` only if no tests exist)
- `lint` is read-only; `fix` is write-mode — not a single combined recipe
- No hyphens in recipe names (`typecheck` not `type-check`)
- `fresh` (not `reinstall` or `reset`) depends on `clean install`
- Each recipe has a comment on the line immediately above it (no blank line between comment and recipe)
- One blank line between recipes
- No `set` declarations or variables unless clearly needed

**.github/workflows/ci.yml**
- File exists (check for any `.github/workflows/*.yml` if the exact name differs)
- Triggers on `push` to `main` and all pull requests
- Has at least two jobs: lint (runs first) and test (runs after lint)
- All action versions are pinned to a specific tag (not `@latest`)
- `actions/checkout` is v6 or newer
- Has a multi-platform or multi-version test matrix where the runtime warrants it

### Step 4 — Produce the report

Use this exact format for the report:

```
## Project Standards Audit: <project-name>
Audited: <absolute path>

### README.md         [PASS | FAIL | MISSING]
- OK   Has project name and description
- FAIL Missing prerequisites section
- OK   Quickstart command present (just dev)
- FAIL No link to docs/PURPOSE.md
- OK   License stated (MIT)

### docs/PURPOSE.md   [PASS | FAIL | MISSING]
...

### .gitignore        [PASS | FAIL | MISSING]
...

### Justfile          [PASS | FAIL | MISSING]
...

### CI workflow       [PASS | FAIL | MISSING]
...

---
Summary: X/5 areas passing
Critical gaps: <one-line list of the most important missing things, or "none">
```

Each item in a section is either `OK` (compliant) or `FAIL` (violation or missing). Section header shows `PASS` if all items are OK, `FAIL` if any item fails, `MISSING` if the file doesn't exist at all (counts as all items failing).

### Step 5 — Offer to fix

After the report, ask: "Would you like me to fix any of these issues?"

If the user says yes (or gives a specific list), apply fixes:
- For missing files, create them from scratch following the standard
- For existing files with gaps, use Edit to add missing content
- After fixing, re-audit only the changed areas and confirm they now pass
- If something requires human input (e.g., the actual purpose statement), scaffold a template and mark the sections with `<!-- TODO: fill in -->`

## Judgment calls

- If a README has a prerequisites section but it's vague (e.g., "Node.js" with no version), mark it FAIL with a note.
- For .gitignore, look at what languages/tools the project actually uses (check package.json, go.mod, Cargo.toml, etc.) and only flag missing entries that are relevant to the project.
- For CI: if the workflow file has a different name, still check it. If there are multiple workflow files, audit the one most likely to be the main CI gate.
- For Justfile app-type classification: look at whether the project has a start script, server code, or deployment config — if yes, treat it as an app; if it's a pure library or tool, omit `run`/`dev`.

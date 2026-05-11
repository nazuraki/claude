---
name: audit
description: "Audit a project for compliance with project standards — files AND GitHub repository settings. Use this skill whenever the user asks to audit, check, or validate a project against standards — including phrases like 'does this project comply', 'check project standards', 'what's missing', 'run the audit', or '/audit'."
---

# Project Standards Audit

Systematically check a project against all standards and produce a structured compliance report.

## Invocation

- `/audit` — audit the current working directory
- `/audit <path>` — audit the project at the given path

## Audit Process

### Step 1 — Resolve the target

If a path was given, use it. Otherwise use the current working directory. State the project being audited at the top of your report.

Detect the GitHub repo identity by running:
```sh
git -C <path> remote get-url origin
```
Parse `owner/repo` from the URL. If no remote exists, skip all GitHub settings checks and note it in the report.

### Step 2 — Check each area

#### README.md

- File exists
- Has project name and one-sentence description
- Lists prerequisites (runtime versions, required environment variables)
- Has a quickstart command (`just dev` or equivalent)
- Links to `docs/PURPOSE.md`
- States a license

#### docs/PURPOSE.md

- File exists
- Has a "problem being solved" section (1–3 paragraphs)
- Explicitly lists non-goals
- States the intended audience or users

#### .gitignore

- File exists
- Covers language/runtime artifacts relevant to this project's stack (build output, `__pycache__`, `node_modules`, `target/`, etc.) — check what languages the project uses (package.json, go.mod, Cargo.toml, etc.) and verify relevant entries are present
- Ignores `.env` and `.env.*` variants
- Ignores IDE directories (`.idea/`, `.vscode/`)
- Ignores OS files (`.DS_Store`, `Thumbs.db`)
- Ignores local-only config (e.g., `settings.local.json`)

#### Justfile

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

#### .github/workflows/ci.yml

- File exists (check for any `.github/workflows/*.yml` if the exact name differs)
- Triggers on `push` to `main` and all pull requests
- Has at least two jobs: lint (runs first) and test (runs after lint)
- All action versions are pinned to a specific tag (not `@latest`)
- `actions/checkout` is v6 or newer
- Has a multi-platform or multi-version test matrix where the runtime warrants it

#### GitHub repository settings

Fetch base settings:
```sh
gh api repos/{owner}/{repo}
```

Check:

| Field | Expected |
|-------|----------|
| `allow_merge_commit` | `false` |
| `allow_rebase_merge` | `false` |
| `squash_merge_commit_title` | `"PR_TITLE"` |
| `allow_update_branch` | `true` |
| `delete_branch_on_merge` | `true` |
| `social_preview_url` | non-null |

Fetch branch protection:
```sh
gh api repos/{owner}/{repo}/branches/main/protection 2>/dev/null || echo "NOT_PROTECTED"
```

Check:
- Required PR before merging (`required_pull_request_reviews` exists)
- Required status checks (`required_status_checks.contexts` non-empty)

Fetch webhooks:
```sh
gh api repos/{owner}/{repo}/hooks
```

Check:
- At least one webhook present (nazu reindexing hook). If the webhook URL is unknown, flag as UNKNOWN rather than FAIL.

Fetch labels:
```sh
gh api repos/{owner}/{repo}/labels --paginate
```

**Required labels:** `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `ci`, `build`, `style`, `revert`, `priority`, `nice to have`, `wontfix`

**Forbidden labels:** `good first issue`, `help wanted`

Check:
- All required labels present
- Neither forbidden label present

### Step 3 — Produce the report

Use this exact format:

```
## Project Standards Audit: <project-name>
Audited: <absolute path>

### README.md                    [PASS | FAIL | MISSING]
- OK   Has project name and description
- FAIL Missing prerequisites section
- OK   Quickstart command present (just dev)
- FAIL No link to docs/PURPOSE.md
- OK   License stated (MIT)

### docs/PURPOSE.md              [PASS | FAIL | MISSING]
...

### .gitignore                   [PASS | FAIL | MISSING]
...

### Justfile                     [PASS | FAIL | MISSING]
...

### CI workflow                  [PASS | FAIL | MISSING]
...

### GitHub settings              [PASS | FAIL | N/A]
- OK   No merge commits
- FAIL No rebase merging (currently enabled)
- OK   Commit message = PR title
- OK   Suggest branch updates
- FAIL Auto-delete head branches (disabled)
- FAIL Social preview image (not set)
- OK   Branch protection — PR required
- FAIL Branch protection — CI status checks required
- FAIL Nazu reindexing webhook (UNKNOWN)

### Labels                       [PASS | FAIL | N/A]
- FAIL Missing: perf, ci, style
- FAIL Forbidden present: good first issue
- OK   All other required labels present

---
Summary: X/7 areas passing
Critical gaps: <one-line list of the most important missing things, or "none">
```

Each item is `OK` or `FAIL`. Section header is `PASS` if all items OK, `FAIL` if any fail, `MISSING` if the file doesn't exist, `N/A` if no GitHub remote was detected.

### Step 4 — Offer to fix

After the report, ask: "Would you like me to fix any of these issues?"

If the user says yes (or gives a specific list), apply fixes:

**File-based gaps** — create missing files from scratch or edit existing ones to add missing content. If something requires human input (e.g., the actual purpose statement), scaffold a template with `<!-- TODO: fill in -->`.

**GitHub settings** — apply with a single PATCH:
```sh
gh api repos/{owner}/{repo} \
  --method PATCH \
  --field allow_merge_commit=false \
  --field allow_rebase_merge=false \
  --field squash_merge_commit_title=PR_TITLE \
  --field allow_update_branch=true \
  --field delete_branch_on_merge=true
```

**Labels** — create missing required labels:
```sh
gh label create "feat"        --repo {owner}/{repo} --color 0075ca --description "New feature (Conventional Commits: feat)"
gh label create "fix"         --repo {owner}/{repo} --color d73a4a --description "Bug fix (Conventional Commits: fix)"
gh label create "chore"       --repo {owner}/{repo} --color e4e669 --description "Chore (Conventional Commits: chore)"
gh label create "docs"        --repo {owner}/{repo} --color 0075ca --description "Documentation (Conventional Commits: docs)"
gh label create "refactor"    --repo {owner}/{repo} --color bfd4f2 --description "Code refactor (Conventional Commits: refactor)"
gh label create "test"        --repo {owner}/{repo} --color bfd4f2 --description "Tests (Conventional Commits: test)"
gh label create "perf"        --repo {owner}/{repo} --color bfd4f2 --description "Performance improvement (Conventional Commits: perf)"
gh label create "ci"          --repo {owner}/{repo} --color bfd4f2 --description "CI/CD (Conventional Commits: ci)"
gh label create "build"       --repo {owner}/{repo} --color bfd4f2 --description "Build system (Conventional Commits: build)"
gh label create "style"       --repo {owner}/{repo} --color bfd4f2 --description "Code style (Conventional Commits: style)"
gh label create "revert"      --repo {owner}/{repo} --color e4e669 --description "Revert (Conventional Commits: revert)"
gh label create "priority"    --repo {owner}/{repo} --color b60205 --description "High priority"
gh label create "nice to have" --repo {owner}/{repo} --color c5def5 --description "Low priority, would be nice"
gh label create "wontfix"     --repo {owner}/{repo} --color ffffff --description "Won't fix"
```

Delete forbidden labels:
```sh
gh api repos/{owner}/{repo}/labels/good%20first%20issue --method DELETE 2>/dev/null
gh api repos/{owner}/{repo}/labels/help%20wanted --method DELETE 2>/dev/null
```

**Manual only:**
- Social preview — must be uploaded via GitHub Settings → Social preview
- Nazu webhook — prompt user for the webhook URL, then create with `gh api repos/{owner}/{repo}/hooks --method POST`
- Branch protection — prompt user for required CI job names, then apply via `gh api repos/{owner}/{repo}/branches/main/protection --method PUT`

After fixing, re-audit only the changed areas and confirm they now pass.

## Judgment calls

- If a README has a prerequisites section but it's vague (e.g., "Node.js" with no version), mark it FAIL with a note.
- For .gitignore, look at what languages/tools the project actually uses and only flag entries relevant to the project.
- For CI: if the workflow file has a different name, still check it. If there are multiple workflow files, audit the most likely main CI gate.
- For Justfile app-type classification: look at whether the project has a start script, server code, or deployment config — if yes, treat it as an app.
- If a label already exists with the wrong color or description, mark it OK (name match is sufficient) — do not modify unless the user explicitly asks.
- If the `main` branch doesn't exist, try `master` for branch protection. If neither, skip that check.

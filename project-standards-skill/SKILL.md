---
name: project-standards
description: "Audit a project for compliance with project standards — documentation, .gitignore, Justfile, CI, and GitHub repository settings — and fix the gaps. Use this skill whenever the user asks to audit, check, or validate a project against standards — including phrases like 'does this project comply', 'check project standards', 'what's missing', 'run the audit', 'apply project standards', or '/project-standards'."
---

# Project Standards

Systematically check a project against all standards and produce a structured compliance report, then offer to fix the gaps.

Two areas are owned by sibling skills and this skill defers to them rather than restating their rules:

| Area | Owning skill | Read before auditing |
|------|--------------|----------------------|
| Documentation (`README.md`, `docs/PURPOSE.md`, `CONTEXT.md`, `CLAUDE.md`, `LICENSE`, `docs/` layout, monorepo package docs) | `/project-docs` | `~/.claude/skills/project-docs/SKILL.md` |
| `Justfile` (required recipes, naming, structure, monorepo modules) | `/justfile` | `~/.claude/skills/justfile/SKILL.md` |

If a rule here ever disagrees with the owning skill, the owning skill wins.

## Invocation

- `/project-standards` — audit the current working directory
- `/project-standards <path>` — audit the project at the given path

## Audit Process

### Step 1 — Resolve the target

If a path was given, use it. Otherwise use the current working directory. State the project being audited at the top of your report.

Detect the GitHub repo identity by running:
```sh
git -C <path> remote get-url origin
```
Parse `owner/repo` from the URL. If no remote exists, skip all GitHub settings checks and note it in the report.

### Step 2 — Check each area

#### Documentation

Read the project-docs skill, then run its audit process against this project. That skill decides whether the repo is a single project or a monorepo and which documents are required where.

Carry its findings into this report as three sections:

- **README.md** — the root README checks
- **docs/PURPOSE.md** — the purpose doc checks
- **Other docs** — `CONTEXT.md`, `CLAUDE.md`, `LICENSE`, optional-doc triggers, "never" violations, and (monorepo) one line per package README

#### .gitignore

- File exists
- Covers language/runtime artifacts relevant to this project's stack (build output, `__pycache__`, `node_modules`, `target/`, etc.) — check what languages the project uses (package.json, go.mod, Cargo.toml, etc.) and verify relevant entries are present
- Ignores `.env` and `.env.*` variants
- Ignores IDE directories (`.idea/`, `.vscode/`)
- Ignores OS files (`.DS_Store`, `Thumbs.db`)
- Ignores local-only config (e.g., `settings.local.json`)

#### Justfile

Read the Justfile skill, then run its audit process against this project's Justfile (root Justfile plus per-package modules in a monorepo). Each `MISSING`, `RENAME`, or structural finding from that audit becomes a `FAIL` line here; `OK` lines carry over as `OK`. Do not apply the Justfile skill's fixes during the audit — fixes happen in Step 4.

#### .github/workflows/ci.yml

- File exists (check for any `.github/workflows/*.yml` if the exact name differs)
- Triggers on `pull_request` events (PR open and update) — this is the critical gate
- Also triggers on `push` to `main`
- Has at least two jobs covering lint/typecheck and tests
- All action versions are pinned to a specific tag (not `@latest`)
- `actions/checkout` is v6 or newer
- Has a multi-platform or multi-version test matrix where the runtime warrants it

#### GitHub repository settings

Fetch base settings and social preview in one batch:
```sh
gh api repos/{owner}/{repo}
gh api graphql -f query='{ repository(owner: "{owner}", name: "{repo}") { usesCustomOpenGraphImage } }'
```

Check:

| Source | Field | Expected |
|--------|-------|----------|
| REST | `allow_merge_commit` | `false` |
| REST | `allow_rebase_merge` | `false` |
| REST | `squash_merge_commit_title` | `"PR_TITLE"` |
| REST | `allow_update_branch` | `true` |
| REST | `delete_branch_on_merge` | `true` |
| GraphQL | `usesCustomOpenGraphImage` | `true` |

#### Branch protection

Resolve the default branch from the `default_branch` field of the `gh api repos/{owner}/{repo}` response already fetched above, then:

```sh
gh api repos/{owner}/{repo}/branches/{default_branch}/protection
```

A `404 Not Found` means the default branch is unprotected — mark all three checks FAIL.

Check (names are machine-friendly identifiers; report them verbatim):

| Check | Field | Expected |
|-------|-------|----------|
| `branch-protection-enabled` | endpoint returns `200` | Protection exists on the default branch |
| `require-pr-approval` | `required_pull_request_reviews.required_approving_review_count` | `>= 1` |
| `require-ci-checks` | `required_status_checks.checks[].context` | Includes the CI **lint** and **test** job names |

For `require-ci-checks`: compare the required contexts against the job names in the project's CI workflow (see the CI workflow area). A job satisfies lint or test if it performs that role even when named differently (e.g., `lint-and-typecheck` covers lint); if no required status check maps to each of lint and test, mark FAIL. If the API returns only the legacy `required_status_checks.contexts` array, check that instead.

Fetch labels:
```sh
gh api repos/{owner}/{repo}/labels --paginate
```

**Required labels:** `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `ci`, `build`, `style`, `revert`, `priority`, `nice to have`, `wontfix`, `question`, `invalid`, `XS`, `S`, `M`, `L`, `XL`

**Effort labels (t-shirt sizes):**

| Label | Meaning |
|-------|---------|
| `XS` | Minor update with no code impact (e.g., docs typo, comment fix) |
| `S`  | Small, localized change to a single file or function |
| `M`  | Moderate change spanning a few files within one area |
| `L`  | Large change across multiple areas or subsystems |
| `XL` | Project-wide impact (e.g., tooling change, switch to monorepo, major refactor) |

**Forbidden labels:** `good first issue`, `help wanted`

**Legacy labels to rename** (count as present if found, but flag for rename in fix mode):

| Existing name | Rename to |
|--------------|-----------|
| `feature` | `feat` |
| `bug` | `fix` |
| `documentation` | `docs` |

Check:
- All required labels present (legacy names count as satisfying the requirement but are flagged for rename)
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

### Other docs                   [PASS | FAIL | MISSING]
- OK   CONTEXT.md present with open-questions section
- FAIL CLAUDE.md contains project narrative (belongs in CONTEXT.md)
- OK   LICENSE present
- FAIL apps/web/README.md missing        (monorepo only)

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

### Branch protection            [PASS | FAIL | N/A]
- OK   branch-protection-enabled
- FAIL require-pr-approval (required approvals: 0)
- OK   require-ci-checks (lint, test)

### Labels                       [PASS | FAIL | N/A]
- FAIL Missing: perf, ci, style
- FAIL Forbidden present: good first issue
- OK   All other required labels present

---
Summary: X/9 areas passing
Critical gaps: <one-line list of the most important missing things, or "none">
```

Each item is `OK` or `FAIL`. Section header is `PASS` if all items OK, `FAIL` if any fail, `MISSING` if the file doesn't exist, `N/A` if no GitHub remote was detected.

### Step 4 — Offer to fix

After the report, ask: "Would you like me to fix any of these issues?"

If the user says yes (or gives a specific list), apply fixes:

**Documentation gaps** — apply the project-docs skill's fix step (its templates, its `<!-- TODO: fill in -->` convention).

**Justfile gaps** — apply the Justfile skill's fix step.

**Other file-based gaps** (`.gitignore`, CI workflow) — create missing files from scratch or edit existing ones to add missing content.

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

**Branch protection** — apply with a single PUT, substituting the actual lint and test job names from the project's CI workflow:
```sh
gh api repos/{owner}/{repo}/branches/{default_branch}/protection \
  --method PUT \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      { "context": "lint" },
      { "context": "test" }
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1
  },
  "restrictions": null
}
EOF
```

**Labels** — rename legacy labels first, then create any still missing:
```sh
# Rename legacy labels (preserves existing issues/PRs tagged with them)
gh api repos/{owner}/{repo}/labels/feature       --method PATCH --field name=feat          --field description="New feature (Conventional Commits: feat)" 2>/dev/null
gh api repos/{owner}/{repo}/labels/bug           --method PATCH --field name=fix           --field description="Bug fix (Conventional Commits: fix)" 2>/dev/null
gh api repos/{owner}/{repo}/labels/documentation --method PATCH --field name=docs          --field description="Documentation (Conventional Commits: docs)" 2>/dev/null

# Create missing required labels
gh label create "feat"         --repo {owner}/{repo} --color 0075ca --description "New feature (Conventional Commits: feat)"         --force
gh label create "fix"          --repo {owner}/{repo} --color d73a4a --description "Bug fix (Conventional Commits: fix)"               --force
gh label create "chore"        --repo {owner}/{repo} --color e4e669 --description "Chore (Conventional Commits: chore)"               --force
gh label create "docs"         --repo {owner}/{repo} --color 0075ca --description "Documentation (Conventional Commits: docs)"        --force
gh label create "refactor"     --repo {owner}/{repo} --color bfd4f2 --description "Code refactor (Conventional Commits: refactor)"    --force
gh label create "test"         --repo {owner}/{repo} --color bfd4f2 --description "Tests (Conventional Commits: test)"                --force
gh label create "perf"         --repo {owner}/{repo} --color bfd4f2 --description "Performance improvement (Conventional Commits: perf)" --force
gh label create "ci"           --repo {owner}/{repo} --color bfd4f2 --description "CI/CD (Conventional Commits: ci)"                  --force
gh label create "build"        --repo {owner}/{repo} --color bfd4f2 --description "Build system (Conventional Commits: build)"        --force
gh label create "style"        --repo {owner}/{repo} --color bfd4f2 --description "Code style (Conventional Commits: style)"          --force
gh label create "revert"       --repo {owner}/{repo} --color e4e669 --description "Revert (Conventional Commits: revert)"             --force
gh label create "priority"     --repo {owner}/{repo} --color b60205 --description "High priority"                                     --force
gh label create "nice to have" --repo {owner}/{repo} --color c5def5 --description "Low priority, would be nice"                      --force
gh label create "wontfix"      --repo {owner}/{repo} --color ffffff --description "Won't fix"                                         --force
gh label create "question"     --repo {owner}/{repo} --color d876e3 --description "Further information requested"                     --force
gh label create "invalid"      --repo {owner}/{repo} --color e4e669 --description "This doesn't seem right"                          --force

# Effort (t-shirt size) labels
gh label create "XS"           --repo {owner}/{repo} --color c2e0c6 --description "Effort: minor update with no code impact (e.g., docs)" --force
gh label create "S"            --repo {owner}/{repo} --color a2eeef --description "Effort: small, localized change"                       --force
gh label create "M"            --repo {owner}/{repo} --color fbca04 --description "Effort: moderate change across a few files"           --force
gh label create "L"            --repo {owner}/{repo} --color d93f0b --description "Effort: large change across multiple areas"           --force
gh label create "XL"           --repo {owner}/{repo} --color b60205 --description "Effort: project-wide impact (e.g., tooling, monorepo)" --force
```

Delete forbidden labels:
```sh
gh api repos/{owner}/{repo}/labels/good%20first%20issue --method DELETE 2>/dev/null
gh api repos/{owner}/{repo}/labels/help%20wanted --method DELETE 2>/dev/null
```

**Manual only:**
- Social preview — must be uploaded via GitHub Settings → Social preview

After fixing, re-audit only the changed areas and confirm they now pass.

## Judgment calls

- If a README has a prerequisites section but it's vague (e.g., "Node.js" with no version), mark it FAIL with a note.
- For .gitignore, look at what languages/tools the project actually uses and only flag entries relevant to the project.
- For CI: if the workflow file has a different name, still check it. If there are multiple workflow files, audit the most likely main CI gate.
- App-vs-library classification (used by both sibling skills): look at whether the project has a start script, server code, or deployment config — if yes, treat it as an app.
- If a label already exists with the wrong color or description, mark it OK (name match is sufficient) — do not modify unless the user explicitly asks.

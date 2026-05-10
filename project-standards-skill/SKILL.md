---
name: project-standards
description: "Audit ALL GitHub repos against the full project standards — file content AND repository settings. Use this skill when the user asks to audit all projects, check standards across repos, run a multi-repo compliance check, or apply fixes across repositories. Trigger on phrases like 'audit all projects', 'check all repos', 'project standards across all repos', '/project-standards', or 'iterate over all projects'."
---

# Project Standards — Multi-Repo Audit

Iterate over every GitHub repository and produce a compliance report covering both file-based standards and GitHub repository settings. Optionally apply fixes.

## Invocation

- `/project-standards` — audit all repos, report only
- `/project-standards --fix` — audit all repos, then apply fixes where possible

## Standards reference

File-based standards live in `docs/project-standards.md` (in THIS skills repo). Read it at the start of each run so the check is always current.

---

## Step 1 — Discover repos

```sh
gh repo list --limit 100 --json name,nameWithOwner,url,isPrivate,isArchived
```

Skip archived repos. List them at the top of the report as skipped. Proceed with all others.

---

## Step 2 — Per-repo checks

Run both categories for each repo. Use `gh api` for all GitHub settings — never clone repos.

### Category A — GitHub repository settings

Fetch base settings:
```sh
gh api repos/{nameWithOwner}
```

Check these fields:

| Field | Expected value | Label |
|-------|---------------|-------|
| `allow_merge_commit` | `false` | No merge commits |
| `allow_rebase_merge` | `false` | No rebase merging |
| `squash_merge_commit_title` | `"PR_TITLE"` | Commit message = PR title |
| `allow_update_branch` | `true` | Suggest branch updates |
| `delete_branch_on_merge` | `true` | Auto-delete head branches |
| `social_preview_url` | non-null | Social preview image set |

Fetch branch protection for `main`:
```sh
gh api repos/{nameWithOwner}/branches/main/protection 2>/dev/null || echo "NOT_PROTECTED"
```

Check:
- Required PR before merging (`required_pull_request_reviews` exists)
- Required status checks (`required_status_checks.contexts` non-empty)

If the response is `NOT_PROTECTED`, both checks fail.

Fetch webhooks:
```sh
gh api repos/{nameWithOwner}/hooks
```

Check:
- At least one webhook configured (presence of the nazu reindexing hook). If the webhook URL is unknown, flag as UNKNOWN rather than FAIL and prompt the user to supply it at fix time.

Fetch labels:
```sh
gh api repos/{nameWithOwner}/labels --paginate
```

**Required labels** (Conventional Commits + triage):
`feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `ci`, `build`, `style`, `revert`, `priority`, `nice to have`, `wontfix`

**Labels that must NOT exist:**
`good first issue`, `help wanted`

Check:
- All required labels present
- Neither forbidden label present

### Category B — File-based standards

Read each file via the GitHub API (no clone needed):
```sh
gh api repos/{nameWithOwner}/contents/{path} --jq '.content' | base64 -d
```

Apply exactly the same checks as the single-repo `/audit` skill:

**README.md** — exists, project name + description, prerequisites, quickstart command, link to `docs/PURPOSE.md`, license stated

**docs/PURPOSE.md** — exists, problem statement (1–3 paragraphs), non-goals section, intended audience

**.gitignore** — exists, covers language artifacts for the project's actual stack, ignores `.env`/`.env.*`, IDE dirs (`.idea/`, `.vscode/`), OS files (`.DS_Store`, `Thumbs.db`), local config (`settings.local.json`)

**Justfile** — exists, header comment, `default` recipe first using `@just --list`, all required recipes present (`install`, `check`, `lint`, `fix`, `typecheck`, `test`, `clean`, `fresh`), app-type recipes where applicable (`run`, `dev`), naming rules followed, recipe comment structure correct

**.github/workflows/ci.yml** — exists (check any `.github/workflows/*.yml` if exact name differs), triggers on `push` to `main` and pull requests, lint and test jobs present, all action versions pinned, `actions/checkout` at v6+

---

## Step 3 — Report

Produce a structured report. Use this exact format:

```
## Project Standards Audit — All Repos
Run: <date>   Repos checked: <N>   Skipped (archived): <list or "none">

────────────────────────────────────────────────
### <owner>/<repo>                    [PASS | FAIL]
────────────────────────────────────────────────

**Settings**                          [PASS | FAIL]
- OK   No merge commits
- FAIL No rebase merging (allow_rebase_merge: true)
- OK   Commit message = PR title
- OK   Suggest branch updates
- FAIL Auto-delete head branches (disabled)
- FAIL Social preview image (not set)
- FAIL Branch protection — PR required (not protected)
- FAIL Branch protection — CI status checks required (not protected)
- FAIL Nazu reindexing webhook (UNKNOWN — supply URL to fix)

**Labels**                            [PASS | FAIL]
- OK   feat, fix, chore, docs, refactor, test, perf, ci, build, style, revert, priority, nice to have, wontfix
- FAIL Missing: perf, ci, style
- FAIL Forbidden present: good first issue, help wanted

**README.md**                         [PASS | FAIL | MISSING]
- OK   Project name and description
- FAIL Missing prerequisites section
...

**docs/PURPOSE.md**                   [PASS | FAIL | MISSING]
...

**.gitignore**                        [PASS | FAIL | MISSING]
...

**Justfile**                          [PASS | FAIL | MISSING]
...

**CI workflow**                       [PASS | FAIL | MISSING]
...

────────────────────────────────────────────────
### <owner>/<repo2>                   [PASS | FAIL]
...

---
## Summary
Repos fully compliant: X / N
Top gaps across all repos:
- <most common failing check>
- <second most common>
- ...
```

Each item is `OK` (compliant) or `FAIL` (violation or missing). A section is `PASS` if all items OK, `FAIL` if any fail, `MISSING` if the file doesn't exist.

---

## Step 4 — Fix mode

If `--fix` was passed OR the user approves fixes after seeing the report, apply them in this order:

### Fixes that can be applied automatically

**GitHub settings** — apply with a single PATCH per repo:
```sh
gh api repos/{nameWithOwner} \
  --method PATCH \
  --field allow_merge_commit=false \
  --field allow_rebase_merge=false \
  --field squash_merge_commit_title=PR_TITLE \
  --field allow_update_branch=true \
  --field delete_branch_on_merge=true
```

**Labels** — create missing required labels:
```sh
gh label create "feat" --repo {nameWithOwner} --color 0075ca --description "New feature (Conventional Commits: feat)"
gh label create "fix" --repo {nameWithOwner} --color d73a4a --description "Bug fix (Conventional Commits: fix)"
gh label create "chore" --repo {nameWithOwner} --color e4e669 --description "Chore (Conventional Commits: chore)"
gh label create "docs" --repo {nameWithOwner} --color 0075ca --description "Documentation (Conventional Commits: docs)"
gh label create "refactor" --repo {nameWithOwner} --color bfd4f2 --description "Code refactor (Conventional Commits: refactor)"
gh label create "test" --repo {nameWithOwner} --color bfd4f2 --description "Tests (Conventional Commits: test)"
gh label create "perf" --repo {nameWithOwner} --color bfd4f2 --description "Performance improvement (Conventional Commits: perf)"
gh label create "ci" --repo {nameWithOwner} --color bfd4f2 --description "CI/CD (Conventional Commits: ci)"
gh label create "build" --repo {nameWithOwner} --color bfd4f2 --description "Build system (Conventional Commits: build)"
gh label create "style" --repo {nameWithOwner} --color bfd4f2 --description "Code style (Conventional Commits: style)"
gh label create "revert" --repo {nameWithOwner} --color e4e669 --description "Revert (Conventional Commits: revert)"
gh label create "priority" --repo {nameWithOwner} --color b60205 --description "High priority"
gh label create "nice to have" --repo {nameWithOwner} --color c5def5 --description "Low priority, would be nice"
gh label create "wontfix" --repo {nameWithOwner} --color ffffff --description "Won't fix"
```

Delete forbidden labels:
```sh
gh api repos/{nameWithOwner}/labels/good%20first%20issue --method DELETE 2>/dev/null
gh api repos/{nameWithOwner}/labels/help%20wanted --method DELETE 2>/dev/null
```

### Fixes that require manual action

- **Social preview image** — must be uploaded via GitHub web UI (Settings → Social preview). Flag each affected repo with its URL.
- **Nazu webhook** — prompt the user for the webhook URL and payload URL before creating. Once supplied, create with `gh api repos/{nameWithOwner}/hooks --method POST`.
- **Branch protection** — requires knowing the required CI job names. Prompt the user, then apply via `gh api repos/{nameWithOwner}/branches/main/protection --method PUT`.
- **File-based gaps** (README, PURPOSE, .gitignore, Justfile, CI) — offer to create a PR in the target repo. Use `gh pr create` after committing the fix on a branch in that repo.

### After fixes

Re-run only the categories that were fixed and confirm they now pass. Do not re-run unchanged sections.

---

## Judgment calls

- If a repo has no `main` branch, try `master`. If neither exists, skip branch protection check and note it.
- For .gitignore language coverage: inspect the repo's primary language from `gh api repos/{nameWithOwner} --jq '.language'` and check for that language's artifacts.
- GitHub API rate limit is 5,000 req/hr for authenticated requests. At ~10 API calls per repo, this supports ~500 repos per run. For large org accounts, warn if repo count exceeds 100.
- If a label already exists but has the wrong color or description, report it as OK (name match is sufficient) — do not modify existing labels unless the user explicitly asks.

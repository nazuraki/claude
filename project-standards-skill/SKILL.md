---
name: project-standards
description: "Audit a project for compliance with project standards — documentation, .gitignore, Justfile, CI, and GitHub repository settings — and fix the gaps. Use this skill whenever the user asks to audit, check, or validate a project against standards — including phrases like 'does this project comply', 'check project standards', 'what's missing', 'run the audit', 'apply project standards', or '/project-standards'."
---

# Project Standards

Systematically check a project against all standards and produce a structured compliance report, then offer to fix the gaps.

Two areas are owned by sibling skills and this skill defers to them rather than restating their rules:

| Area | Owning skill | Read before auditing |
|------|--------------|----------------------|
| Documentation (`README.md`, `docs/PURPOSE.md`, `CONTEXT.md`, `CLAUDE.md`, `LICENSE`, `docs/` detail directories and summary docs, monorepo package docs) | `/project-docs` | `~/.claude/skills/project-docs/SKILL.md` |
| `Justfile` (required recipes, naming, structure, monorepo modules) | `/justfile` | `~/.claude/skills/justfile/SKILL.md` |

If a rule here ever disagrees with the owning skill, the owning skill wins.

Two companion files sit beside this skill: [workflows.md](workflows.md) holds the workflow templates the CI area checks against, and [fixes.md](fixes.md) holds the commands Step 4 runs. Read each when you reach the step that needs it.

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
- **Other docs** — `CONTEXT.md`, `CLAUDE.md`, `LICENSE`, detail directories (`docs/requirements/`, `features/`, `use-cases/`, `research/`, `decisions/`, `design/`, `runbooks/`) and their summary docs, optional-doc triggers, "never" violations, and (monorepo) one line per package README

#### .gitignore

- File exists
- Covers language/runtime artifacts relevant to this project's stack (build output, `__pycache__`, `node_modules`, `target/`, etc.) — check what languages the project uses (package.json, go.mod, Cargo.toml, etc.) and verify relevant entries are present
- Ignores `.env` and `.env.*` variants
- Ignores IDE directories (`.idea/`, `.vscode/`)
- Ignores OS files (`.DS_Store`, `Thumbs.db`)
- Ignores Claude Code local state with exactly these three entries. Ignoring `.claude/` as a whole is a FAIL: it hides committed skills, agents, and shared settings.
  ```
  .claude/settings.local.json
  .claude/launch.json
  .claude/scheduled_tasks.lock
  ```

#### Justfile

Read the Justfile skill, then run its audit process against this project's Justfile (root Justfile plus per-package modules in a monorepo). Each `MISSING`, `RENAME`, or structural finding from that audit becomes a `FAIL` line here; `OK` lines carry over as `OK`. Do not apply the Justfile skill's fixes during the audit — fixes happen in Step 4.

#### CI workflows

The main gate is `.github/workflows/ci.yml`:

- File exists (check for any `.github/workflows/*.yml` if the exact name differs)
- Triggers on `pull_request` events (PR open and update) — this is the critical gate
- Also triggers on `push` to `main`
- `concurrency` group `${{ github.workflow }}-${{ github.ref }}` with `cancel-in-progress: true`
- Top-level `permissions: contents: read`
- Jobs are named `lint` and `test`. `lint` runs `just lint` then `just typecheck`; `test` runs `just test`, each after `extractions/setup-just`. CI never re-implements what the Justfile defines, so job names map 1:1 onto required status checks
- A `docker` job running `just docker-build` when the repo has a Dockerfile
- Dependencies install from the lockfile (`pnpm install --frozen-lockfile`, `npm ci`, `cargo build --locked`)
- Node version comes from `node-version-file: .nvmrc` (the file is committed), never an inline `node-version`
- All action versions are pinned to a major tag or SHA, never `@latest` or `@main`
- `actions/checkout` is v6 or newer
- Matrix jobs are named after what varies, in terms a developer recognizes: the package in a monorepo (`test (core)`, `test (bot)`), the platform for a desktop app (`build (macos)`). Never a bare runtime version: `test (22)` says nothing. A Node-version matrix is only for a published library that supports more than one major, and then the name carries both: `test (core, node 22)`
- In a monorepo the matrix job is `test-package` and a gate job `test` depends on it, so the ruleset requires `test` and never has to list packages (see the monorepo variant in workflows.md)

Secondary workflows are specified in [workflows.md](workflows.md). Check each one whose trigger applies:

| Workflow | Required when | Check |
|----------|---------------|-------|
| `publish.yml` | Repo has a Dockerfile and deploys as a container | Exists under that name; runs on `push` to `main` and `v*` tags; pushes to GHCR with `latest`, `sha-*`, and semver tags; `permissions: packages: write`; concurrency per ref |
| `pages.yml` | GitHub Pages is enabled (`gh api repos/{owner}/{repo}/pages` returns `200`) | Exists under that name; `build_type` is `workflow`; deploys with `actions/deploy-pages` from the `github-pages` environment; repo `homepage` is the Pages URL |
| `pr-guidelines.yml` | Every repo | Exists under that name; triggers on `pull_request` types `opened, edited, synchronize, reopened`; job `pr-title` runs `amannn/action-semantic-pull-request` with the Conventional Commits types; `pr-title` is a required status check (squash titles come from PR titles, so this is what keeps `main` history conventional) |
| `release.yml` | The project publishes versioned releases | Matches the release shape for its kind: library, desktop app, or service (services need no `release.yml`; `publish.yml` is their release pipeline) |

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
| REST | `squash_merge_commit_message` | `"BLANK"` |
| REST | `allow_update_branch` | `true` |
| REST | `delete_branch_on_merge` | `true` |
| REST | `allow_auto_merge` | `false` |
| REST | `description` | Non-empty |
| REST | `homepage` | The Pages URL when Pages is enabled; otherwise anything |
| REST | `has_wiki` | `false` — docs live in the repo |
| REST | `has_discussions` | `false` unless the repo actually uses discussions |
| GraphQL | `usesCustomOpenGraphImage` | `true` (public repos; `N/A` on private) |

#### Security

Dependabot state needs two more calls; secret scanning is in the `security_and_analysis` field of the base settings already fetched.

```sh
gh api repos/{owner}/{repo}/vulnerability-alerts -i      # 204 = enabled, 404 = disabled
gh api repos/{owner}/{repo}/automated-security-fixes      # {"enabled": true|false}
```

| Check | Where | Expected |
|-------|-------|----------|
| `dependabot-alerts` | `vulnerability-alerts` returns `204` | Enabled on every repo (free on private) |
| `dependabot-security-updates` | `automated-security-fixes.enabled` | `true` |
| `secret-scanning` | `security_and_analysis.secret_scanning.status` | `enabled` on public repos; `N/A` on private (needs Advanced Security) |
| `secret-scanning-push-protection` | `security_and_analysis.secret_scanning_push_protection.status` | `enabled` on public repos; `N/A` on private |

#### Branch rules

Branch protection is expressed as a **repository ruleset** targeting the default branch, not classic branch protection. Resolve the default branch from the `default_branch` field of the `gh api repos/{owner}/{repo}` response already fetched above, then fetch the rules in effect on it (this merges repository and organization rulesets) and, separately, check that no classic protection remains:

```sh
gh api repos/{owner}/{repo}/rules/branches/{default_branch}
gh api repos/{owner}/{repo}/branches/{default_branch}/protection
```

An empty array from the first call means no ruleset governs the default branch — mark every rule check FAIL (`codeowners-file` and `no-classic-protection` are checked on their own).

A `403` whose message says to upgrade the plan means the repo is private and its owner is on the Free plan, where rulesets and branch protection are unavailable. Report the whole area as `N/A (private repo, Free plan)`. A private repo that accepts contributors must live in a Team-plan org: Write access is the only way to push branches without forking, and only branch rules keep Write from merging. Flag the move under Critical gaps.

Check (names are machine-friendly identifiers; report them verbatim):

| Check | Where | Expected |
|-------|-------|----------|
| `ruleset-active` | first call returns a non-empty array | An active ruleset targets the default branch |
| `no-deletion` | a rule of type `deletion` | Present |
| `no-force-push` | a rule of type `non_fast_forward` | Present |
| `require-pr-approval` | `pull_request` rule, `parameters.required_approving_review_count` | `>= 1` |
| `require-codeowner-review` | `pull_request` rule, `parameters.require_code_owner_review` | `true` |
| `dismiss-stale-reviews` | `pull_request` rule, `parameters.dismiss_stale_reviews_on_push` | `true` |
| `require-conversation-resolution` | `pull_request` rule, `parameters.required_review_thread_resolution` | `true` |
| `codeowners-file` | `.github/CODEOWNERS` in the repo | Exists, with a catch-all `*` rule naming the person who approves merges |
| `require-ci-checks` | `required_status_checks` rule, `parameters.required_status_checks[].context` | Includes the CI **lint** and **test** job names and **pr-title**, and `strict_required_status_checks_policy` is `true` |
| `no-classic-protection` | second call returns `404` | No classic protection rule on the default branch |

`no-deletion` and `no-force-push` exist because a ruleset permits both unless a rule forbids them, where classic protection forbade them by default. An approval count alone lets two collaborators with Write approve each other's PRs. Code-owner review makes the owner's approval mandatory, and dismissing stale reviews stops a later push from riding an earlier approval. `codeowners-file` is a file check, but it lives here because the rule enforces nothing without it. The catch-all rule names a user or team (`*  @login`), never the org. When auditing by remote, read it with `gh api repos/{owner}/{repo}/contents/.github/CODEOWNERS`. `no-classic-protection` catches repos that predate rulesets: classic and ruleset protection can coexist, and two sources of truth is the failure mode.

For `require-ci-checks`: compare the required contexts against the job names in the project's CI workflow (see the CI workflow area). A job satisfies lint or test if it performs that role even when named differently (e.g., `lint-and-typecheck` covers lint); if no required status check maps to each of lint, test, and pr-title, mark FAIL.

Fetch labels:
```sh
gh api repos/{owner}/{repo}/labels --paginate
```

**Required labels:** `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `ci`, `build`, `style`, `revert`, `priority`, `nice to have`, `wontfix`, `question`, `invalid`, `accessibility`, `security`, `XS`, `S`, `M`, `L`, `XL`

**Optional labels** (allowed, never required): `blocked` for work waiting on an external dependency or decision, and area labels in the form `area:<kebab-name>` (e.g. `area:ingest`) for repos large enough to route issues by subsystem. Labels outside this list are not findings, so Dependabot's `dependencies` and language labels pass silently.

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
- FAIL No status badge under the H1
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
- FAIL docs/decisions.md missing entry for 0003-adopt-pnpm.md
- FAIL apps/web/README.md missing        (monorepo only)

### .gitignore                   [PASS | FAIL | MISSING]
...

### Justfile                     [PASS | FAIL | MISSING]
...

### CI workflows                 [PASS | FAIL | MISSING]
- OK   ci.yml triggers on pull_request and push to main
- FAIL ci.yml has no concurrency group
- FAIL lint job re-implements biome instead of running just lint
- OK   pr-guidelines.yml (pr-title required)
- OK   publish.yml (Dockerfile present)
- OK   pages.yml not required (Pages off)

### GitHub settings              [PASS | FAIL | N/A]
- OK   No merge commits
- FAIL No rebase merging (currently enabled)
- OK   Commit message = PR title
- OK   Squash commit message blank
- OK   Suggest branch updates
- FAIL Auto-delete head branches (disabled)
- FAIL Auto-merge (enabled)
- OK   Description set
- FAIL Homepage (Pages enabled, homepage unset)
- FAIL Wiki (enabled)
- OK   Discussions off
- FAIL Social preview image (not set)

### Security                     [PASS | FAIL | N/A]
- OK   dependabot-alerts
- FAIL dependabot-security-updates (disabled)
- OK   secret-scanning
- OK   secret-scanning-push-protection

### Branch rules                 [PASS | FAIL | N/A]
- OK   ruleset-active (main)
- OK   no-deletion
- OK   no-force-push
- FAIL require-pr-approval (required approvals: 0)
- OK   require-codeowner-review
- FAIL dismiss-stale-reviews (disabled)
- OK   require-conversation-resolution
- OK   codeowners-file (* @login)
- OK   require-ci-checks (lint, test, pr-title)
- FAIL no-classic-protection (classic rule still on main)

### Labels                       [PASS | FAIL | N/A]
- FAIL Missing: perf, ci, style
- FAIL Forbidden present: good first issue
- OK   All other required labels present

---
Summary: X/10 areas passing
Critical gaps: <one-line list of the most important missing things, or "none">
```

Each item is `OK` or `FAIL`. Section header is `PASS` if all items OK, `FAIL` if any fail, `MISSING` if the file doesn't exist, `N/A` if no GitHub remote was detected, or, for Branch rules only, the repo is private on a Free plan.

### Step 4 — Offer to fix

After the report, ask: "Would you like me to fix any of these issues?"

If the user says yes (or gives a specific list), apply fixes using [fixes.md](fixes.md) beside this skill: documentation and Justfile gaps go through the sibling skills' fix steps; `.gitignore` and workflow gaps are file edits (workflows start from [workflows.md](workflows.md)); GitHub settings, security, CODEOWNERS, branch rules, and labels each have their commands there. Label renames and deletions rewrite every issue carrying the label, so confirm those individually before running them. The social preview image is manual.

After fixing, re-audit only the changed areas and confirm they now pass.

## Judgment calls

- If a README has a prerequisites section but it's vague (e.g., "Node.js" with no version), mark it FAIL with a note.
- For .gitignore, look at what languages/tools the project actually uses and only flag entries relevant to the project.
- For CI: if the workflow file has a different name, still check it. If there are multiple workflow files, audit the most likely main CI gate.
- App-vs-library classification (used by both sibling skills): look at whether the project has a start script, server code, or deployment config — if yes, treat it as an app.
- If a label already exists with the wrong color or description, mark it OK (name match is sufficient) — do not modify unless the user explicitly asks.
- Secret scanning and the social preview are `N/A` on private repos, not FAIL. Dependabot is never `N/A`.
- `has_discussions`: if the repo has discussions with real content, mark OK and note it rather than proposing to switch them off.
- A `403` on the rules endpoints is a plan limit, not a missing setting. Do not fall back to classic protection; report `N/A` and, if the repo takes contributors, the Team-org move.

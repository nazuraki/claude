---
name: work-on
description: "Full issue workflow: verify clean main, pull, read issue, branch, plan (with tests), iterate on plan until approved, implement, validate (lint/typecheck/test), open PR. Usage: /work-on <issue-number>"
---

# Work On Issue

End-to-end workflow for picking up a GitHub issue, implementing it, and opening a PR.

## Invocation

```
/work-on <issue-number>
```

Abort with a clear message if no issue number is provided.

## Step 1 — Verify clean main

Run:
```sh
git branch --show-current
```

If the current branch is not `main`, stop and tell the user:
> You're on branch `<branch>`. Switch to `main` before starting a new issue.

Do not proceed.

Run:
```sh
git status --short
```

If there are any uncommitted changes or untracked files, stop and tell the user what's dirty. Do not proceed.

## Step 2 — Update main

```sh
git pull --ff-only
```

If this fails (diverged or no remote), report it and stop. Do not force-pull or reset.

## Step 3 — Read the issue

```sh
gh issue view <issue-number> --json number,title,body,labels,assignees,milestone,url
```

Display a compact summary:
- Issue number and title
- URL
- Labels and milestone (if any)
- Body (full text)

If the issue doesn't exist or `gh` errors, report and stop.

## Step 4 — Create branch

Derive a slug from the issue title: lowercase, words joined by hyphens, max 40 chars, no special characters. Format:

```
<issue-number>-<slug>
```

Examples: `142-add-user-avatar`, `88-fix-login-redirect-loop`

Run:
```sh
git checkout -b <branch-name>
```

Confirm the branch name to the user.

## Step 5 — Implementation plan

Analyze the issue and the relevant codebase to produce an implementation plan. The plan must:

- Break the work into numbered, concrete steps
- Call out which files will be created or modified
- Include a testing strategy — enumerate every behaviour that should be verified, then classify each as **automated** (will be covered by a new or updated test) or **manual** (genuinely cannot be automated). Default to automated; manual is only valid for things like visual rendering, hardware interaction, or third-party integration with no test double available
- Flag any ambiguities or assumptions that need user confirmation
- Note any risks or non-obvious side effects

Present the plan clearly. Do not start implementing.

## Step 6 — Plan approval loop

Ask the user: **"Does this plan look good, or do you have changes?"**

Loop:
- If the user requests changes, revise the plan and re-present it
- If the user approves (e.g. "yes", "looks good", "go ahead"), proceed to Step 7
- If the user says to abort, check out `main` and delete the branch

Do not begin implementation until explicitly approved.

## Step 7 — Implement

Carry out the approved plan step by step. Follow the implementation order in the plan. Write the automated tests identified in the plan alongside the code they cover — do not leave tests until the end. After all steps are complete, verify the implementation matches the plan.

Commit logically cohesive chunks as you go rather than one giant commit at the end. Each commit message must follow Conventional Commits (`<type>(<scope>): <description>`).

## Step 8 — Validate loop

Detect the project's check command in order of preference:
1. `just check` (if a Justfile exists with a `check` recipe)
2. `npm run check` / `pnpm run check` (if `package.json` has a `check` script)
3. Run lint, typecheck, and test commands individually if no unified check exists

Run the check command. If it fails:
- Read the output
- Fix the issues
- Re-run
- Repeat until the check passes with no errors

Do not open a PR until all checks pass.

## Step 9 — Open PR

```sh
gh pr create \
  --title "<issue-title>" \
  --body "$(cat <<'EOF'
Closes #<issue-number>

## Summary
<3-5 bullet points describing what changed and why>

## Test plan

**Automated** (covered by tests added in this PR — verified by CI):
<bulleted list of behaviours covered by new/updated tests>

**Manual** (not automatable):
<bulleted list of anything that genuinely cannot be automated, or "None" if everything is covered>


🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

PR title and all commit messages must follow Conventional Commits:

```
<type>(<optional scope>): <description>
```

Types: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, `test`

Choose the type that best describes the change — use the issue and the diff to decide, not the issue title verbatim. Include a scope when the change is clearly contained to one module or area (e.g. `fix(auth): ...`). Omit scope when the change is broad.

## Step 10 — Present changes

Show the user:
- PR URL
- Branch name
- Files changed (from `git diff --name-only main`)
- A one-paragraph plain-English summary of what was implemented

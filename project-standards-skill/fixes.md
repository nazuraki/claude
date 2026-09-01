# Fix steps

Commands and templates for Step 4 of the project-standards skill. Substitute `{owner}`, `{repo}`, and `{default_branch}` from Step 1.

## Documentation gaps

Apply the project-docs skill's fix step (its templates, its `<!-- TODO: fill in -->` convention).

## Justfile gaps

Apply the Justfile skill's fix step.

## Other file-based gaps

`.gitignore` and workflows: create missing files from scratch or edit existing ones to add missing content. Workflows start from the templates in [workflows.md](workflows.md).

## GitHub settings

Apply with a single PATCH:
```sh
gh api repos/{owner}/{repo} \
  --method PATCH \
  --field allow_merge_commit=false \
  --field allow_rebase_merge=false \
  --field squash_merge_commit_title=PR_TITLE \
  --field squash_merge_commit_message=BLANK \
  --field allow_update_branch=true \
  --field delete_branch_on_merge=true \
  --field allow_auto_merge=false \
  --field has_wiki=false \
  --field has_discussions=false
```
Add `--field description="..."` and, when Pages is on, `--field homepage=<pages url>` with values taken from the README.

## Security

Dependabot on every repo; secret scanning on public repos only (the PATCH fails on private repos without Advanced Security):
```sh
gh api repos/{owner}/{repo}/vulnerability-alerts --method PUT
gh api repos/{owner}/{repo}/automated-security-fixes --method PUT
gh api repos/{owner}/{repo} --method PATCH --input - <<'EOF'
{ "security_and_analysis": { "secret_scanning": { "status": "enabled" }, "secret_scanning_push_protection": { "status": "enabled" } } }
EOF
```

## CODEOWNERS

Create `.github/CODEOWNERS` with a catch-all rule naming the person who approves merges (the auditing user by default; for an org repo this is still a person, not the org):
```sh
mkdir -p .github
printf '# Default reviewers for any file not matched by a more specific rule\n*\t@%s\n' "$(gh api user --jq .login)" > .github/CODEOWNERS
```
The file goes in through a PR like any other change. The ruleset below can be applied at any time, but code-owner review enforces nothing until the file is on the default branch.

## Branch rules

Create a ruleset named after the default branch, substituting the actual lint, test, and pr-title job names from the project's CI workflow. The bypass entry (`RepositoryRole` 5 = repository admin) is the ruleset equivalent of `enforce_admins: false`; release automation that pushes with an admin token depends on it.
```sh
gh api repos/{owner}/{repo}/rulesets \
  --method POST \
  --input - <<'EOF'
{
  "name": "{default_branch}",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "bypass_actors": [
    { "actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always" }
  ],
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true,
        "require_last_push_approval": false,
        "required_review_thread_resolution": true,
        "allowed_merge_methods": ["squash"]
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [
          { "context": "lint" },
          { "context": "test" },
          { "context": "pr-title" }
        ]
      }
    }
  ]
}
EOF
```

If a ruleset already targets the default branch, update it in place with the same body instead of creating a second one:
```sh
gh api repos/{owner}/{repo}/rulesets --jq '.[] | select(.target == "branch") | "\(.id) \(.name)"'
gh api repos/{owner}/{repo}/rulesets/{id} --method PUT --input - <<'EOF'
...same body...
EOF
```

Once the ruleset is active, remove classic protection so there is one source of truth:
```sh
gh api repos/{owner}/{repo}/branches/{default_branch}/protection --method DELETE
```

## Labels

Rename legacy labels first. A rename rewrites the label on every issue and PR carrying it, and a delete strips it from all of them, so confirm each rename and delete with the user before running it; creates are additive and need no confirmation., then create any still missing:
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
gh label create "accessibility" --repo {owner}/{repo} --color f143ab --description "Barrier affecting people with disabilities"        --force
gh label create "security"     --repo {owner}/{repo} --color 662259 --description "Related to PII, data, host or runtime security"    --force

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

## Manual only
- Social preview — must be uploaded via GitHub Settings → Social preview

After fixing, re-audit only the changed areas and confirm they now pass.

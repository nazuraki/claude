# Justfile Skill

Write or audit a project's Justfile for consistency with the standard recipe set.

## Triggers

- `/justfile` — audit current project's Justfile and fix inconsistencies
- `/justfile new` — scaffold a new Justfile for the current project

## Standard Recipe Set

Every Justfile follows this structure and order:

```just
# <project-name> — <one-line description>
# Requires: just, <runtime>, <key tools>   ← omit if obvious (node/pnpm)

default:
    @just --list

# Install dependencies
install:
    <package-manager> install

# [app-only: run + dev recipes here]

# [monorepo-only: workspace convenience recipes here]

# Build
build:
    <build command>

# Run all checks (lint + typecheck + test)
check: lint typecheck test

# Lint and check formatting
lint:
    <linter> check .

# Fix lint and formatting issues
fix:
    <linter> check . --write

# Type-check
typecheck:
    <tsc or pnpm -r run typecheck>

# Run tests
test:
    <test runner>

# Remove build artifacts and node_modules
clean:
    rm -rf node_modules dist .svelte-kit

# Reinstall from scratch
fresh: clean install
```

**App-only recipes** (runnable apps, not libraries) — insert after `install`:

```just
# Run (requires .env)
run:
    <start command>

# Run in dev mode
dev:
    <dev command>
```

**Monorepo workspace recipes** — insert after `dev`:

```just
# Dev <workspace> only
<workspace>:
    pnpm --filter <package> dev
```

**Docker recipes** (containerized apps only) — insert after `build`:

```just
# Build Docker image
docker-build:
    docker build -t <image-name> .

# Run Docker container locally
docker-run:
    docker run --env-file .env -p <port>:<port> <image-name>

# Push image to registry
docker-push:
    docker push <registry>/<image-name>
```

**Deploy recipe** (deployable apps only) — insert after Docker recipes (or after `build` if no Docker):

```just
# Deploy to production
deploy: build
    <deploy command>
```

For staging environments, add a separate recipe immediately after `deploy`:

```just
# Deploy to staging
deploy-staging: build
    <staging deploy command>
```

## Naming Rules

- `lint` = **read-only** (never modifies files)
- `fix` = **write-mode** auto-fix — NOT `format` (`format` is ambiguous about whether it modifies)
- `check` = CI gate — always `check: lint typecheck test`; drop `test` only if no tests exist
- `typecheck` not `type-check` — no hyphens in recipe names
- `fresh` not `reinstall` or `reset`

## Structure Rules

- `default: @just --list` — ALWAYS first, ALWAYS this exact form
- Never `default: check`, never bare `dev` as default
- Header comment line 1: `# <project-name> — <description>`
- Each recipe has a `# Comment` on the line immediately above it (no blank line between)
- One blank line between recipes
- No variables or `set` declarations unless the project specifically needs them

## Omission Rules

- Omit `test` from `check` dependencies only if the project has no tests
- Omit `run` for libraries and pure build tools
- Omit `build` for projects with no build step
- Omit `docker-build`, `docker-run`, `docker-push` for non-containerized projects
- Omit `deploy` / `deploy-staging` for libraries and projects with no deployment target
- Always include `clean` and `fresh` — cheap and consistently expected

## Package Manager Rules

- Respect whatever the project uses (npm/pnpm/bun) — don't change it
- pnpm monorepo workspace-wide: `pnpm -r run <script>`
- pnpm monorepo targeted: `pnpm --filter <pkg> <script>`

## Audit Process

1. Read the Justfile (or note it's missing)
2. Compare against the standard recipe set
3. Report findings in this format, then apply all fixes:

```
## Justfile audit: <project>

MISSING  default (@just --list)
RENAME   format → fix
MISSING  lint — read-only check separate from fix
MISSING  typecheck — standalone recipe
MISSING  clean, fresh
OK       install, dev, check, run
```

4. Apply all fixes with Edit tool (or Write for a new file)
5. Show the final Justfile after edits

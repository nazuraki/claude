# Project Standards

Requirements every repository must satisfy.

---

## README.md

- Project name and one-sentence description
- Prerequisites (runtime versions, required environment variables)
- Quickstart command (`just dev` or equivalent)
- Link to `docs/PURPOSE.md`
- License

---

## docs/PURPOSE.md

- Problem being solved (1–3 paragraphs)
- Non-goals — what this explicitly does not do
- Intended audience or users

---

## .gitignore

- Language/runtime artifacts (build output, `__pycache__`, `node_modules`, `target/`, etc.)
- `.env` and all `.env.*` variants
- IDE directories (`.idea/`, `.vscode/`)
- OS files (`.DS_Store`, `Thumbs.db`)
- Local-only config (e.g., `settings.local.json`)

---

## Justfile

### Required recipes (all projects)

| Recipe | Purpose |
|--------|---------|
| `default` | `@just --list` — ALWAYS first, ALWAYS this exact form |
| `install` | Install dependencies |
| `build` | Produce distributable artifact (omit if no build step) |
| `check` | CI gate — `check: lint typecheck test` (drop `test` only if no tests exist) |
| `lint` | Read-only linter/formatter check — never modifies files |
| `fix` | Write-mode auto-fix (NOT `format` — that name is ambiguous) |
| `typecheck` | Type-check only (no hyphens — `typecheck` not `type-check`) |
| `test` | Run the test suite |
| `clean` | Remove build artifacts and `node_modules` |
| `fresh` | `fresh: clean install` — reinstall from scratch |

### App-only recipes (runnable apps, not libraries)

Insert after `install`:

| Recipe | Purpose |
|--------|---------|
| `run` | Start the app (requires `.env`) |
| `dev` | Start in dev/watch mode |

### Docker recipes (containerized apps only)

Insert after `build`:

| Recipe | Purpose |
|--------|---------|
| `docker-build` | Build Docker image |
| `docker-run` | Run container locally with `.env` |
| `docker-push` | Push image to registry |

### Deploy recipes (deployable apps only)

Insert after Docker recipes (or after `build` if no Docker):

| Recipe | Purpose |
|--------|---------|
| `deploy` | Deploy to production (`deploy: build`) |
| `deploy-staging` | Deploy to staging (if staging environment exists) |

### Naming rules

- `lint` = read-only; `fix` = write-mode auto-fix
- `check` always depends on `lint typecheck test`
- No hyphens in recipe names (`typecheck`, not `type-check`)
- `fresh` not `reinstall` or `reset`

### Structure rules

- Header comment: `# <project-name> — <one-line description>`
- Each recipe has a `# Comment` on the line immediately above it (no blank line between comment and recipe)
- One blank line between recipes
- No `set` declarations or variables unless the project specifically needs them

---

## .github/workflows/ci.yml

- **Triggers:** `push` to `main`, all pull requests
- **Jobs:** lint (runs first), test (runs after lint passes)
- **Action versions:** pinned to a specific tag — no `@latest`; `actions/checkout` must be `v6` or newer; use the most recent stable version available for all other actions
- **Test matrix:** multi-platform or multi-version matrix where the runtime warrants it

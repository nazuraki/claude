---
name: project-docs
description: "Define, scaffold, or audit the documentation a project should have and how it is organized — for single-project repos and monorepos. Use this skill whenever the user asks what docs a project needs, how to organize documentation, where a document belongs, to set up or scaffold docs, or '/project-docs'."
---

# Project Docs

The documents every project carries, what each one is for, and where it lives. Layout differs between a single-project repo and a monorepo; both are specified below.

## Invocation

- `/project-docs` — audit the current project's documents against this skill and offer fixes
- `/project-docs new` — scaffold the required documents with `<!-- TODO: fill in -->` markers
- `/project-docs <path>` — audit the project at the given path

## Principles

- **Docs record what code cannot.** Intent, decisions, business rules, external contracts, deployment topology, open questions. Anything derivable from the codebase (file trees, route lists, symbol names, dependency versions, constants) does not belong in a doc — it goes stale and tooling answers it faster.
- **One canonical home per fact.** If a fact appears in two documents, one of them links to the other.
- **Docs live next to what they describe.** Cross-cutting docs at the root; package-specific docs in the package.
- **Short files.** A document over ~200 lines is a sign it should split or shed derivable content.
- **Every document is Markdown**, has an H1 matching its purpose, and uses relative links.

## Document catalog

### Required in every project

| Document | Purpose | Contents |
|----------|---------|----------|
| `README.md` | Front door for a new reader | Project name and one-sentence description; prerequisites (runtime versions, required env vars); quickstart command (`just install` then `just dev` or equivalent); link to `docs/PURPOSE.md`; license line |
| `docs/PURPOSE.md` | Why the project exists | Problem being solved (1–3 paragraphs); explicit non-goals; intended audience or users |
| `CONTEXT.md` | Working context for humans and agents | Architectural decisions not visible in code; business rules and thresholds (canonical definition, even if also in code); deployment topology; env var semantics; external contracts not yet implemented; open questions and deferred decisions |
| `CLAUDE.md` | Agent instructions only | Commands, conventions, guardrails. No project narrative — that belongs in `CONTEXT.md`, which `CLAUDE.md` may reference |
| `LICENSE` | Legal terms | Full license text; the README states the license name |
| `Justfile` | Task entry point | Defined by the Justfile skill (`/justfile`) — not covered here |

`README.md` is for someone who has never seen the project. `CONTEXT.md` is for someone about to change it. `docs/PURPOSE.md` is for someone deciding whether it should exist. Keep those audiences separate; do not merge the files.

`CONTEXT.md` is updated as the final step of every implementation task. Its **Open questions** section is the most valuable part of the file — never trim it.

### Optional — create only when the trigger applies

| Document | Create when |
|----------|-------------|
| `CHANGELOG.md` | The project publishes versioned releases. Otherwise PR history is the changelog |
| `CONTRIBUTING.md` | The repo accepts outside contributions. Otherwise a short "Contributing" section in the README suffices |
| `docs/decisions/NNNN-<kebab-title>.md` | An architectural decision is made that a future reader will question. One decision per file, numbered sequentially, never edited after acceptance — supersede with a new one |
| `docs/design/<kebab-title>.md` | A feature or subsystem needs a design doc, spec, or PRD before implementation |
| `docs/runbooks/<kebab-title>.md` | The project is operated in production and has procedures (deploy, rollback, incident response) |
| `.github/PULL_REQUEST_TEMPLATE.md` | The team wants a fixed PR checklist |
| `.github/ISSUE_TEMPLATE/` | The repo receives issues from people outside the core team |

Do not create `docs/` subfolders speculatively. A folder exists only when a file exists to put in it.

### Never

- Auto-generated API reference committed to the repo (generate in CI or on demand instead)
- A `docs/` mirror of the README
- Per-directory README files inside a single project's source tree (`src/foo/README.md`) — use a comment header or `CONTEXT.md`

## Single-project layout

```
.
├── README.md
├── CONTEXT.md
├── CLAUDE.md
├── LICENSE
├── Justfile
├── CHANGELOG.md            # optional
├── CONTRIBUTING.md         # optional
├── docs/
│   ├── PURPOSE.md
│   ├── decisions/          # optional, ADRs
│   ├── design/             # optional
│   └── runbooks/           # optional
└── .github/
    ├── workflows/ci.yml
    └── PULL_REQUEST_TEMPLATE.md   # optional
```

## Monorepo layout

A monorepo is one product delivered as several packages (apps, libraries, services). The root describes the product; each package describes itself only.

```
.
├── README.md               # map of the repo — see below
├── CONTEXT.md              # cross-cutting context only
├── CLAUDE.md               # repo-wide agent instructions
├── LICENSE
├── Justfile                # root recipes + `mod` per package (see Justfile skill)
├── docs/
│   ├── PURPOSE.md          # purpose of the product as a whole
│   ├── decisions/          # single ADR sequence for the whole repo
│   ├── design/             # cross-package designs
│   └── runbooks/
├── apps/<app>/
│   ├── README.md           # required
│   ├── CONTEXT.md          # only if the app has decisions the rest of the repo needn't know
│   ├── CLAUDE.md           # only for app-specific conventions
│   ├── Justfile            # per-package module
│   └── docs/design/        # only for app-specific designs
└── packages/<lib>/
    ├── README.md           # required
    └── ...                 # same rules as apps/
```

### Root documents in a monorepo

- **`README.md`** is a map, not a manual. It holds the product's one-sentence description, prerequisites that apply repo-wide, the workspace-level quickstart, a table of packages (name, one-line purpose, link to its README), and the license line. Package-specific instructions do not belong here.
- **`docs/PURPOSE.md`** covers the product. Packages do not get their own unless independently published (see below).
- **`CONTEXT.md`** holds only what spans packages: shared contracts between packages, deployment topology, repo-wide business rules, open questions that touch more than one package. Link to package `CONTEXT.md` files where they exist.
- **`docs/decisions/`** is the only ADR sequence. Decisions in a monorepo almost always affect more than one package; a single numbering avoids two ADR 0007s.
- **`CLAUDE.md`** carries repo-wide conventions. Claude Code also loads a nested `CLAUDE.md` when working inside a package, so package-level files must add to the root, never repeat it.

### Package documents in a monorepo

- **`README.md`** is required in every package. It states what the package is, how it fits into the product (one sentence, link to root README), package-specific prerequisites, and how to run its tasks (`just <package> dev`, `just <package> test`). It links back to the root for everything else.
- **`CONTEXT.md`** is allowed when the package has decisions, rules, or open questions the rest of the repo does not need. The root `CONTEXT.md` links to it.
- **`docs/PURPOSE.md`** appears only when the package is published on its own (a library on npm, a standalone CLI). Otherwise the product's purpose is the package's purpose.
- **`CHANGELOG.md`** appears only for independently versioned packages.
- **`docs/design/`** holds designs scoped to that package only. A design that touches two packages goes in the root `docs/design/`.

### Deciding root vs. package

Ask: "If this package were deleted, would this document still be true?" If yes, it belongs at the root. If no, it belongs in the package.

## Formatting rules

- Root conventional files are UPPERCASE (`README.md`, `CONTEXT.md`, `CLAUDE.md`, `LICENSE`).
- Files under `docs/` are kebab-case, except `PURPOSE.md`.
- ADRs are `NNNN-kebab-title.md`, four-digit zero-padded, starting at `0001`.
- Each file starts with a single H1; sections use H2 and H3 only.
- Links are relative paths; never absolute URLs into the same repo.
- No personal info, hostnames, internal URLs, or credentials in any document — treat every repo as public record.

## Audit process

1. Detect repo type: a monorepo has a workspace manifest (`pnpm-workspace.yaml`, `package.json` `workspaces`, `go.work`, Cargo `[workspace]`) or an `apps/` / `packages/` split. Otherwise single project.
2. Inventory every document listed in the catalog, at the root and (for monorepos) in each package.
3. For each required document: check presence, then check each listed content item.
4. For each optional document: check that its trigger applies if present, and flag any that should exist (e.g., a deployed app with no runbooks, a versioned library with no changelog).
5. Flag documents that violate **Never**, and content that is derivable from code.
6. Report in this format:

```
## Project docs audit: <project>   (<single project | monorepo, N packages>)

### Root
OK       README.md
FAIL     README.md — no prerequisites section
MISSING  docs/PURPOSE.md
FAIL     CONTEXT.md — contains a file tree (derivable; remove)
OK       CLAUDE.md
OK       LICENSE

### apps/web            (monorepo only)
MISSING  README.md
OK       CONTEXT.md

Summary: X/Y documents passing
```

7. Ask: "Would you like me to fix any of these?" On yes, create missing files from the templates below and edit existing ones. Where content needs human input, write `<!-- TODO: fill in -->`.

## Templates

`README.md`:

```markdown
# <project-name>

<one-sentence description>

## Prerequisites

- <runtime> <version>
- Environment: `<VAR>` — <what it does>

## Quickstart

    just install
    just dev

See [docs/PURPOSE.md](docs/PURPOSE.md) for why this project exists.

## License

<license name> — see [LICENSE](LICENSE).
```

`docs/PURPOSE.md`:

```markdown
# Purpose

## Problem

<!-- TODO: 1–3 paragraphs -->

## Non-goals

- <!-- TODO -->

## Audience

<!-- TODO -->
```

`CONTEXT.md`:

```markdown
# Context

## Decisions

<!-- Architectural choices not visible in code, and what was ruled out -->

## Rules and thresholds

<!-- Business rules; canonical definitions -->

## Deployment

<!-- Topology, how traffic arrives, what handles access control -->

## Environment

- `<VAR>` — <semantics>

## External contracts

<!-- Expected schemas and interfaces not yet implemented -->

## Open questions

- <!-- Never trim this section -->
```

Monorepo package `README.md`:

```markdown
# <package-name>

<one sentence: what it is and how it fits into the product>. Part of [<product>](../../README.md).

## Prerequisites

<!-- Only what differs from the root -->

## Tasks

    just <package> dev
    just <package> test
```

## Related skills

- `/project-standards` — audits the whole project; uses this skill for its documentation checks
- `/justfile` — the Justfile is a required file but its rules live there

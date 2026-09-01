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
- **Every detail directory has a summary doc.** Nobody should have to open a folder to learn what is in it (see [Detail directories](#detail-directories-and-summary-docs)).
- **Short files.** A document over ~200 lines is a sign it should split or shed derivable content.
- **Every document is Markdown**, has an H1 matching its purpose, and uses relative links.

## Document catalog

### Required in every project

| Document | Purpose | Contents |
|----------|---------|----------|
| `README.md` | Front door for a new reader | Status badge on the first line after the H1 (see below); project name and one-sentence description; prerequisites (runtime versions, required env vars); quickstart command (`just install` then `just dev` or equivalent); link to `docs/PURPOSE.md`; license line |
| `docs/PURPOSE.md` | Why the project exists | Problem being solved (1–3 paragraphs); explicit non-goals; intended audience or users |
| `CONTEXT.md` | Working context for humans and agents | Architectural decisions not visible in code; business rules and thresholds (canonical definition, even if also in code); deployment topology; env var semantics; external contracts not yet implemented; open questions and deferred decisions |
| `CLAUDE.md` | Agent instructions only | Commands, conventions, guardrails. No project narrative — that belongs in `CONTEXT.md`, which `CLAUDE.md` may reference |
| `LICENSE` | Legal terms | Public repos: full license text, and the README states the license name. Private repos: no `LICENSE` file; the README license line states that the code is proprietary and names the owner |
| `Justfile` | Task entry point | Defined by the Justfile skill (`/justfile`) — not covered here |

**Status badge.** The root README shows the project's lifecycle stage as a [shields.io](https://shields.io) static badge on the line immediately after the H1. Use the exact markdown from this table so every repo renders the same badge for the same stage:

| Stage | Meaning | Markdown |
|-------|---------|----------|
| research | Investigating whether and how to build it; no committed scope | `![Status: research](https://img.shields.io/badge/status-research-lightgrey)` |
| planning | Scope agreed, design underway, little or no code | `![Status: planning](https://img.shields.io/badge/status-planning-red)` |
| in progress | Actively being built; not usable end to end | `![Status: in progress](https://img.shields.io/badge/status-in_progress-orange)` |
| alpha | Usable by the team; incomplete and unstable | `![Status: alpha](https://img.shields.io/badge/status-alpha-yellow)` |
| beta | Feature complete for the intended audience; stabilizing | `![Status: beta](https://img.shields.io/badge/status-beta-blue)` |
| production | Released and supported | `![Status: production](https://img.shields.io/badge/status-production-brightgreen)` |

For a project no longer maintained, keep the stage badge and add `![Archived](https://img.shields.io/badge/archived-inactive)` on the same line. Other badges (CI, license, version) may follow on the same line, but the status badge comes first. Update the badge in the same change that moves the project between stages. In a monorepo, only the root README carries the badge; a package README may carry its own only when the package is independently published.

`README.md` is for someone who has never seen the project. `CONTEXT.md` is for someone about to change it. `docs/PURPOSE.md` is for someone deciding whether it should exist. Keep those audiences separate; do not merge the files.

`CONTEXT.md` is updated as the final step of every implementation task. Its **Open questions** section is the most valuable part of the file — never trim it.

### Detail directories — create when applicable

Each of these is a directory of individual detail files under `docs/`, paired with a summary doc (rules in the next section).

| Directory | Holds | Create when | Detail file naming |
|-----------|-------|-------------|--------------------|
| `docs/requirements/` | What the system must do or guarantee: functional and non-functional requirements, constraints, acceptance criteria | Requirements come from stakeholders or span more than one issue, so they need a home outside the issue tracker | `<kebab-area>.md`, one area per file (e.g. `authentication.md`, `performance.md`) |
| `docs/features/` | What the product does from the user's point of view, one feature per file: behaviour, scope, out-of-scope, links to the requirements and use cases it satisfies | The product has user-facing features whose behaviour must be agreed before or after building | `<kebab-feature>.md` |
| `docs/use-cases/` | Actor–goal interactions: primary flow, alternate flows, preconditions, postconditions | User interactions need to be spelled out step by step. Write them with the `write-use-cases` skill when it is available | `<kebab-actor-goal>.md` (e.g. `admin-revokes-api-key.md`) |
| `docs/research/` | Investigations that informed a decision: spikes, technology evaluations, benchmarks, competitor or prior-art surveys, findings and recommendations | An investigation produces findings worth keeping. A research doc feeds a decision; it does not make one | `<kebab-topic>.md`, with the date of the investigation in the front matter or first line |
| `docs/decisions/` | Architecture Decision Records: context, decision, consequences, status | An architectural decision is made that a future reader will question. One decision per file, never edited after acceptance — supersede with a new one | `NNNN-<kebab-title>.md`, four-digit zero-padded from `0001` |
| `docs/design/` | Design docs and technical specs for a feature or subsystem: approach, alternatives, data model, interfaces | A change is large enough to need a design before implementation | `<kebab-title>.md` |
| `docs/runbooks/` | Operational procedures: deploy, rollback, incident response, routine maintenance | The project is operated in production | `<kebab-procedure>.md` |
| `docs/guides/` | How to use, configure, or extend the product, one topic per file: usage, configuration, theming, integration, embedding | Users need more than the README quickstart. A guide describes the product as built; it never restates a feature or design doc | `<kebab-topic>.md` |

The flow between them: **research** informs **decisions**; **requirements** and **use cases** define what a **feature** must do; **design** says how it will be built; **runbooks** say how it is operated; **guides** tell users how to use what was built. A detail file links to the files it derives from or satisfies.

**Stable IDs.** Requirements and use cases carry IDs that are never changed or reused: `RQ-nnn` and `UC-nnn`, three digits zero-padded, one sequence of each per repo (a monorepo keeps a single root sequence). A requirement is an H2 inside its area file, `## RQ-014 <title>`, with its status on the next line. A use case's H1 is `# UC-007 <actor goal>`. Summary entries, features, and cross-references cite the ID, so a renamed file or heading never breaks a reference.

**Mockups.** Exported UI mockups (a rendered `screen.png` plus the `code.html` it was generated from, for example from Stitch) live in `docs/design/mockups/<kebab-name>/`. They are assets, not detail files: they get no entry of their own in `docs/design.md`; the design doc or feature that uses one links to it, and a mockup nothing links to is removed. Accompanying design-system notes go in `docs/design/design-system.md`, kebab-case like every other detail file.

### Optional root documents

| Document | Create when |
|----------|-------------|
| `CHANGELOG.md` | The project publishes versioned releases. Otherwise PR history is the changelog |
| `CONTRIBUTING.md` | The repo accepts outside contributions. Otherwise a short "Contributing" section in the README suffices |
| `.github/PULL_REQUEST_TEMPLATE.md` | The team wants a fixed PR checklist |
| `.github/ISSUE_TEMPLATE/` | The repo receives issues from people outside the core team |

### Never

- A `docs/` subfolder created speculatively — a folder exists only when a file exists to put in it
- Auto-generated API reference committed to the repo (generate in CI or on demand instead)
- A `docs/` mirror of the README
- Per-directory README files inside a single project's source tree (`src/foo/README.md`) — use a comment header or `CONTEXT.md`

## Detail directories and summary docs

Every detail directory `docs/<area>/` has a companion summary doc `docs/<area>.md` beside it. The summary is the index and the reader's entry point; the directory holds the detail.

```
docs/
├── decisions.md          # summary: one line per ADR, linked
└── decisions/
    ├── 0001-use-postgres.md
    └── 0002-drop-redis-cache.md
```

Rules:

- **Created together.** The summary doc is created with the first detail file, and the directory is never created without one.
- **Complete.** Every file in the directory has an entry in the summary; every entry links to a file that exists. No orphans, no dangling links.
- **One line per file.** Each entry is the file's title, a one-sentence summary, its status where the type has one (requirements: `draft` / `agreed` / `retired`; decisions: `proposed` / `accepted` / `superseded by NNNN`; research: `open` / `concluded`), and a relative link. Longer commentary belongs in the detail file.
- **Updated in the same change** that adds, supersedes, or retires a detail file.
- **Opens with a short overview** — one paragraph on what the directory covers and how it is organized, then the table.

Summary doc names: `requirements.md`, `features.md`, `use-cases.md`, `research.md`, `decisions.md`, `design.md`, `runbooks.md`, `guides.md`.

## Single-project layout

```
.
├── README.md
├── CONTEXT.md
├── CLAUDE.md
├── LICENSE                 # public repos only
├── Justfile
├── CHANGELOG.md            # optional
├── CONTRIBUTING.md         # optional
├── docs/
│   ├── PURPOSE.md
│   ├── requirements.md     # summary  ┐ when applicable
│   ├── requirements/       # detail   ┘
│   ├── features.md
│   ├── features/
│   ├── use-cases.md
│   ├── use-cases/
│   ├── research.md
│   ├── research/
│   ├── decisions.md
│   ├── decisions/
│   ├── design.md
│   ├── design/
│   ├── runbooks.md
│   ├── runbooks/
│   ├── guides.md
│   └── guides/
└── .github/
    ├── workflows/ci.yml
    ├── CODEOWNERS                 # required; rules in the project-standards skill
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
│   ├── requirements.md, requirements/   # product-level and cross-package
│   ├── features.md, features/           # features spanning packages
│   ├── use-cases.md, use-cases/         # product-level use cases
│   ├── research.md, research/           # research that informed repo-wide decisions
│   ├── decisions.md, decisions/         # single ADR sequence for the whole repo
│   ├── design.md, design/               # cross-package designs
│   ├── runbooks.md, runbooks/           # product-level operations
│   └── guides.md, guides/               # product-level user guides
├── apps/<app>/
│   ├── README.md           # required
│   ├── CONTEXT.md          # only if the app has decisions the rest of the repo needn't know
│   ├── CLAUDE.md           # only for app-specific conventions
│   ├── Justfile            # per-package module
│   └── docs/               # only package-scoped detail directories, each with its summary
│       ├── features.md, features/
│       ├── design.md, design/
│       ├── runbooks.md, runbooks/
│       └── guides.md, guides/
└── packages/<lib>/
    ├── README.md           # required
    └── ...                 # same rules as apps/
```

### Root documents in a monorepo

- **`README.md`** is a map, not a manual. It holds the product's one-sentence description, prerequisites that apply repo-wide, the workspace-level quickstart, a table of packages (name, one-line purpose, link to its README), and the license line. Package-specific instructions do not belong here.
- **`docs/PURPOSE.md`** covers the product. Packages do not get their own unless independently published (see below).
- **`CONTEXT.md`** holds only what spans packages: shared contracts between packages, deployment topology, repo-wide business rules, open questions that touch more than one package. Link to package `CONTEXT.md` files where they exist.
- **`docs/decisions/`** is the only ADR sequence. Decisions in a monorepo almost always affect more than one package; a single numbering avoids two ADR 0007s. Package-scoped decisions still live here, tagged with the package in the title.
- **`docs/requirements/`**, **`docs/use-cases/`**, and **`docs/research/`** stay at the root by default — requirements and use cases describe the product, and research informs product-level decisions. Only a package that is independently published gets its own.
- **`CLAUDE.md`** carries repo-wide conventions. Claude Code also loads a nested `CLAUDE.md` when working inside a package, so package-level files must add to the root, never repeat it.

### Package documents in a monorepo

- **`README.md`** is required in every package. It states what the package is, how it fits into the product (one sentence, link to root README), package-specific prerequisites, and how to run its tasks (`just <package> dev`, `just <package> test`). It links back to the root for everything else.
- **`CONTEXT.md`** is allowed when the package has decisions, rules, or open questions the rest of the repo does not need. The root `CONTEXT.md` links to it.
- **`docs/PURPOSE.md`** appears only when the package is published on its own (a library on npm, a standalone CLI). Otherwise the product's purpose is the package's purpose.
- **`CHANGELOG.md`** appears only for independently versioned packages.
- **`docs/features/`**, **`docs/design/`**, **`docs/runbooks/`**, **`docs/guides/`** hold items scoped to that package only, each with its summary doc. An item that touches two packages goes in the root directory of the same name.
- Package summary docs may link into root detail files (a package feature satisfying a root requirement); root summaries never link into package directories except from the root `README.md` package table.

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
4. For each detail directory present: check the summary doc exists, lists every file, has no dangling links, and carries status where the type has one. Check detail files follow the naming rule for their type.
5. For each detail directory or optional document absent: flag it when its trigger clearly applies (a deployed app with no runbooks, a versioned library with no changelog, ADRs referencing a spike that has no research doc, usage or configuration docs sitting loose under `docs/` instead of in `docs/guides/`).
6. Flag documents that violate **Never**, content that is derivable from code, package docs that belong at the root or vice versa, requirements or use cases without stable IDs, mockups nothing links to, a private repo carrying a `LICENSE` file, and a public repo without one.
7. Report in this format:

```
## Project docs audit: <project>   (<single project | monorepo, N packages>)

### Root
OK       README.md
FAIL     README.md — no status badge under the H1 (or stage not one of the six)
FAIL     README.md — no prerequisites section
MISSING  docs/PURPOSE.md
FAIL     CONTEXT.md — contains a file tree (derivable; remove)
OK       CLAUDE.md
OK       LICENSE (public) / OK       README license line states proprietary (private)
FAIL     docs/decisions.md — missing entry for 0003-adopt-pnpm.md
MISSING  docs/runbooks/ — project has a deploy recipe but no runbooks
OK       docs/research.md

### apps/web            (monorepo only)
MISSING  README.md
OK       CONTEXT.md
FAIL     docs/design/ — no docs/design.md summary

Summary: X/Y documents passing
```

8. Ask: "Would you like me to fix any of these?" On yes, create missing files from the templates below and edit existing ones. Where content needs human input, write `<!-- TODO: fill in -->`. When generating a missing summary doc, derive each entry's title and one-line summary from the detail file's H1 and first paragraph.

## Templates

Templates for every document above are in [templates.md](templates.md) alongside this skill. Read that file when scaffolding or fixing.

## Related skills

- `/project-standards` — audits the whole project; uses this skill for its documentation checks
- `/justfile` — the Justfile is a required file but its rules live there
- `write-use-cases` — authoring guidance for files under `docs/use-cases/`

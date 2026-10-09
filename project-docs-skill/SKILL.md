---
name: project-docs
description: "Define, scaffold, or audit a project's documentation against the Project Documentation and Project Details specifications — for single-project repos and monorepos. Use this skill whenever the user asks what docs a project needs, how to organize documentation, where a document or fact belongs, to set up or scaffold docs, or '/project-docs'."
---

# Project Docs

Applies two specifications to a project: audit it, scaffold it, or answer where something belongs.

- **Project Documentation 1.3.0**: which documents a project carries, where they live, and the shape of each kind of
  detail file. Cited as `§2.4` (section 2, rule 4).
- **Project Details 1.1.0**: the README opening, meaning the details line (type, status, version, license badges), the
  description, and where other badges go. Cited as `Details §2.1`.

The specs are the only source of the rules. This skill holds the procedure, the report format, and the templates.

## Load the specs first

Before any audit, scaffold, or placement answer, read both specs' raw Markdown:

    curl -fsSL https://lepid-labs.github.io/spec/project-documentation/v1.3.0/index.md
    curl -fsSL https://lepid-labs.github.io/spec/project-details/v1.1.0/index.md

Use `curl` (or read local copies under `site/spec/` in the lepid-labs.github.io checkout), not a summarizing web
fetch: the audit depends on exact wording. If neither is available, stop and say so rather than auditing from memory.
If `https://lepid-labs.github.io/spec/` lists a newer version of either, tell the user and ask whether to audit against
it.

## Invocation

- `/project-docs` — audit the current project and offer fixes
- `/project-docs new` — scaffold the required documents with `<!-- TODO: fill in -->` markers
- `/project-docs <path>` — audit the project at the given path

## Scope

The spec covers the documents people read to understand a project. It does not cover agent instruction files
(`CLAUDE.md`, `AGENTS.md`) or CI and repository settings (the Project Operations spec), which `/project-standards`
owns, or task runners, which `/justfile` owns.

## Audit process

1. Detect the layout: a monorepo has a workspace manifest (`pnpm-workspace.yaml`, `package.json` `workspaces`,
   `go.work`, Cargo `[workspace]`) or an `apps/` / `packages/` split. Otherwise it is a single project.
2. Inventory every document the spec names, at the root and, for a monorepo, in each package.
3. Check each item below against the spec section cited. Record OK, FAIL (a MUST broken), WARN (a SHOULD broken,
   including a detail file that departs from its shape), or MISSING.

| Check | Spec |
|-------|------|
| `README.md`: H1, one- or two-sentence description, prerequisites with every environment variable's meaning, install and run commands, link to `docs/PURPOSE.md`, license line linking `LICENSE` | §2 |
| README details line: the paragraph right after the H1 holds the type badge, then the status badge, then a version badge if and only if the type is library or native app and it publishes versioned releases (never for a service or web app), then optionally a license badge, and nothing else; exact badge Markdown; `archived` is a status, not an extra badge | Details §1, §2, §3, §4 |
| Version badge: public release source → the shields.io badge that reads it (`label=version`); private source (private repo releases, private GitHub Packages) → static `version-<version>-blue` badge that never needs a manual edit, so the release automation rewrites it (check with `/project-standards`) | Details §5 |
| License badge, if present: last on the details line and nowhere else; SPDX id with `--` for hyphens, or the fixed `proprietary` badge; matches `LICENSE` | Details §6 |
| README description: the paragraph right after the details line, no badges in it; other badges (CI, conformance) only after it | Details §1 |
| Monorepo badges: type badge only at the root; package details line only for an independently published package, and then status, version, and a license badge only if the package has its own `LICENSE` | Details §7 |
| `LICENSE`: present at the root; full license text, or copyright owner and "all rights reserved"; parts under other terms named | §3 |
| `docs/PURPOSE.md`: problem in one to two sentences; `Audience` section | §4 |
| `docs/requirements/` and `docs/requirements.md`: present, at least one area file, requirements carry `RQ-nnn` IDs with status | §5, §8 |
| Knowledge in its home, per the table in §1.8; derivable content absent; documents under about 200 lines | §1 |
| `CONTEXT.md` or another catch-all context file: flag it, and map each part of it to its home | §1.9 |
| Detail directories: created only when their trigger applies; flag a directory whose trigger clearly applies but is absent (a deployed project with no runbooks). Never flag a missing `docs/decisions/` from the code or its history: its trigger is a design question being asked (§6.4) | §6.1 |
| Detail files link what they derive from or satisfy; research recommends but never decides; mockups only under `docs/design/mockups/`, each linked | §6.2, §6.3, §6.6 |
| Detail-file shapes, per kind: requirement area §6.8, feature §6.9, use case §6.10, research (`Status`, `Date`, Question, Method, Findings, Recommendation) §6.11, decision (`Status`, Context, Options, Decision, Consequences) §6.12, design (Approach, Alternatives, Interfaces, Risks) §6.13, runbook (Prerequisites, Steps, Verify, Recovery) §6.14, guide §6.15. A departure is a WARN, not a FAIL | §6.7–§6.15 |
| Summary docs: one per detail directory, opening paragraph, every file listed, no dangling links, status where the type has one | §7 |
| Decision records: each answers a design question at a pivot point and links the research behind it; WARN on a record that cites no research or records a local choice, an inherited standard, a convention, or an implementation detail. Numbering, status values (`open`, `proposed`, `accepted`, `superseded by NNNN`); a changed decision revised in its own record, with an optional `History` section, rather than replaced by a new one | §6.4, §6.12, §7.4, §11.3 |
| Stable IDs: `RQ-nnn` as `## RQ-nnn <title>` with status on the next line, `UC-nnn` in the use case H1, one sequence each, never reused | §8 |
| `docs/open-questions.md`, if present: one line per question, none that already has a decision record | §9.3 |
| `CHANGELOG.md` and `CONTRIBUTING.md` where their triggers apply; `CONTRIBUTING.md` follows its shape (Development setup, Checks, Making a change, Reporting issues with a private security channel, License) | §9 |
| Monorepo: root README is a map with a package table; decisions, requirements, use cases, and research at the root; package READMEs; no package PURPOSE, CHANGELOG, or LICENSE unless independently published; root summaries never link into packages | §10 |
| Formatting: single H1, H2 and H3 only, naming and case, relative links, nothing private | §11 |
| Prohibited items | §12 |

4. Report in this format:

```
## Project docs audit: <project>   (<single project | monorepo, N packages>) — docs 1.3.0, details 1.1.0

### Root
OK       README.md
FAIL     README.md — details line has the status badge before the type badge (Details §2.1)
FAIL     README.md — CI badge on the details line; move it after the description (Details §2.3)
FAIL     README.md — lists DATABASE_URL without saying what it is (§2.4)
MISSING  docs/requirements/ (§5.1)
FAIL     CONTEXT.md — catch-all context file (§1.9); its deployment notes belong in docs/runbooks/
OK       LICENSE
FAIL     docs/decisions.md — missing entry for 0003-adopt-pnpm.md (§7.5)
WARN     docs/decisions/0002-choose-a-queue.md — no Options section (§6.12)
MISSING  docs/runbooks/ — the project is deployed but has no runbooks (§6.1)

### apps/web            (monorepo only)
MISSING  README.md (§10.6)
FAIL     docs/design/ — no docs/design.md summary (§7.1)

Summary: X/Y checks passing, Z warnings
```

5. Ask: "Would you like me to fix any of these?"

## Fix process

- Create missing documents from [templates.md](templates.md) and edit existing ones. Where content needs human input,
  write `<!-- TODO: fill in -->`.
- When generating a summary doc, take each entry's title and one-sentence summary from the detail file's H1 and first
  paragraph.
- When fixing badge order, move a license badge to the end of the details line and other badges (CI, conformance) to
  a line after the description. Replace a legacy `Archived` badge with the `archived` status (Details §4.1).
- When the type badge is missing, infer the type from what the repo releases (a compiled binary is a native app; server
  code whose main interface is an API is a service; a server or static build whose main interface is pages is a web
  app; published packages with no runnable deliverable is a library). State the inference and confirm it before
  writing the badge. Never write two types; if the repo releases two kinds of thing, say so and leave the badge to the
  user.
- When splitting a `CONTEXT.md`, move each part to its home per §1.8: rules and thresholds to requirements,
  design decisions that meet §6.4 to decision records (a choice that changes an existing decision revises that record
  and adds a `History` line), open questions to open decision records or `docs/open-questions.md`, deployment
  topology to a runbook, environment variable meanings to the README, development setup to `CONTRIBUTING.md`, and
  the reasoning behind one piece of code to a design's Alternatives or a comment in that code. Then delete the file
  and repoint anything that linked to it.
- Never write decision records reconstructed from the code, commits, or pull requests (§6.4). If a past design
  question looks worth a record, ask the user whether its research or discussion survives, and write the record only
  from that.
- When splitting a flat document into a detail directory, renumber `UC-n`/`DD-n` style IDs into the spec's form
  without changing the numbers, and rewrite each file to its shape (§6.7–§6.15).
- Before moving or renaming any document, search the repo for paths into `docs/`: build and site scripts, CI
  workflows, tests that read docs by name, tool config that lists documents, `package.json` `homepage` URLs, and code
  comments that cite a document or a decision number. Update them in the same change.
- When the documents disagree with the code, the code wins: correct the document and say so in the report.
- Wrap Markdown prose at 120 characters.

## Related skills

- `/project-standards` — audits the whole project against Project Operations; uses this skill for its documentation
  checks and reads the README type badge (Details §3) to choose the release shape
- `/justfile` — the Justfile rules
- `write-use-cases` — authoring guidance for files under `docs/use-cases/`

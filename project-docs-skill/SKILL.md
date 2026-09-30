---
name: project-docs
description: "Define, scaffold, or audit a project's documentation against the Project Documentation and Project Details specifications — for single-project repos and monorepos. Use this skill whenever the user asks what docs a project needs, how to organize documentation, where a document or fact belongs, to set up or scaffold docs, or '/project-docs'."
---

# Project Docs

Applies two specifications to a project: audit it, scaffold it, or answer where something belongs.

- **Project Documentation 1.1.0**: which documents a project carries and where they live. Cited as `§2.4` (section 2,
  rule 4).
- **Project Details 1.0.0**: the README opening, meaning the details line (type, status, version badges), the
  description, and where other badges go. It builds on Project Documentation. Cited as `Details §2.1`.

The specs are the only source of the rules. This skill holds the procedure, the report format, and the templates.

## Load the specs first

Before any audit, scaffold, or placement answer, read both specs' raw Markdown:

    curl -fsSL https://lepid-labs.github.io/spec/project-documentation/v1.1.0/index.md
    curl -fsSL https://lepid-labs.github.io/spec/project-details/v1.0.0/index.md

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
3. Check each item below against the spec section cited. Record OK, FAIL (present but wrong), or MISSING.

| Check | Spec |
|-------|------|
| `README.md`: H1, one- or two-sentence description, prerequisites with every environment variable's meaning, install and run commands, link to `docs/PURPOSE.md`, license line linking `LICENSE` | §2 |
| README details line: the paragraph right after the H1 holds the type badge, then the status badge, then a version badge if and only if the project publishes versioned releases, and nothing else; exact badge Markdown; `archived` is a status, not an extra badge | Details §1, §2, §3, §4 |
| Version badge: reads the version from where releases are published (shields.io, `label=version`), never a hand-edited static badge | Details §5 |
| README description: the paragraph right after the details line, no badges in it; other badges (CI, license, conformance) only after it | Details §1 |
| Monorepo badges: type badge only at the root; package details line only for an independently published package, and then status and version only | Details §6 |
| `LICENSE`: present at the root; full license text, or copyright owner and "all rights reserved"; parts under other terms named | §3 |
| `docs/PURPOSE.md`: problem in one to two sentences; `Audience` section | §4 |
| `docs/requirements/` and `docs/requirements.md`: present, at least one area file, requirements carry `RQ-nnn` IDs with status | §5, §9 |
| Knowledge in its home, per the table in §1.7; derivable content absent | §1 |
| `CONTEXT.md` or another catch-all context file: flag it, and map each part of it to its home | §1.8 |
| Detail directories: created only when their trigger applies; flag a directory whose trigger clearly applies but is absent (a deployed project with no runbooks) | §7 |
| Summary docs: one per detail directory, opening paragraph, every file listed, no dangling links, status where the type has one | §8 |
| Decision records: numbering, status values (`open`, `proposed`, `accepted`, `superseded by NNNN`), accepted records unedited | §7.4, §8.4, §12.3 |
| `docs/open-questions.md`, if present: one line per question, none that already has a decision record | §10.3 |
| `CHANGELOG.md` and `CONTRIBUTING.md` where their triggers apply | §10 |
| Monorepo: root README is a map; decisions, requirements, use cases, and research at the root; package READMEs; no package PURPOSE, CHANGELOG, or LICENSE unless independently published | §11 |
| Formatting: single H1, H2 and H3 only, naming and case, relative links, nothing private | §12 |
| Prohibited items | §13 |

4. Report in this format:

```
## Project docs audit: <project>   (<single project | monorepo, N packages>) — docs 1.1.0, details 1.0.0

### Root
OK       README.md
FAIL     README.md — details line has the status badge before the type badge (Details §2.1)
FAIL     README.md — CI badge on the details line; move it after the description (Details §2.3)
FAIL     README.md — lists DATABASE_URL without saying what it is (§2.4)
MISSING  docs/requirements/ (§5.1)
FAIL     CONTEXT.md — catch-all context file (§1.8); its deployment notes belong in docs/runbooks/
OK       LICENSE
FAIL     docs/decisions.md — missing entry for 0003-adopt-pnpm.md (§8.5)
MISSING  docs/runbooks/ — the project is deployed but has no runbooks (§7.1)

### apps/web            (monorepo only)
MISSING  README.md (§11.6)
FAIL     docs/design/ — no docs/design.md summary (§8.1)

Summary: X/Y checks passing
```

5. Ask: "Would you like me to fix any of these?"

## Fix process

- Create missing documents from [templates.md](templates.md) and edit existing ones. Where content needs human input,
  write `<!-- TODO: fill in -->`.
- When generating a summary doc, take each entry's title and one-sentence summary from the detail file's H1 and first
  paragraph.
- When fixing badge order, move non-details badges (CI, license, conformance, a legacy `Archived` badge) to a line
  after the description; replace a legacy `Archived` badge with the `archived` status (Details §4.1).
- When the type badge is missing, infer the type from what the repo releases (a compiled binary is a native app; server
  code whose main interface is an API is a service; a server or static build whose main interface is pages is a web
  app; published packages with no runnable deliverable is a library). State the inference and confirm it before
  writing the badge. Never write two types; if the repo releases two kinds of thing, say so and leave the badge to the
  user.
- When splitting a `CONTEXT.md`, move each part to its home per §1.7: rules and thresholds to requirements,
  architectural choices to accepted decision records, open questions to open decision records or
  `docs/open-questions.md`, deployment topology to a runbook, environment variable meanings to the README. Then delete
  the file and repoint anything that linked to it.
- Wrap Markdown prose at 120 characters.

## Related skills

- `/project-standards` — audits the whole project against Project Operations; uses this skill for its documentation
  checks and reads the README type badge (Details §3) to choose the release shape
- `/justfile` — the Justfile rules
- `write-use-cases` — authoring guidance for files under `docs/use-cases/`

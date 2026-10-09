# Project Docs Templates

Templates used by the project-docs skill's `new` and fix steps. Section references (`§2`) are to the Project
Documentation 1.3.0 spec, and `Details §n` to Project Details 1.1.0. Keep `<!-- TODO: fill in -->` markers where
content needs human input. A detail file may leave out a section that does not apply, add its own after the listed
ones, and, when short, cover the sections in order as plain paragraphs (§6.7).

`README.md` (§2, Details §1–§6). Keep the version badge only for a library or native app that publishes versioned
releases, using the source from Details §5; a private repo uses the static `version-<version>-blue` badge. The
license badge is optional; use the SPDX id (Details §6), or `proprietary-lightgrey`. A monorepo root adds a package
table and carries no package-specific instructions (§10.2):

```markdown
# <project-name>

![Type: <type>](https://img.shields.io/badge/type-<type>-blueviolet) ![Status: <stage>](https://img.shields.io/badge/status-<stage>-<color>) ![Version](https://img.shields.io/github/v/release/<owner>/<repo>?label=version) [![License: <spdx>](https://img.shields.io/badge/license-<spdx>-blue)](LICENSE)

<one- or two-sentence description>

<other badges, if any: CI, conformance>

See [docs/PURPOSE.md](docs/PURPOSE.md) for why this project exists.

## Prerequisites

- <runtime> <version>
- `<VAR>`: <what it controls, its format, and its default if any>

## Quickstart

    <install command>
    <run command>

## Packages

| Package | Purpose |
|---------|---------|
| [<name>](<path>/README.md) | <one line> |

## License

<license name>; see [LICENSE](LICENSE).
<!-- proprietary: "Proprietary: © <owner>, all rights reserved; see [LICENSE](LICENSE)." -->
```

`LICENSE` for a proprietary project (§3); an open-source project uses the license's full text instead:

```text
Copyright (c) <year> <owner>. All rights reserved.

No part of this repository may be copied, modified, or distributed without
the prior written permission of <owner>.
```

`docs/PURPOSE.md` (§4):

```markdown
# Purpose

<!-- TODO: the problem being solved, in one to two sentences -->

## Audience

<!-- TODO: who the project is for -->
```

Requirements area file, `docs/requirements/<area>.md` (§6.8, §8.3):

```markdown
# <Area> requirements

<one sentence: what this area covers>

## RQ-001 <requirement title>

Status: draft

<!-- TODO: one checkable obligation; thresholds as a number and a unit. Acceptance criteria where one sentence
cannot carry them; a link to the decision that set it, if one did -->
```

Feature, `docs/features/<feature>.md` (§6.9):

```markdown
# <Feature name>

<!-- TODO: what it lets a user do, and for whom. Link its design and any mockups -->

## Behaviour

## Scope

## Out of scope

## Satisfies

- RQ-<nnn>, UC-<nnn>
```

Use case, `docs/use-cases/<actor-goal>.md` (§6.10, §8.3):

```markdown
# UC-001 <actor goal>

<!-- TODO: the primary actor, their goal, and what starts the interaction -->

## Preconditions

## Primary flow

1. <!-- TODO: one action by the actor or the system, by intent, not interface -->

## Alternate flows

- **2a.** <!-- TODO: the branch, and where it rejoins or ends -->

## Postconditions
```

Research document, `docs/research/<topic>.md` (§6.11):

```markdown
# <Topic>

Status: open
Date: <YYYY-MM-DD>

## Question

<!-- TODO: what it set out to answer, and the decision or requirement it serves -->

## Method

## Findings

## Recommendation

<!-- What the findings suggest, and a link to the decision record that takes it up -->
```

Decision record, `docs/decisions/NNNN-<title>.md` (§6.4, §6.12):

```markdown
# NNNN <Title>

Status: <open | proposed | accepted | superseded by NNNN>

## Context

<!-- The design question, the forces that make it one, and a link to the research it relies on -->

## Options

<!-- Each alternative, with what favours and what counts against it -->

## Decision

<!-- The choice, stated so it can be followed, or "No choice is made yet." while open -->

## Consequences

<!-- What follows, good and bad: the work it creates, what it rules out, what it makes harder -->

## History

<!-- Optional: one line per earlier decision, "<YYYY-MM-DD>: <what it decided>" -->
```

Design, `docs/design/<title>.md` (§6.13):

```markdown
# <Change or component>

<!-- TODO: what is being built, and the requirements or feature it serves -->

## Approach

## Alternatives

## Interfaces

<!-- Link the code or schema that defines a contract rather than copying it -->

## Risks
```

Runbook, `docs/runbooks/<procedure>.md` (§6.14). One runbook describes the deployment topology; the others link it:

```markdown
# <Do the procedure>

<one sentence: when to run it and what it achieves>

## Prerequisites

<!-- Access, tools, approvals; name secrets and roles, never their values -->

## Steps

1. <!-- TODO: one action, the exact command, and what the reader sees when it worked -->

## Verify

## Recovery
```

Guide, `docs/guides/<topic>.md` (§6.15):

```markdown
# <Task or topic, as a user would put it>

<!-- TODO: who the guide is for, and what they can do once they have followed it -->

## Prerequisites

<!-- Only what goes beyond the README's prerequisites -->

## <The task's own sections>
```

Summary doc, `docs/<area>.md` (§7):

```markdown
# <Area>

<one paragraph: what this directory covers and how it is organized>

| Title | Summary | Status |
|-------|---------|--------|
| [<title>](<area>/<file>.md) | <one sentence> | <status> |
```

`docs/open-questions.md` (§9.3, optional):

```markdown
# Open questions

Questions not yet worth a decision record, one line each. A question that gets a record in
[decisions.md](decisions.md) is removed from this list.

- <!-- TODO -->
```

`CONTRIBUTING.md` (§9.2), when the project accepts outside contributions:

```markdown
# Contributing

<!-- TODO: which contributions are welcome, and which are not -->

## Development setup

<!-- Beyond the README's prerequisites and install commands, which this links to -->

## Checks

<!-- The lint, type-check and test commands CI runs, and which must pass -->

## Making a change

<!-- Branching, the commit or PR title convention, and what a change includes: tests, and the docs it affects -->

## Reporting issues

<!-- Where to report bugs and request features, and the private channel for security issues -->

## License

<!-- The terms contributions are accepted under, and any sign-off they need -->
```

Monorepo package `README.md` (§10.6):

```markdown
# <package-name>

<one sentence: what it is and how it fits into the product>. Part of [<product>](../../README.md).

## Prerequisites

<!-- Only what differs from the root -->

## Tasks

    <how to run this package's tasks>
```

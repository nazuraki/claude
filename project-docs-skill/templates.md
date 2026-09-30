# Project Docs Templates

Templates used by the project-docs skill's `new` and fix steps. Section references (`§2`) are to the Project
Documentation 1.0.0 spec. Keep `<!-- TODO: fill in -->` markers where content needs human input.

`README.md` (§2, §6):

```markdown
# <project-name>

![Status: <stage>](https://img.shields.io/badge/status-<stage>-<color>) ![Type: <type>](https://img.shields.io/badge/type-<type>-blueviolet)

<one-sentence description>

See [docs/PURPOSE.md](docs/PURPOSE.md) for why this project exists.

## Prerequisites

- <runtime> <version>
- `<VAR>`: <what it controls, its format, and its default if any>

## Quickstart

    <install command>
    <run command>

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

Requirements area file, `docs/requirements/<area>.md` (§5, §9):

```markdown
# <Area> requirements

<one sentence: what this area covers>

## RQ-001 <requirement title>

Status: draft

<!-- TODO: what the project must do or guarantee, and how to tell it does -->
```

Decision record, `docs/decisions/NNNN-<title>.md` (§7.4, §8.4):

```markdown
# NNNN <Title>

Status: <open | proposed | accepted | superseded by NNNN>

## Context

<!-- The question, and the forces that make it one -->

## Decision

<!-- The choice made, or "Not yet made." with the options, while open -->

## Consequences

<!-- What follows from the choice, good and bad -->
```

`docs/open-questions.md` (§10.3, optional):

```markdown
# Open questions

Questions not yet worth a decision record, one line each. A question that gets a record in
[decisions.md](decisions.md) is removed from this list.

- <!-- TODO -->
```

Runbook, `docs/runbooks/<procedure>.md` (§7):

```markdown
# <Procedure>

<one sentence: when to run this>

1. <!-- TODO: step -->
```

Other detail files (features, use cases, research, design, guides) (§7):

```markdown
# <Title>

<one paragraph summary; research adds its date>

<!-- body; link the requirements, use cases, or decisions this derives from -->
```

Summary doc, `docs/<area>.md` (§8):

```markdown
# <Area>

<one paragraph: what this directory covers and how it is organized>

| Title | Summary | Status |
|-------|---------|--------|
| [<title>](<area>/<file>.md) | <one sentence> | <status> |
```

Monorepo package `README.md` (§11.6):

```markdown
# <package-name>

<one sentence: what it is and how it fits into the product>. Part of [<product>](../../README.md).

## Prerequisites

<!-- Only what differs from the root -->

## Tasks

    <how to run this package's tasks>
```

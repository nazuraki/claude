# Project Docs Templates

Templates used by the project-docs skill's `new` and fix steps. Keep `<!-- TODO: fill in -->` markers where content needs human input.

`README.md`:

```markdown
# <project-name>

**Status:** <research | planning | in progress | alpha | beta | production>

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

<!-- Architectural choices not visible in code, and what was ruled out. Link ADRs in docs/decisions.md -->

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

Summary doc (`docs/<area>.md`):

```markdown
# <Area>

<one paragraph: what this directory covers and how it is organized>

| Title | Summary | Status |
|-------|---------|--------|
| [<title>](<area>/<file>.md) | <one sentence> | <status> |
```

Detail file (any area; ADRs add **Status**, **Context**, **Decision**, **Consequences** sections):

```markdown
# <Title>

**Status:** <status> · **Date:** <YYYY-MM-DD>
**Related:** [<requirement>](../requirements/<file>.md), [<ADR>](../decisions/<file>.md)

<!-- body -->
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


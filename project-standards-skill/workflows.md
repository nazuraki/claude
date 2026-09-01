# Workflow templates

Templates for the workflows the project-standards skill checks. Substitute the angle-bracket placeholders; keep everything else. Every action is pinned to a major tag. Bump the pins together when one moves.

## `ci.yml` — the PR gate

Jobs run Justfile recipes so the job names map 1:1 onto required status checks and CI never drifts from what developers run locally.

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: extractions/setup-just@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v6
        with:
          node-version-file: .nvmrc
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: just lint
      - run: just typecheck

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: extractions/setup-just@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v6
        with:
          node-version-file: .nvmrc
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: just test

  # Only when the repo has a Dockerfile
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: extractions/setup-just@v4
      - run: just docker-build
```

Swap the setup steps for the project's runtime (`actions/setup-python`, `dtolnay/rust-toolchain@stable` plus `Swatinem/rust-cache`).

**Monorepo variant.** `lint` stays a single root job (`just lint`, `just typecheck` run workspace-wide). Tests run per package through the Justfile modules, named so a developer can tell which package failed, behind a gate job that the ruleset requires:

```yaml
  test-package:
    name: test (${{ matrix.package }})
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        package: [core, bot]          # every Justfile module with a test recipe
    steps:
      # checkout, setup-just, runtime setup, install as above
      - run: just ${{ matrix.package }} test

  test:
    needs: test-package
    if: always()
    runs-on: ubuntu-latest
    steps:
      - run: test "${{ needs.test-package.result }}" = success
```

Checks show as `test (core)`, `test (bot)`, and `test`; the ruleset requires `lint`, `test`, and `pr-title` only, so adding a package never touches the ruleset. Name matrix entries after what varies. A runtime version on its own is not a name: use a version matrix only for a published library that supports more than one major, and then name it `test (core, node 22)`. Desktop apps matrix over platform: `build (macos)`, `build (windows)`.

## `pr-guidelines.yml` — PR title lint

Required in every repo. Squash commit titles come from PR titles, so this is the only enforcement of Conventional Commits on `main` history. The job id `pr-title` is a required status check in the ruleset.

```yaml
name: PR guidelines

on:
  pull_request:
    types: [opened, edited, synchronize, reopened]

permissions:
  pull-requests: read

jobs:
  pr-title:
    runs-on: ubuntu-latest
    steps:
      - uses: amannn/action-semantic-pull-request@v5
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          types: |
            build
            chore
            ci
            docs
            feat
            fix
            perf
            refactor
            revert
            style
            test
          requireScope: false
```

Optional second job `tests-with-code`: diff the PR against its base, and fail when source files under `src/` changed without any `*.test.*` or `*.spec.*` file (or, for Rust, without a `#[cfg(test)]` block or a file under `tests/`) changing too. Print the untested files and tell the author to add tests or explain in the PR description why the change is untestable. Do not make it a required check; it is a nudge, not a gate.

## `publish.yml` — container image to GHCR

Required for any repo with a Dockerfile that deploys as a container. Every push to `main` publishes `latest` and `sha-<short>`; a `v*` tag publishes semver tags.

```yaml
name: Publish

on:
  push:
    branches: [main]
    tags: ["v*"]

concurrency:
  group: publish-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read
  packages: write

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: docker/setup-qemu-action@v3
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository_owner }}/<image-name>
          tags: |
            type=raw,value=latest,enable={{is_default_branch}}
            type=sha,prefix=sha-
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
      - uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Monorepo variant.** Keep the name `publish.yml`. Add a `changes` job that diffs the push range against each image's input paths and emits a `matrix.include` of `{image, context, dockerfile}` entries; the `publish` job runs `strategy.matrix: ${{ fromJSON(needs.changes.outputs.matrix) }}` with `cache-from`/`cache-to` scoped per image. Tag pushes and unknown base commits publish every image.

## `pages.yml` — GitHub Pages

Required when Pages is enabled. Pages must be set to deploy from a workflow, and the repo `homepage` is the Pages URL.

```yaml
name: Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: extractions/setup-just@v4
      # runtime setup + install as in ci.yml
      - run: just build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: <build output dir>

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

Add a `paths:` filter to the push trigger when only part of the repo feeds the site.

## Release shapes

Which shape applies depends on what the project ships. A repo has at most one.

### Library — published package

`release.yml` runs on every push to `main`. It computes the next version from the Conventional Commit titles since the last tag, writes the bump commit `chore(release): vX.Y.Z`, tags, and creates the GitHub release. A separate `publish.yml` on `v*` tags publishes the package with provenance.

- `permissions: contents: write`; `concurrency: { group: release, cancel-in-progress: false }`
- The bump commit is pushed with an admin token stored as `RELEASE_TOKEN`, which uses the ruleset's admin bypass. Guard the job with `if: github.event_name == 'workflow_dispatch' || !startsWith(github.event.head_commit.message, 'chore(release):')` so the bump does not release itself.
- `publish.yml` for a package: trigger `push.tags: ["v*"]`, `permissions: { contents: read, id-token: write }`, `npm publish --provenance --access public` via OIDC trusted publishing. No registry token in secrets.

### Desktop app — installable binaries

`release.yml` runs on `workflow_dispatch` with a boolean `major` input. A `prepare` job computes the version and changelog (`orhun/git-cliff-action@v4`) and pushes the tag. A `build` job calls a reusable `build.yml` (`on: workflow_call` with a `tag` input) that runs a platform matrix (`macos-latest`, `windows-latest`, add `ubuntu-latest` when shipped) and uploads the installers to the GitHub release with `softprops/action-gh-release@v2`.

### Service — container deployed to a host

No `release.yml`. `publish.yml` above is the release pipeline: every merge to `main` ships `latest`, and a hand-cut `vX.Y.Z` tag marks a release and publishes semver tags. The host pulls the image; `just deploy` triggers that pull (for example by calling the deployment backplane's deploy endpoint). A GitHub release object per tag is optional. Examples: the edge proxy, the deployment backplane, dashboards.

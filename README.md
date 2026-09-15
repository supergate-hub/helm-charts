# Supergate Helm Charts

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Charts and repackaged platform images used by Supergate's GitOps repositories.
This repository holds **what** is deployed (charts, image definitions, pinned upstream
versions). Environment values, hostnames, addresses and Argo CD applications live in
the private infra-ops repository.

## Usage

[Helm](https://helm.sh) must be installed to use the charts.

```console
helm repo add supergate https://supergate-hub.github.io/helm-charts
helm search repo supergate
```

Argo CD applications reference charts by exact version:

```yaml
source:
  repoURL: https://supergate-hub.github.io/helm-charts
  chart: <chart>
  targetRevision: <exact version>
```

Every released chart is also pushed to `oci://ghcr.io/supergate-hub/charts`, the same archive at a
second address for consumers that speak OCI:

```console
helm pull oci://ghcr.io/supergate-hub/charts/<chart> --version <exact version>
```

The Pages index stays the address this organization's Argo CD applications use. A chart reaches
GHCR only after chart-releaser published it, so the two never hold different content for a
version. Packages must be public: private packages consume the organization's shared Actions and
Packages storage, and these charts are public anyway.

## Charts

Upstream charts are vendored **unchanged** at a pinned version. `charts.lock.json` records
the source, the chart reference and the sha256 of the pulled archive, so any copy can be
re-verified with `helm pull <chartRef> --version <version>` and `sha256sum`.

| Chart | Version | App version | Upstream |
| --- | --- | --- | --- |
| cert-manager | v1.21.1 | v1.21.1 | https://charts.jetstack.io |
| external-secrets | 2.10.0 | v2.10.0 | https://charts.external-secrets.io |
| gha-runner-scale-set | 0.14.2 | 0.14.2 | oci://ghcr.io/actions/actions-runner-controller-charts |
| gha-runner-scale-set-controller | 0.14.2 | 0.14.2 | oci://ghcr.io/actions/actions-runner-controller-charts |
| harbor | 1.19.2 | 2.15.2 | https://helm.goharbor.io |
| kube-prometheus-stack | 89.2.2 | v0.93.1 | https://prometheus-community.github.io/helm-charts |
| metallb | 0.16.1 | v0.16.1 | https://metallb.github.io/metallb |
| traefik | 41.5.0 | v3.7.13 | https://traefik.github.io/charts |
| vault | 0.34.1 | 2.0.4 | https://helm.releases.hashicorp.com |

Supergate-owned charts wrap an upstream dependency with the objects the platform needs:

| Chart | Wraps | Notes |
| --- | --- | --- |
| sst-gateway | traefik 41.5.0 | Management web gateway: Gateway API, scoped RBAC, certificate mirroring, canary, network policies. See `charts/sst-gateway/README.md`. |

Their versions come from Conventional Commit messages via release-please: `feat` bumps the
minor version, `fix` the patch version, `feat!` or a `BREAKING CHANGE` footer the major
version. Merging the generated release pull request updates `Chart.yaml` and `CHANGELOG.md`;
chart-releaser then publishes `<chart>-<version>`. Pull requests are squash-merged, so the
pull request title is the commit message that drives this.

## Updating a vendored chart

Run the **Import upstream chart** workflow (`workflow_dispatch`) with the chart name, exact
version and source. It pulls the archive, verifies and extracts it with
`scripts/vendor_chart.py`, updates `charts.lock.json` and pushes an `import/<chart>-<version>`
branch. Open the pull request from the link in the job summary; lint runs on the pull
request and chart-releaser publishes the release after merge.

Which version to import is tracked automatically. Every Monday the **Upstream chart check**
workflow compares `charts.lock.json` against the upstream repositories and keeps a single
`chart-updates` issue in sync with the answer, including the `gh workflow run` line for each
import; it closes the issue once nothing is behind. Dependabot cannot do this — it only sees
declared dependencies — so it covers the subchart of every Supergate-owned chart
(`charts/sst-*`) and the actions pinned in `.github/workflows/`.

## Layout

| Path | Contents |
| --- | --- |
| `charts/<name>/` | Charts published to the index (vendored upstream or Supergate-owned). |
| `charts.lock.json` | Source and archive digest of every vendored chart. |
| `images/<name>/` | Repackaged public upstream images published to `ghcr.io/supergate-hub/<name>` (currently `sst-traefik`). |
| `.github/workflows/lint-test.yaml` | Pull request: `ct lint` for changed charts; `ct install` in kind for Supergate-owned charts. |
| `.github/workflows/release.yaml` | Push to `main`: chart-releaser packages changed charts, creates a GitHub Release per chart version, updates `index.yaml` on `gh-pages` and mirrors the same archives to `oci://ghcr.io/supergate-hub/charts`. |
| `.github/workflows/import-chart.yaml` | Manual import of an upstream chart version into `charts/`. |
| `.github/workflows/chart-upstream-check.yaml` | Weekly: vendored chart versions against upstream, tracked in one issue (`scripts/check_upstream_charts.py`). |
| `.github/workflows/image-gateway.yaml` | Build, scan and publish the gateway image; see `images/gateway/README.md`. |
| `.github/workflows/pr-title.yaml` | Pull request: title must be a Conventional Commit. |
| `.github/workflows/commit-attribution.yaml` | Pull request and `main`: commits carry an organization author and no `Co-authored-by` trailer. |
| `.github/workflows/release-please.yaml` | Push to `main`: release pull requests for Supergate-owned charts (`release-please-config.json`). |

## Contributing

- Bump `version` in `Chart.yaml` for every Supergate-owned chart change; `ct lint` rejects unchanged versions. Vendored charts keep the upstream version.
- Pin upstream dependencies and images by exact version or digest.
- Never commit environment values, internal hostnames, addresses or credentials. This repository is public.
- Pull request titles follow Conventional Commits and are squash-merged; for `charts/sst-*` the title type decides the next version.
- Commit as the organization identity (`@supergate.cc` or a `supergate-*` noreply address) and never add a `Co-authored-by` trailer: the squash merge turns a commit author into that trailer on `main`, crediting the wrong account permanently. `scripts/check_commit_attribution.py` enforces this.

## License

[Apache 2.0](LICENSE). Vendored upstream charts and repackaged images keep their own licenses (for example `images/gateway/LICENSE.traefik`).

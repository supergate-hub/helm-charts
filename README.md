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

## Layout

| Path | Contents |
| --- | --- |
| `charts/<name>/` | Charts published to the index. Upstream charts are vendored unchanged at a pinned version; Supergate charts wrap upstream dependencies with the extra objects the platform needs. |
| `images/<name>/` | Repackaged public upstream images published to `ghcr.io/supergate-hub/<name>` (currently `sst-traefik`). |
| `.github/workflows/lint-test.yaml` | Pull request: `ct lint` and `ct install` in kind for changed charts. |
| `.github/workflows/release.yaml` | Push to `main`: chart-releaser packages changed charts, creates a GitHub Release per chart version and updates `index.yaml` on `gh-pages`. |
| `.github/workflows/image-gateway.yaml` | Build, scan and publish the gateway image; see `images/gateway/README.md`. |
| `.github/workflows/helm-index-update.yml` | Manual import of an upstream chart version into `charts/`. |

## Contributing

- Bump `version` in `Chart.yaml` for every chart change; `ct lint` rejects unchanged versions.
- Pin upstream dependencies and images by exact version or digest.
- Never commit environment values, internal hostnames, addresses or credentials. This repository is public.
- Pull request titles follow Conventional Commits.

## License

[Apache 2.0](LICENSE). Vendored upstream charts and repackaged images keep their own licenses (for example `images/gateway/LICENSE.traefik`).

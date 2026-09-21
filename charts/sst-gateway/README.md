# sst-gateway

Supergate's management web gateway: the upstream Traefik chart plus the objects the
platform needs around it, so that infra-ops only carries values.

What the chart adds on top of Traefik:

- `Namespace` with the restricted Pod Security Standard (optional).
- Gateway API v1.6.1 standard CRDs and the safe-upgrades admission policy, rendered as
  templates with sync-wave `-20`.
- `GatewayClass`, `Gateway` (HTTPS wildcard listener + HTTP listener) and canary routes.
- Scoped RBAC: Traefik reads only this namespace plus namespace and GatewayClass metadata.
- cert-manager `Certificate` issued in the issuer's namespace and a CronJob that mirrors
  the leaf Secret into the gateway namespace without access to the CA (optional).
- Canary backend, Kubernetes NetworkPolicies (default deny plus exact flows), Cilium
  policies and a `PrometheusRule` (all optional).

## Values that must come from the consumer

The defaults are neutral so the chart lints and installs in a throwaway cluster. A real
deployment sets at least:

| Key | Purpose |
| --- | --- |
| `gateway.wildcardHostname`, `gateway.hostname` | Listener hostnames |
| `certificate.*`, `certSync.enabled` | Issuer, DNS names and leaf mirroring |
| `networkPolicy.allowedCidrs` | Client networks allowed to reach the listeners |
| `networkPolicy.backends` | Traefik egress to file-provider backends in other namespaces: `namespace`, `podLabels`, `port` per entry |
| `scheduling.nodeAffinity`, `scheduling.tolerations`, `dns.nameserver`, `clusterDomain` | Placement and resolver |
| `cilium.*`, `prometheusRule.*` | Only when those CRDs exist |
| `traefik.image`, `traefik.providers.kubernetesGateway.statusAddress`, `traefik.service`, `traefik.providers.file`, `traefik.affinity`, `traefik.resources` | Upstream Traefik values for the environment |

Use release name `sst-traefik`: the Traefik subchart derives its object names from it and
the network and Cilium policies select `app.kubernetes.io/name: traefik`.

## Argo CD

```yaml
sources:
  - repoURL: https://supergate-hub.github.io/helm-charts
    chart: sst-gateway
    targetRevision: 1.0.0
    helm:
      releaseName: sst-traefik
      skipCrds: true          # keeps the Traefik subchart's crds/ out; Gateway API CRDs are templates
      valueFiles: [$values/platform/gateway/values.yaml]
  - repoURL: <values repository>
    targetRevision: main
    ref: values
```

## Known difference from the previously rendered manifests

The Traefik chart exposes no `enableServiceLinks` setting, so the Traefik pod keeps the
Kubernetes default (`true`) where the former renderer forced `false`. Every other object
renders identically with the same values.

<!-- Title: Conventional Commit; it becomes the squash commit. For charts/sst-* the type sets the next version: feat = minor, fix = patch, feat! = major. Examples: feat(sst-gateway): add HTTP listener / chore(charts): import cert-manager v1.21.1 / build(images): bump traefik to 3.7.14 -->

## Summary

<!-- What changes and why. This repository is public: no internal hostnames, IPs, credentials or environment values. Those belong in infra-ops values. -->

## Checklist

- [ ] Charts: `Chart.yaml` version bumped for every changed chart (`ct lint` enforces it); `ct install` passes in kind
- [ ] Charts: upstream dependency versions pinned exactly in `Chart.yaml`; `Chart.lock` committed
- [ ] Images: upstream image digest, base digest and version label bumped together; the PR workflow scan passed
- [ ] No secrets, private values or environment-specific configuration
- [ ] Consumers noted: which infra-ops Application or values file must change after release

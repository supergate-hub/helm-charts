# sst-traefik image

Repackages the unchanged upstream Traefik binary into a distroless static base and
publishes it as `ghcr.io/supergate-hub/sst-traefik`.

## Why not the official image

The official `traefik` image is Alpine based. Its OS packages (OpenSSL) carried
High findings on every scan so far, while the Traefik binary itself had none. The
platform image gate rejects any High or Critical finding, so the binary is copied
into `gcr.io/distroless/static-debian13` with no package manager, shell or OS
packages. The image contains only public upstream software: no configuration,
credentials or application code. See infra-ops ADR 0009.

## Pins

| Input | Where |
| --- | --- |
| Upstream Traefik image | `FROM docker.io/library/traefik@sha256:…` in `Dockerfile` |
| Distroless base | `FROM gcr.io/distroless/static-debian13@sha256:…` in `Dockerfile` |
| Traefik version | `org.opencontainers.image.version` label in `Dockerfile` |

Bump all three together in one pull request. The workflow reads the version label
to tag the published image.

## Workflow (`.github/workflows/image-gateway.yaml`)

- Pull request: build an OCI archive, scan it with Trivy (High/Critical fail the
  job), and scan the official image of the same version for comparison. Nothing is
  published and no artifact is stored.
- Push to `main`: same build and scan, then push to GHCR with tags
  `<version>`, `<version>-<short sha>` and `sha-<sha>`, rescan the pushed digest,
  and write the digest to the job summary. GHCR packages of this public repository
  are public and do not consume Actions storage.
- The official-image comparison is informational. When it reports zero High and
  Critical findings for the pinned version, open a pull request that switches the
  consumers to the official digest and retires this repackaging.

## Consumers

infra-ops references the pushed digest from its gateway values. Harbor can mirror
the image from GHCR with a replication rule so that cluster nodes keep pulling from
`harbor.sst.internal`.

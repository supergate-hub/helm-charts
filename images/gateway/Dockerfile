# Preserve the upstream binary; omit the unused vulnerable Alpine/OpenSSL stack.
FROM docker.io/library/traefik@sha256:f86a2cab1b5c649070c49f883c743dd32d8485a56e3368c5f93b9e91f1e91259 AS upstream
FROM gcr.io/distroless/static-debian13@sha256:1c2c046bc09ed40fad370b599a0b1ae7987f55b01e247cf27a7c27cd97e5bbc7
COPY --from=upstream /usr/local/bin/traefik /usr/local/bin/traefik
COPY LICENSE.traefik /usr/share/doc/traefik/LICENSE
ARG SOURCE_REVISION
LABEL org.opencontainers.image.source="https://github.com/supergate-hub/helm-charts" \
      org.opencontainers.image.revision="${SOURCE_REVISION}" \
      org.opencontainers.image.version="3.7.13"
USER 65532:65532
ENTRYPOINT ["/usr/local/bin/traefik"]

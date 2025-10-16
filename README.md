# Supergate Helm Charts

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This Repo includes Helm Charts used by Supergate.

## Usage

[Helm](https://helm.sh) must be installed to use the charts.
Please refer to Helm's [documentation](https://helm.sh/docs/) to get started.

Once Helm is set up properly, add the repository as follows:

```console
helm repo add supergate https://supergate-hub.github.io/helm-charts
```

You can then run `helm search repo supergate` to see the charts.


## Available Charts and Versions

The table below lists the charts currently provided and their corresponding application versions based on the repository's `index.yaml`.

| Chart | Chart Version | App Version |
| --- | --- | --- |
| harbor | 1.17.1 | 2.13.1 |
| kafka-cluster | 0.1.0 | 0.1.0 |
| kafka-ui | 0.6.2 | v0.6.2 |
| logstash | 8.5.1 | 8.5.1 |
| minio | 5.4.0 | RELEASE.2024-12-18T13-15-44Z |
| opensearch | 2.19.0 | 2.13.0 |
| opensearch-dashboards | 2.17.0 | 2.13.0 |
| rook-ceph | v1.18.2 | v1.18.2 |
| rook-ceph-cluster | v1.18.2 | v1.18.2 |
| strimzi-kafka-operator | 0.47.0 | 0.47.0 |

Note: This table is generated from the `index.yaml` at the repository root. Please let us know if you find any discrepancies.


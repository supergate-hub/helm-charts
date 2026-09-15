{{/* Namespace holding every namespaced object of this chart. */}}
{{- define "sst-gateway.namespace" -}}
{{ .Values.namespace.name }}
{{- end -}}

{{/* Pod-level security context shared by the canary and the certificate sync job. */}}
{{- define "sst-gateway.podSecurityContext" -}}
runAsNonRoot: true
runAsUser: 1000
runAsGroup: 1000
seccompProfile:
  type: RuntimeDefault
{{- end -}}

{{/* Container security context shared by the canary and the certificate sync job. */}}
{{- define "sst-gateway.containerSecurityContext" -}}
allowPrivilegeEscalation: false
readOnlyRootFilesystem: true
capabilities:
  drop: [ALL]
{{- end -}}

{{/* Placement (affinity, tolerations, DNS) shared by the canary and the certificate sync job. */}}
{{- define "sst-gateway.placement" -}}
{{- with .Values.scheduling.nodeAffinity }}
affinity:
  nodeAffinity:
    {{- toYaml . | nindent 4 }}
{{- end }}
{{- with .Values.scheduling.tolerations }}
tolerations:
  {{- toYaml . | nindent 2 }}
{{- end }}
{{- with .Values.dns.nameserver }}
dnsPolicy: None
dnsConfig:
  nameservers: [{{ . | quote }}]
{{- end }}
{{- end -}}

{{/* Egress rule to the cluster DNS. */}}
{{- define "sst-gateway.dnsEgress" -}}
- to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: {{ .Values.dns.kubeDnsNamespace }}
      podSelector:
        matchLabels:
          {{- toYaml .Values.dns.kubeDnsLabels | nindent 10 }}
  ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
{{- end -}}

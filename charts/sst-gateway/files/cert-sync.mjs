// Copies ONE cert-manager leaf certificate, never the issuing CA key.
// API responses and credentials must never be logged.
import https from 'node:https';
import {readFile} from 'node:fs/promises';
import {X509Certificate, createPrivateKey, createPublicKey, timingSafeEqual} from 'node:crypto';
const ns = '{{ include "sst-gateway.namespace" . }}', name = '{{ .Values.gateway.tlsSecretName }}';
const source = '/api/v1/namespaces/{{ .Values.certificate.namespace }}/secrets/' + name;
const target = '/api/v1/namespaces/' + ns + '/secrets';
const base = '/var/run/secrets/kubernetes.io/serviceaccount/';
const ca = await readFile(base + 'ca.crt');
const token = (await readFile(base + 'token', 'utf8')).trim();
async function request(path, method = 'GET', body) {
  const bytes = body && Buffer.from(JSON.stringify(body));
  return new Promise((resolve, reject) => {
    const q = https.request({hostname: 'kubernetes.default.svc.{{ .Values.clusterDomain }}', port: 443, path, method, ca,
      headers: {authorization: 'Bearer ' + token, 'content-type': 'application/json', ...(bytes ? {'content-length': bytes.length} : {})}}, r => {
      const chunks = []; let size = 0;
      r.on('data', b => {size += b.length; if (size > 65536) r.destroy(); else chunks.push(b);});
      r.on('error', () => reject(Error('api_body_failed')));
      r.on('end', () => {try {resolve({status: r.statusCode, body: JSON.parse(Buffer.concat(chunks))});} catch {reject(Error('api_json_failed'));}});
    });
    q.setTimeout(10000, () => q.destroy()); q.on('error', () => reject(Error('api_request_failed'))); q.end(bytes);
  });
}
try {
  const src = await request(source);
  if (src.status !== 200 || src.body.type !== 'kubernetes.io/tls') throw Error('source_unavailable');
  const data = Object.fromEntries(['tls.crt', 'tls.key', 'ca.crt'].map(key => [key, src.body.data[key]]));
  if (Object.values(data).some(v => typeof v !== 'string')) throw Error('source_incomplete');
  const cert = new X509Certificate(Buffer.from(data['tls.crt'], 'base64'));
  const root = new X509Certificate(Buffer.from(data['ca.crt'], 'base64'));
  if (cert.ca || !cert.verify(root.publicKey) || !cert.checkHost('gateway.sst.internal') || !cert.checkHost('grafana.sst.internal') ||
      Date.parse(cert.validFrom) > Date.now() || Date.parse(cert.validTo) < Date.now() + 86400000) throw Error('invalid_leaf');
  const pub = createPublicKey(createPrivateKey(Buffer.from(data['tls.key'], 'base64'))).export({type: 'spki', format: 'der'});
  if (!timingSafeEqual(pub, cert.publicKey.export({type: 'spki', format: 'der'}))) throw Error('key_mismatch');
  const previous = await request(target + '/' + name);
  if (![200, 404].includes(previous.status)) throw Error('target_unavailable');
  if (previous.status === 200 && previous.body.metadata.labels?.['sst.supergate.cc/cert-sync'] !== name) throw Error('foreign_target');
  if (previous.status === 200 && Object.entries(data).every(([key, value]) => previous.body.data?.[key] === value)) {
    console.log('Gateway leaf certificate unchanged.');
  } else {
    const body = {apiVersion: 'v1', kind: 'Secret', metadata: {name, namespace: ns,
      labels: {'sst.supergate.cc/cert-sync': name}, ...(previous.status === 200 ? {resourceVersion: previous.body.metadata.resourceVersion} : {})},
      type: 'kubernetes.io/tls', data};
    const result = await request(target + (previous.status === 200 ? '/' + name : ''), previous.status === 200 ? 'PUT' : 'POST', body);
    if (![200, 201].includes(result.status)) throw Error('sync_failed');
    console.log('Gateway leaf certificate synchronized.');
  }
} catch {
  console.error('Gateway certificate sync failed; existing target retained.'); process.exitCode = 1;
}

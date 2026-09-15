"""Report vendored charts whose upstream has published a newer version.

Reads charts.lock.json and asks Helm for the newest stable upstream version of every vendored
chart: `helm search repo` for classic repositories, `helm show chart` for OCI references, which
resolves the registry's newest tag. Prints a Markdown report on stdout and, with
--json-out, writes the raw findings to a file. Prereleases are ignored because
`helm search repo` skips them without --devel. Usage: check_upstream_charts.py [--json-out PATH]
"""
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r'^v?(\d+)\.(\d+)\.(\d+)')


def key(version):
    """Comparable tuple for a version, or None when it is not plain semver."""
    m = SEMVER.match(version)
    return tuple(int(g) for g in m.groups()) if m else None


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def latest_from_repo(chart, source):
    repo = 'upstream-' + chart
    run('helm', 'repo', 'add', repo, source, '--force-update')
    run('helm', 'repo', 'update', repo)
    found = json.loads(run('helm', 'search', 'repo', f'{repo}/{chart}', '--versions', '-o', 'json'))
    # helm search matches on substring, so kube-prometheus-stack also returns prometheus-node-exporter.
    versions = [e['version'] for e in found if e['name'] == f'{repo}/{chart}']
    return versions[0] if versions else None


def latest_from_oci(chart_ref):
    # helm show chart without --version resolves the registry's newest tag.
    shown = run('helm', 'show', 'chart', chart_ref)
    for line in shown.splitlines():
        if line.startswith('version:'):
            return line.split(':', 1)[1].strip().strip('"\'')
    return None


def check(entry):
    chart, pinned, source = entry['name'], entry['version'], entry['source']
    try:
        if source.startswith('oci://'):
            latest = latest_from_oci(entry['chartRef'])
        else:
            latest = latest_from_repo(chart, source)
    except subprocess.CalledProcessError as exc:
        output = (exc.stderr or exc.stdout or '').strip().splitlines()
        return {'name': chart, 'pinned': pinned, 'source': source, 'error': output[-1] if output else 'helm failed'}
    if latest is None:
        return {'name': chart, 'pinned': pinned, 'source': source, 'error': 'no version found upstream'}
    newer = key(latest) is not None and key(pinned) is not None and key(latest) > key(pinned)
    if not newer and latest.lstrip('v') != pinned.lstrip('v'):
        # Non-semver versions on either side: report the difference and let a human judge.
        newer = key(latest) is None or key(pinned) is None
    return {'name': chart, 'pinned': pinned, 'latest': latest, 'source': source, 'outdated': newer}


def report(results):
    outdated = [r for r in results if r.get('outdated')]
    errors = [r for r in results if r.get('error')]
    lines = []
    if outdated:
        lines += ['| Chart | Pinned | Upstream | Source |', '| --- | --- | --- | --- |']
        lines += [f"| {r['name']} | {r['pinned']} | {r['latest']} | {r['source']} |" for r in outdated]
        lines += ['', 'Import one with the **Import upstream chart** workflow:', '']
        lines += ['```console'] + [
            f"gh workflow run import-chart.yaml -f chart={r['name']} -f version={r['latest']} -f source={r['source']}"
            for r in outdated] + ['```']
    else:
        lines.append('Every vendored chart is pinned to the newest upstream version.')
    if errors:
        lines += ['', '### Not checked', '']
        lines += [f"- `{r['name']}` ({r['source']}): {r['error']}" for r in errors]
    return '\n'.join(lines)


if __name__ == '__main__':
    lock = json.loads((ROOT / 'charts.lock.json').read_text())
    results = [check(e) for e in lock['charts']]
    args = sys.argv[1:]
    if args[:1] == ['--json-out']:
        if len(args) != 2:
            sys.exit(__doc__)
        Path(args[1]).write_text(json.dumps(results, indent=2) + '\n')
    elif args:
        sys.exit(__doc__)
    print(report(results))

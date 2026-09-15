"""Extract a pulled chart archive into charts/<name> unchanged and record it in charts.lock.json.

Fail-closed: the archive must contain only regular files and directories under <name>/,
no links or path traversal. The chart directory is replaced wholesale so nothing from an
older version survives. Usage: vendor_chart.py ARCHIVE CHART VERSION SOURCE CHART_REF
"""
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def vendor(archive, chart, version, source, chart_ref):
    archive = Path(archive)
    sha = hashlib.sha256(archive.read_bytes()).hexdigest()
    dest = ROOT / 'charts' / chart
    with tarfile.open(archive) as tar:
        members = tar.getmembers()
        for m in members:
            inside = m.name == chart or m.name.startswith(chart + '/')
            if not inside or '..' in m.name.split('/') or not (m.isfile() or m.isdir()):
                raise ValueError('unexpected archive entry: ' + m.name)
        if dest.exists():
            shutil.rmtree(dest)
        tar.extractall(ROOT / 'charts', members=members, filter='data')
    chart_yaml = (dest / 'Chart.yaml').read_text()
    app = next((line.split(':', 1)[1].strip().strip('"\'') for line in chart_yaml.splitlines() if line.startswith('appVersion:')), None)
    declared = next((line.split(':', 1)[1].strip().strip('"\'') for line in chart_yaml.splitlines() if line.startswith('version:')), None)
    if declared != version.lstrip('v') and declared != version:
        raise ValueError(f'Chart.yaml version {declared} does not match requested {version}')
    lock_path = ROOT / 'charts.lock.json'
    lock = json.loads(lock_path.read_text()) if lock_path.exists() else {'schemaVersion': 1, 'charts': []}
    entry = {'name': chart, 'version': version, 'appVersion': app, 'source': source, 'chartRef': chart_ref,
             'archive': archive.name, 'sha256': sha, 'pulledAt': datetime.date.today().isoformat()}
    lock['charts'] = [c for c in lock.get('charts', []) if c['name'] != chart] + [entry]
    lock['charts'].sort(key=lambda c: c['name'])
    lock.setdefault('note', 'Vendored upstream charts, unchanged. Re-verify with: helm pull <chartRef> --version <version>; sha256sum must match.')
    lock_path.write_text(json.dumps(lock, indent=2) + '\n')
    print(f'{chart} {version} appVersion={app} sha256={sha}')


if __name__ == '__main__':
    if len(sys.argv) != 6:
        sys.exit(__doc__)
    vendor(*sys.argv[1:])

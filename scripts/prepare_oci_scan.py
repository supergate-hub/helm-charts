"""Convert a verified OCI archive to a new, path-safe scanner input directory.

BuildKit writes an OCI layout tar whose index also carries provenance attestation
manifests. Trivy needs a directory layout, and the archive is untrusted input for
the scanner, so extraction is fail-closed: exact checksum, bounded size, only the
OCI layout entries, no links, and every blob re-verified against its digest name.
"""
import hashlib
from pathlib import Path
import re
import tarfile


def unpack(archive, checksum, destination):
    if destination.exists() or not re.fullmatch(r'[a-f0-9]{64}', checksum):
        raise ValueError('New destination and SHA256 required')
    if archive.stat().st_size > 500_000_000:
        raise ValueError('Archive too large')
    if hashlib.sha256(archive.read_bytes()).hexdigest() != checksum:
        raise ValueError('Archive digest mismatch')
    with tarfile.open(archive) as tar:
        entries = tar.getmembers()
        names = set()
        if len(entries) > 1000 or sum(m.size for m in entries) > 500_000_000:
            raise ValueError('Expanded archive too large')
        for entry in entries:
            safe = (entry.isdir() and entry.name.rstrip('/') in ('blobs', 'blobs/sha256')
                    or entry.isfile() and re.fullmatch(r'(?:index.json|oci-layout|blobs/sha256/[a-f0-9]{64})', entry.name))
            if entry.name in names or not safe:
                raise ValueError('Duplicate, linked or unexpected OCI entry')
            names.add(entry.name)
        if not {'index.json', 'oci-layout'} <= names:
            raise ValueError('OCI metadata missing')
        destination.mkdir(mode=0o700)
        for entry in entries:
            if not entry.isfile():
                continue
            path = destination / entry.name
            data = tar.extractfile(entry).read()
            if entry.name.startswith('blobs/') and hashlib.sha256(data).hexdigest() != path.name:
                raise ValueError('OCI blob digest mismatch')
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            path.write_bytes(data)
            path.chmod(0o600)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('archive', type=Path)
    parser.add_argument('checksum_file', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    unpack(args.archive, args.checksum_file.read_text().split()[0], args.destination)

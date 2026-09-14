import hashlib
import io
from pathlib import Path
import tarfile
import tempfile
import unittest

from scripts.prepare_oci_scan import unpack


class OciScanTests(unittest.TestCase):
    def archive(self, root, names):
        path = root / 'image.tar'
        with tarfile.open(path, 'w') as tar:
            for name, kind, data in names:
                info = tarfile.TarInfo(name)
                info.type = kind
                info.size = len(data)
                if kind == tarfile.SYMTYPE:
                    info.linkname = '/etc/passwd'
                tar.addfile(info, io.BytesIO(data))
        return path, hashlib.sha256(path.read_bytes()).hexdigest()

    def test_valid_layout_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            digest = hashlib.sha256(b'test').hexdigest()
            path, checksum = self.archive(root, [
                ('index.json', tarfile.REGTYPE, b'{}'),
                ('oci-layout', tarfile.REGTYPE, b'{}'),
                ('blobs/sha256/' + digest, tarfile.REGTYPE, b'test'),
            ])
            unpack(path, checksum, root / 'out')
            self.assertEqual((root / 'out/blobs/sha256' / digest).read_bytes(), b'test')
            with self.assertRaises(ValueError):
                unpack(path, checksum, root / 'out')

    def test_unsafe_entries_and_bad_blob_digest_are_rejected(self):
        cases = [
            [('../escape', tarfile.REGTYPE, b'x')],
            [('index.json', tarfile.SYMTYPE, b'')],
            [('index.json', tarfile.REGTYPE, b'{}')],
            [('blobs/sha256/' + '0' * 64, tarfile.REGTYPE, b'x')],
        ]
        for extra in cases:
            with self.subTest(extra=extra), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                path, checksum = self.archive(root, [
                    ('index.json', tarfile.REGTYPE, b'{}'),
                    ('oci-layout', tarfile.REGTYPE, b'{}'),
                ] + extra)
                with self.assertRaises(ValueError):
                    unpack(path, checksum, root / 'out')

    def test_archive_checksum_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _ = self.archive(root, [])
            with self.assertRaises(ValueError):
                unpack(path, '0' * 64, root / 'out')


if __name__ == '__main__':
    unittest.main()

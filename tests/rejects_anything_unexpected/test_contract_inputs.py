import os
from pathlib import Path
import tempfile
import unittest

from wirth.validate import validate
from validator_support import ValidatorTestCase


class ContractInputTests(ValidatorTestCase):
    def test_invalid_contract_name_does_not_allow_reading_symlink_or_directory(self):
        path = self.root / 'contracts/.hidden.md'
        target = self.root / 'source.md'
        target.write_text(self.text.replace('A promise', ''))
        path.symlink_to(target)
        result = self.denied_cli(target)
        self.assert_cli_errors(result, [
            "contracts/.hidden.md: invalid contract filename '.hidden.md'",
            'contracts/.hidden.md: symlinks are not allowed'])
        path.unlink()
        path.mkdir()
        self.assertCountEqual(validate(), [
            "contracts/.hidden.md: invalid contract filename '.hidden.md'",
            'contracts/.hidden.md: must resolve to a regular file'])

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'FIFO requires POSIX')
    def test_invalid_contract_name_does_not_allow_reading_fifo(self):
        os.mkfifo(self.root / 'contracts/.pipe.md')
        result = self.cli('validate')
        self.assert_cli_errors(result, [
            "contracts/.pipe.md: invalid contract filename '.pipe.md'",
            'contracts/.pipe.md: must resolve to a regular file'])

    def test_contract_files_must_not_be_symlinks(self):
        path = self.root / 'contracts/one.md'
        path.unlink()
        (self.root / 'source.md').write_text(self.text)
        for target in ['../source.md', 'missing', 'one.md']:
            with self.subTest(target=target):
                path.symlink_to(target)
                try:
                    self.assertCountEqual(validate(), ['contracts/one.md: symlinks are not allowed'])
                finally:
                    path.unlink()
        path.mkdir()
        self.assertCountEqual(validate(), ['contracts/one.md: must resolve to a regular file'])

    def test_unexpected_entries_are_reported(self):
        for name in ['new.MD', 'new.md.bak', 'old.json', 'notes', '.hidden']:
            path = self.root / 'contracts' / name
            path.write_text('{}')
            with self.subTest(name=name):
                self.assertCountEqual(validate(), [
                    f'contracts/{name}: unexpected entry; expected a direct *.md regular file'])
            path.unlink()
        nested = self.root / 'contracts/nested'
        nested.mkdir()
        (nested / 'x.md').write_text('{}')
        self.assertCountEqual(validate(), [
            'contracts/nested: unexpected entry; expected a direct *.md regular file'])

    def test_symlinked_discovery_directory_fails(self):
        directory = self.root / 'contracts'
        directory.rename(self.root / 'inputs')
        with tempfile.TemporaryDirectory() as outside:
            (Path(outside) / 'one.md').write_text(self.text)
            for target in [self.root / 'inputs', Path(outside)]:
                with self.subTest(target=target):
                    directory.symlink_to(target, target_is_directory=True)
                    self.assertEqual(validate(), ['cannot discover contracts/: symlinks are not allowed'])
                    directory.unlink()
        for target in ['missing', 'contracts']:
            directory.symlink_to(target)
            self.assertEqual(validate(), ['cannot discover contracts/: symlinks are not allowed'])
            directory.unlink()
        directory.write_text('not a directory')
        self.assertEqual(validate(), ['cannot discover contracts/: must resolve to a directory'])

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'FIFO requires POSIX')
    def test_contract_fifo_fails_without_blocking(self):
        os.mkfifo(self.root / 'contracts/pipe.md')
        result = self.cli('validate')
        self.assert_cli_errors(result, [
            'contracts/pipe.md: must resolve to a regular file'])

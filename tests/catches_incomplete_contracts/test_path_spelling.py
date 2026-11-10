import os
from unittest.mock import patch

from wirth.validate import validate
from validator_support import ValidatorTestCase


class PathSpellingTests(ValidatorTestCase):
    def test_wrong_case_is_rejected_on_a_filesystem_that_accepts_it(self):
        self.evidence('directory/Proof.py')
        wrong = self.folder / 'DIRECTORY/proof.py'
        if not wrong.exists():
            self.skipTest('requires a case-insensitive filesystem; alias does not resolve here')
        self.assertTrue(wrong.samefile(self.folder / 'directory/Proof.py'))
        for reference in ['DIRECTORY/Proof.py', 'directory/proof.py']:
            with self.subTest(reference=reference):
                self.write_check(reference)
                component = 'DIRECTORY' if reference.startswith('DIRECTORY/') else 'proof.py'
                self.assertCountEqual(validate(), [
                    f'contracts/one.md:6: evidence reference: path spelling does not match an existing entry: {component!r}'])

    def test_discovery_directory_spelling_is_exact_when_filesystem_ignores_case(self):
        directory = self.root / 'contracts'
        directory.rename(self.root / 'Contracts')
        if not directory.exists():
            self.skipTest('requires a case-insensitive filesystem; alias does not resolve here')
        self.assertTrue(directory.samefile(self.root / 'Contracts'))
        self.assertCountEqual(validate(), ["cannot discover contracts/: path spelling does not match an existing entry: 'contracts'"])

    def test_exact_membership_with_controlled_directory_listings(self):
        # Supplementary membership check: these real paths exist, but the controlled
        # listing reports another spelling. This is not a real alias-resolution test.
        self.evidence('directory/Proof.py')
        self.write_check('directory/Proof.py')
        real_listdir = os.listdir
        for parent, name, listed, expected in [
                (self.root, 'contracts', 'Contracts',
                 ["cannot discover contracts/: path spelling does not match an existing entry: 'contracts'"]),
                (self.root / 'tests', 'complete_contracts', 'Complete_contracts',
                 ["contracts/one.md:5: tests folder: path spelling does not match an existing entry: 'complete_contracts'"]),
                (self.folder, 'directory', 'DIRECTORY',
                 ["contracts/one.md:6: evidence reference: path spelling does not match an existing entry: 'directory'"]),
                (self.folder / 'directory', 'Proof.py', 'proof.py',
                 ["contracts/one.md:6: evidence reference: path spelling does not match an existing entry: 'Proof.py'"])]:
            with self.subTest(parent=parent.name, name=name):
                def listing(path):
                    names = real_listdir(path)
                    return [listed if entry == name else entry for entry in names] if path == parent else names
                with patch('wirth.validate.os.listdir', side_effect=listing):
                    self.assertCountEqual(validate(), expected)
        self.assertEqual(validate(), [])

import os
import shutil
import unittest

from wirth.validate import validate
from validator_support import ValidatorTestCase


class CurrentContractSetTests(ValidatorTestCase):
    def test_command_finds_contracts_in_the_project_contracts_folder(self):
        result = self.cli('validate')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        self.write('# Title\n', name='two.md')
        self.assert_cli_failure('at least one claim', label='contracts/two.md')

    def test_every_current_contract_is_checked(self):
        self.write(self.other_contract(), name='two.md')
        (self.folder / 'check.py').unlink()
        (self.root / 'tests/other_claim/check.py').unlink()
        errors = validate()
        self.assertCountEqual(errors, [
            f'contracts/{name}:6: evidence reference: path does not exist'
            for name in ['one.md', 'two.md']])

    @unittest.skipUnless(shutil.which('git'), 'requires git')
    def test_parent_contracts_are_not_discovered(self):
        result = self.run_command(['git', 'init', '--quiet'])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.write('This is not a contract.')
        child = self.root / 'child'
        child.mkdir()
        os.chdir(child)
        self.assertEqual(validate(), ['no contracts found in contracts/'])

    def test_root_readme_and_nested_contracts_are_not_discovered(self):
        (self.root / 'README.md').write_text('This is not a contract.')
        nested = self.root / 'child/contracts'
        nested.mkdir(parents=True)
        (nested / 'one.md').write_text('This is not a contract either.')
        self.assertEqual(validate(), [])

    def commit_baseline(self):
        for args in [('init', '--quiet'), ('add', '.'),
                     ('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
                      '-c', 'commit.gpgsign=false', 'commit', '--quiet', '-m', 'Baseline')]:
            result = self.run_command(['git', *args])
            self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_command(['git', 'status', '--porcelain'])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '')

    @unittest.skipUnless(shutil.which('git'), 'requires git')
    def test_uncommitted_edits_follow_current_content_in_both_directions(self):
        invalid = self.text.replace('A promise', '')
        error = ['contracts/one.md:3: claim must be nonblank']
        for baseline, edited, expected in [(self.text, invalid, error),
                                           (invalid, self.text, [])]:
            with self.subTest(baseline_valid=baseline == self.text):
                self.write(baseline)
                self.commit_baseline()
                self.write(edited)
                changed = self.run_command(['git', 'diff', '--name-only'])
                self.assertEqual(changed.returncode, 0, changed.stderr)
                self.assertEqual(changed.stdout, 'contracts/one.md\n')
                self.assertCountEqual(validate(), expected)

    @unittest.skipUnless(shutil.which('git'), 'requires git')
    def test_untracked_invalid_contract_is_checked(self):
        text = self.other_contract('')
        self.commit_baseline()
        self.write(text, name='two.md')
        status = self.run_command(['git', 'status', '--porcelain'])
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertEqual(status.stdout, '?? contracts/two.md\n')
        self.assertCountEqual(validate(), ['contracts/two.md:3: claim must be nonblank'])

    @unittest.skipUnless(shutil.which('git'), 'requires git')
    def test_deleting_last_committed_contract_reports_empty(self):
        self.commit_baseline()
        (self.root / 'contracts/one.md').unlink()
        self.assertCountEqual(validate(), ['no contracts found in contracts/'])

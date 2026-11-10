import os

from wirth.validate import validate
from validator_support import ISSUE, ISSUE_SHAPE, TESTS_SHAPE, ValidatorTestCase


class InputErrorTests(ValidatorTestCase):
    def test_evidence_name_delimiters_do_not_hide_independent_result_errors(self):
        names = [('report(1): final.py', 'report(1): final.py'),
                 ('tests/report(1): final.py', 'report(1): final.py'),
                 ('report(1): draft(2): final.py', 'report(1): draft(2): final.py'),
                 ('check.py', None)]
        results = [('', 'must be nonblank'),
                   ('A result (first): Next (last): Done', None),
                   ('`', 'must use nonempty, paired single-backtick code spans')]
        for name, invalid_segment in names:
            path = self.folder / name
            path.parent.mkdir(parents=True, exist_ok=True)
            # Windows forbids ':' in file names, so these evidence files cannot exist there:
            # https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file
            if os.name != 'nt' or ':' not in name:
                path.touch()
            for result, problem in results:
                with self.subTest(name=name, result=result):
                    self.write(self.text.replace('`check.py::', f'`{name}::')
                               .replace('An observation', result))
                    expected = []
                    if invalid_segment is not None:
                        expected.append('contracts/one.md:6: evidence reference: '
                                        f'invalid evidence-path segment {invalid_segment!r}')
                    if problem is not None:
                        expected.append(f'contracts/one.md:6: evidence result {problem}')
                    self.assertCountEqual(validate(), expected)

    def test_invalid_contract_filename_preserves_content_errors(self):
        for name in ['.hidden.md', 'bad--name.md', 'résumé.md']:
            with self.subTest(name=name):
                self.write('# Local contract\n\n' + self.claim('named_claim', '', ' `missing.py::test_observation`'),
                           name=name)
                self.write(self.other_contract(''), name='two.md')
                try:
                    self.assertCountEqual(validate(), [
                        f'contracts/{name}: invalid contract filename {name!r}',
                        f'contracts/{name}:3: claim must be nonblank',
                        f'contracts/{name}:6: evidence result must be nonblank',
                        f'contracts/{name}:6: evidence reference: path does not exist',
                        'contracts/two.md:3: claim must be nonblank'])
                finally:
                    (self.root / 'contracts' / name).unlink()
        (self.root / 'contracts/two.md').unlink()
        self.assertEqual(validate(), [])

    def test_invalid_evidence_name_preserves_result_error_without_missing_evidence(self):
        for name in ['', 'report(1).py']:
            with self.subTest(name=name):
                self.write_check(name)
                path = self.root / 'contracts/one.md'
                path.write_text(path.read_text().replace('An observation', ''))
                self.assertCountEqual(validate(), [
                    'contracts/one.md:6: evidence result must be nonblank',
                    f'contracts/one.md:6: evidence reference: invalid evidence-path segment {name!r}'])

    def test_missing_issue_does_not_hide_claim_or_its_errors(self):
        for claim, later_errors in [('A promise', []), ('', ['contracts/one.md:3: claim must be nonblank'])]:
            with self.subTest(claim=claim):
                self.write(self.text.replace(ISSUE, '').replace('A promise', claim))
                self.assertCountEqual(validate(), [
                    f'contracts/one.md:3: claim must be followed by {ISSUE_SHAPE}', *later_errors])

    def test_bad_title_does_not_hide_later_errors(self):
        self.write(self.text.replace('# Local contract', 'Bad title')
                   .replace('Issue: https://github.com/chalkbadger/wirth/issues/6', 'Issue: invalid')
                   .replace('A promise', '').replace('An observation', ''))
        self.assertCountEqual(validate(), [
            "contracts/one.md:1: expected '# <nonblank title>'",
            f'contracts/one.md:4: expected {ISSUE_SHAPE}',
            'contracts/one.md:3: claim must be nonblank',
            'contracts/one.md:6: evidence result must be nonblank'])

    def test_evidence_errors_retain_later_claim_errors(self):
        self.write(self.text.replace('check.py', 'missing.py').replace('An observation', '')
                   + self.claim('later', ''))
        self.assertCountEqual(validate(), [
            'contracts/one.md:6: evidence result must be nonblank',
            'contracts/one.md:6: evidence reference: path does not exist',
            'contracts/one.md:7: claim must be nonblank'])

    def test_errors_are_preserved_across_fields_and_contracts(self):
        self.write('# Title\n\n## [a] A promise\nIssue: invalid\n')
        self.write(self.text.replace('check.py', 'missing.py'), name='two.md')
        self.assertCountEqual(validate(), [
            f'contracts/one.md:4: expected {ISSUE_SHAPE}',
            f'contracts/one.md:3: claim must be followed by {TESTS_SHAPE}',
            'contracts/one.md:3: claim must have at least one evidence item',
            'contracts/two.md:6: evidence reference: path does not exist'])

    def test_invalid_utf8_names_contract(self):
        (self.root / 'contracts/one.md').write_bytes(b'\xff')
        errors = validate()
        self.assertEqual(len(errors), 1, errors)
        self.assertTrue(errors[0].startswith('contracts/one.md: cannot read Markdown:'), errors)
        self.assertIn('decode', errors[0])

    def test_unreadable_contract_names_file_and_other_contract_is_checked(self):
        self.write(self.other_contract(''), name='two.md')
        result = self.denied_cli(self.root / 'contracts/one.md')
        self.assert_cli_errors(result, [
            'contracts/one.md: cannot read Markdown: denied by fixture',
            'contracts/two.md:3: claim must be nonblank'])

    def test_no_contracts_missing_or_empty_directory(self):
        (self.root / 'contracts/one.md').unlink()
        self.assertCountEqual(validate(), ['no contracts found in contracts/'])
        (self.root / 'contracts').rmdir()
        self.assertCountEqual(validate(), ['no contracts found in contracts/'])

    def test_unreadable_contracts_directory_is_reported(self):
        result = self.denied_cli(self.root / 'contracts')
        self.assert_cli_errors(result, ['cannot discover contracts/: denied by fixture'])

    def test_denied_evidence_listing_retains_other_contract_error(self):
        self.evidence('checks/proof.py')
        self.write_check('checks/proof.py')
        self.write(self.other_contract(''), name='two.md')
        result = self.denied_cli(self.folder / 'checks', listing_only=True)
        self.assert_cli_errors(result, [
            'contracts/one.md:6: evidence reference: denied by fixture',
            'contracts/two.md:3: claim must be nonblank'])

    def test_entry_failures_retain_later_contract_errors(self):
        self.write(self.other_contract(''), name='two.md')
        (self.root / 'contracts/one.md').unlink()
        for name, diagnostic in [
                ('one.txt', 'unexpected entry; expected a direct *.md regular file'),
                ('one.md', 'must resolve to a regular file')]:
            with self.subTest(name=name):
                path = self.root / 'contracts' / name
                path.mkdir()
                try:
                    self.assertCountEqual(validate(), [
                        f'contracts/{name}: {diagnostic}',
                        'contracts/two.md:3: claim must be nonblank'])
                finally:
                    path.rmdir()

    def test_malformed_evidence_retains_later_claim_and_reference_errors(self):
        self.write(self.text + '- malformed evidence\n'
                   + self.claim('later', '', item='Later result `missing.py::test_observation`'))
        self.assertCountEqual(validate(), [
            "contracts/one.md:7: expected '- <result> `file::test_name`', ending with the test in a code span",
            'contracts/one.md:8: claim must be nonblank',
            'contracts/one.md:11: evidence reference: path does not exist'])

    def test_unreadable_evidence_file_names_its_line_and_other_contract_is_checked(self):
        self.write(self.other_contract(''), name='two.md')
        result = self.denied_cli(self.folder / 'check.py')
        self.assert_cli_errors(result, [
            'contracts/one.md:6: evidence reference: cannot read: denied by fixture',
            'contracts/two.md:3: claim must be nonblank'])

import sys

from wirth.validate import validate
from validator_support import ISSUE, ISSUE_SHAPE, ValidatorTestCase


def deny_network(event, args):
    if event.startswith('socket.'):
        raise AssertionError('network access is forbidden during validation tests')


sys.addaudithook(deny_network)

EVIDENCE = '- A result `check.py::test_observation`\n'
MISSING = '-  `missing.py::test_observation`\n'
A = 'Tests: [tests/a/](../tests/a/)\n'
B = 'Tests: [tests/b/](../tests/b/)\n'
FILE_ISSUE = ("Issue lines now go under each claim heading; expected '## [id] <claim>' "
              f"followed by '{ISSUE_SHAPE}'")


class RecoveryTests(ValidatorTestCase):
    def setUp(self):
        super().setUp()
        self.claim('a')
        self.claim('b')

    def assert_diagnostics(self, text, expected):
        self.write(text)
        self.assertCountEqual(validate(), ['contracts/one.md:' + error for error in expected])

    def test_missing_title_reports_only_title_at_first_claim(self):
        self.assert_diagnostics('\n## [a] A promise\n' + ISSUE + A + EVIDENCE,
                                ["2: expected '# <nonblank title>'"])

    def test_first_blank_claim_retains_its_own_error(self):
        self.assert_diagnostics(
            '## [a] \n' + ISSUE + A + EVIDENCE,
            ["1: expected '# <nonblank title>'", '1: claim must be nonblank'])

    def test_malformed_heading_has_no_missing_evidence_or_issue_cascade(self):
        for after in ['', ISSUE + A]:
            with self.subTest(after=after):
                self.assert_diagnostics('# Title\n\n## a bad\n' + after,
                                        ["3: expected '## [id] <nonblank claim>'"])

    def test_later_errors_survive_first_claim_recovery_and_blank_lines(self):
        for claim, own_error in [('A promise', []), ('', ['2: claim must be nonblank'])]:
            with self.subTest(claim=claim):
                self.assert_diagnostics(
                    f'\n## [a] {claim}\n' + ISSUE + A + EVIDENCE + '\n## [b] \n\n' + ISSUE + B + MISSING,
                    ["2: expected '# <nonblank title>'",
                     *own_error, '7: claim must be nonblank',
                     '11: evidence result must be nonblank',
                     '11: evidence reference: path does not exist'])

    def test_later_errors_survive_malformed_heading_and_blank_lines(self):
        self.assert_diagnostics(
            '\n# Title\n\n## a bad\n\n## [b] \n' + ISSUE + B + '\n' + MISSING,
            ["4: expected '## [id] <nonblank claim>'", '6: claim must be nonblank',
             '10: evidence result must be nonblank',
             '10: evidence reference: path does not exist'])

    def test_missing_evidence_is_retained_for_parsed_claims(self):
        for first in ['', '## a bad\n\n']:
            with self.subTest(first=first):
                self.assert_diagnostics(
                    '# Title\n\n' + first + '## [a] A promise\n' + ISSUE + A,
                    (["3: expected '## [id] <nonblank claim>'"] if first else []) +
                    [f'{5 if first else 3}: claim must have at least one evidence item'])

    def test_evidence_directly_after_malformed_heading_keeps_its_errors(self):
        self.assert_diagnostics(
            '# Title\n\n## a bad\n\n' + MISSING,
            ["3: expected '## [id] <nonblank claim>'", '5: evidence result must be nonblank'])

    def test_malformed_heading_keeps_earlier_errors(self):
        for text, expected in [
                ('## a bad\n' + EVIDENCE,
                 ["1: expected '# <nonblank title>'", "1: expected '## [id] <nonblank claim>'"]),
                ('# Title\n\n## [a] A promise\n' + ISSUE + A + '## a bad\n' + EVIDENCE,
                 ['3: claim must have at least one evidence item',
                  "6: expected '## [id] <nonblank claim>'"])]:
            with self.subTest(text=text):
                self.assert_diagnostics(text, expected)

    def test_file_level_issue_in_title_position_is_reported(self):
        self.assert_diagnostics(
            'Issue: invalid\n\n## [a] \n' + ISSUE + A + EVIDENCE,
            ["1: expected '# <nonblank title>'", f'1: {FILE_ISSUE}', '3: claim must be nonblank'])

    def test_nonfinal_claim_without_evidence_is_reported_after_missing_title(self):
        self.assert_diagnostics(
            '## [a] A promise\n' + ISSUE + A + '## [b] Another promise\n' + ISSUE + B + EVIDENCE,
            ["1: expected '# <nonblank title>'",
             '1: claim must have at least one evidence item'])

    def test_valid_contract_with_blank_lines_passes(self):
        self.assert_diagnostics(
            '\n# Title\n \t\n\n## [a] A promise\n\n' + ISSUE + '\n' + A + '\n' + EVIDENCE + '\n', [])

    def test_command_retains_later_errors_after_missing_title(self):
        self.write('\n \t\n## [a] A promise\n' + ISSUE + A + EVIDENCE + '\n## [b] \n\n' + ISSUE + B + MISSING)
        script = '''import sys
def deny_network(event, args):
    if event.startswith('socket.'):
        raise AssertionError('network access is forbidden during validation tests')
sys.addaudithook(deny_network)
from wirth.__main__ import main
sys.exit(main())
'''
        result = self.run_command([sys.executable, '-c', script, 'validate'])
        self.assert_cli_errors(result, [
            "contracts/one.md:3: expected '# <nonblank title>'",
            'contracts/one.md:8: claim must be nonblank',
            'contracts/one.md:12: evidence result must be nonblank',
            'contracts/one.md:12: evidence reference: path does not exist'])

    def test_missing_evidence_survives_each_opening_recovery(self):
        for opening, expected in [
                (ISSUE, ["1: expected '# <nonblank title>'", f'1: {FILE_ISSUE}',
                         '2: claim must have at least one evidence item']),
                ('', ["1: expected '# <nonblank title>'",
                      '1: claim must have at least one evidence item'])]:
            with self.subTest(opening=opening):
                self.assert_diagnostics(opening + '## [a] A promise\n' + ISSUE + A, expected)

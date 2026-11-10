from wirth.validate import validate
from validator_support import ISSUE_SHAPE, TESTS, TESTS_SHAPE, ValidatorTestCase


ITEM = '- An observation `check.py::test_observation`\n'


class CompleteContentTests(ValidatorTestCase):
    def test_multiple_claims_and_evidence(self):
        self.evidence('other.py', 'def test_other():\n    pass\n')
        self.write(self.text + '- Another observation `other.py::test_other`\n\n'
                   + self.claim('second-2'))
        self.assertEqual(validate(), [])

    def test_required_content(self):
        issue = 'Issue: https://github.com/chalkbadger/wirth/issues/6'
        cases = [('', ["1: expected '# <nonblank title>'", '1: contract must have at least one claim']),
                 (self.text.replace('# Local contract', '# '), ['1: title must be nonblank']),
                 (self.text.replace('# Local contract', '#Title'), ["1: expected '# <nonblank title>'"]),
                 (self.text.replace(issue, 'Issue: '), [f'4: expected {ISSUE_SHAPE}']),
                 (self.text.replace('Issue: ', 'Issue:'), [f'4: expected {ISSUE_SHAPE}']),
                 ('# Title\n', ['2: contract must have at least one claim']),
                 ('# Title', ['2: contract must have at least one claim']),
                 (self.text.replace('## [complete_contracts] A promise', '## A promise'),
                  ["3: expected '## [id] <nonblank claim>'"]),
                 (self.text.replace('A promise', ' '), ['3: claim must be nonblank']),
                 (self.text.replace(ITEM, ''), ['3: claim must have at least one evidence item']),
                 (self.text.replace('An observation', ' '), ['6: evidence result must be nonblank']),
                 (self.text.replace('`check.py::', '`::'),
                  ["6: evidence reference: invalid evidence-path segment ''"]),
                 (self.text.replace(TESTS, 'Tests: tests/complete_contracts/\n'),
                  [f"5: expected '{TESTS_SHAPE}'"])]
        for text, expected in cases:
            with self.subTest(text=text):
                self.write(text)
                self.assertCountEqual(validate(), ['contracts/one.md:' + error for error in expected])

    def test_empty_claim_before_another_claim_fails(self):
        self.write(self.text.replace(ITEM, '') + self.claim('second'))
        self.assertCountEqual(validate(), [
            'contracts/one.md:3: claim must have at least one evidence item'])

    def test_byte_written_line_endings_and_no_final_newline_pass(self):
        for ending in [b'\n', b'\r\n', b'\r', None]:
            with self.subTest(ending=ending):
                data = (self.text.rstrip('\n').encode() if ending is None else
                        self.text.encode().replace(b'\n', ending))
                (self.root / 'contracts/one.md').write_bytes(data)
                self.assertEqual(validate(), [])

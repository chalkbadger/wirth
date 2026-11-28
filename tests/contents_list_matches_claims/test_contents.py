from wirth.validate import validate
from validator_support import ValidatorTestCase


UNEXPECTED = 'unexpected content; expected a claim heading or evidence item'
ITEM_SHAPE = "expected '- <result> `file::test_name`', ending with the test in a code span"
# Anchors as GitHub renders the headings below; test_anchors.py cites the recorded render.
FIRST = '- [A promise](#complete_contracts-a-promise)'
MISMATCH = 'contents list does not match the claims; the list should be:'
SECOND = '- [I run `wirth validate`, and it passes.](#second-i-run-wirth-validate-and-it-passes)'


class ContentsListTests(ValidatorTestCase):
    def setUp(self):
        super().setUp()
        self.claims = self.text.split('\n', 2)[2] + '\n' + self.claim('second', 'I run `wirth validate`, and it passes.')

    def contract(self, *contents):
        return '# Local contract\n\n' + ''.join(line + '\n' for line in contents) + '\n' + self.claims

    def test_contract_without_a_list_passes(self):
        self.write('# Local contract\n\n' + self.claims)
        self.assertEqual(validate(), [])

    def test_matching_list_passes(self):
        self.write(self.contract(FIRST, SECOND))
        self.assertEqual(validate(), [])
        # Blank lines between list items keep one list.
        self.write(self.contract(FIRST, '', SECOND))
        self.assertEqual(validate(), [])

    def test_list_out_of_step_with_the_claims_fails_at_the_list(self):
        added = self.claim('third', 'A third promise')
        third = '- [A third promise](#third-a-third-promise)'
        reworded = '- [I start `wirth validate`, and it passes.](#second-i-start-wirth-validate-and-it-passes)'
        cases = [
            ('added', self.contract(FIRST, SECOND) + added, 4, [FIRST, SECOND, third]),
            ('removed', self.contract(FIRST, SECOND, third), 5, [FIRST, SECOND]),
            ('reworded', self.contract(FIRST, SECOND).replace('## [second] I run', '## [second] I start'),
             4, [FIRST, reworded]),
            ('reordered', self.contract(SECOND, FIRST), 3, [FIRST, SECOND]),
            ('link changed', self.contract(FIRST, SECOND.replace('#second-', '#second_')), 4, [FIRST, SECOND]),
        ]
        for case, text, line, expected in cases:
            with self.subTest(case=case):
                self.write(text)
                self.assertEqual(validate(), [
                    f'contracts/one.md:{line}: {MISMATCH}\n' + '\n'.join(expected)])
        self.write('# Local contract\n\n' + FIRST + '\n')
        self.assertCountEqual(validate(), [
            'contracts/one.md:3: contents list has no claims to list; remove it or add claims',
            'contracts/one.md:4: contract must have at least one claim'])

    def test_one_line_shows_every_line_the_list_needs(self):
        for first in [FIRST, '- [Something else](#elsewhere)']:
            with self.subTest(first=first):
                self.write(self.contract(first))
                result = self.cli('validate')
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, '')
                heading, *shown = result.stderr.splitlines()
                self.assertEqual(heading, f'contracts/one.md:3: {MISMATCH}')
                self.assertEqual(shown, [FIRST, SECOND])
                self.write(self.contract(*shown))
                result = self.cli('validate')
                self.assertEqual((result.returncode, result.stderr), (0, ''))
                self.assertIn('contract structure valid', result.stdout)

    def test_list_away_from_the_title_fails_as_today(self):
        cases = [
            ('after a note', '# Local contract\n\nA note\n' + FIRST + '\n\n' + self.claims,
             [f'3: {UNEXPECTED}', '4: evidence must follow a claim heading', f'4: {ITEM_SHAPE}']),
            ('after the claims', '# Local contract\n\n' + self.claims + FIRST + '\n',
             [f'12: {ITEM_SHAPE}']),
            ('without a title', FIRST + '\n\n' + self.claims,
             ["1: expected '# <nonblank title>'"]),
        ]
        for case, text, expected in cases:
            with self.subTest(case=case):
                self.write(text)
                self.assertCountEqual(validate(), ['contracts/one.md:' + error for error in expected])

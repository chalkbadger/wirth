from wirth.validate import validate
from validator_support import ISSUE, TESTS, ValidatorTestCase


UNEXPECTED = 'unexpected content; expected a claim heading or evidence item'
ITEM = '- An observation `check.py::test_observation`\n'
LOOSE = 'put this result under a group heading, because its claim has groups'


class EvidenceGroupTests(ValidatorTestCase):
    def grouped(self, body):
        return '# Local contract\n\n## [complete_contracts] A promise\n' + ISSUE + TESTS + body

    def test_grouped_and_ungrouped_claims_pass(self):
        self.write(self.grouped('\n### Saved approvals\n\n' + ITEM + ITEM + '\n### ChatGPT Apps\n\n' + ITEM)
                   + '\n' + self.claim('ungrouped'))
        self.assertEqual(validate(), [])
        # A single group is allowed, and the same name may group another claim.
        self.write(self.grouped('### Saved approvals\n' + ITEM)
                   + '\n' + self.claim('second', item='A result `check.py::test_observation`').replace(
                       '- A result', '### Saved approvals\n- A result'))
        self.assertEqual(validate(), [])

    def test_broken_groups_fail_at_their_line(self):
        cases = [
            ('item above the first group', ITEM + '### Topic\n' + ITEM, [f'6: {LOOSE}']),
            ('group without evidence', '### Topic\n' + ITEM + '### Empty\n### Other\n' + ITEM,
             ['8: group must have at least one evidence item']),
            ('last group without evidence', ITEM.join(['### Topic\n', '### Notes\n']),
             ['8: group must have at least one evidence item']),
            ('repeated name', '### Topic\n' + ITEM + '### Topic\n' + ITEM,
             ["8: duplicate group name 'Topic' in this claim"]),
            ('repeated name with other spacing', '### Topic\n' + ITEM + '###\tTopic \n' + ITEM,
             ["8: duplicate group name 'Topic' in this claim"]),
            ('repeated name with spaces between words', '### Saved approvals\n' + ITEM + '### Saved  approvals\n' + ITEM,
             ["8: duplicate group name 'Saved  approvals' in this claim"]),
            ('blank name', '### \n' + ITEM, ['6: group name must be nonblank']),
            ('non-ASCII name', '### Café\n' + ITEM,
             ['6: group name must contain only ASCII letters, digits, spaces, allowed punctuation '
              'or printable ASCII code spans']),
        ]
        for case, body, expected in cases:
            with self.subTest(case=case):
                self.write(self.grouped(body))
                self.assertCountEqual(validate(), ['contracts/one.md:' + error for error in expected])
        # Spaces inside a code span are significant, so these names differ.
        self.write(self.grouped('### Run `a b`\n' + ITEM + '### Run `a  b`\n' + ITEM))
        self.assertEqual(validate(), [])
        # An empty last group is reported when the next claim starts.
        self.write(self.grouped('### Topic\n' + ITEM + '### Empty\n') + '\n' + self.claim('second'))
        self.assertCountEqual(validate(), ['contracts/one.md:8: group must have at least one evidence item'])

    def test_group_heading_before_the_first_claim_fails_as_today(self):
        self.write(self.text.replace('## [', '### Topic\n## ['))
        self.assertCountEqual(validate(), [f'contracts/one.md:3: {UNEXPECTED}'])
        # Above the Issue and Tests lines, a group heading is not a group either.
        self.write(self.text.replace(ISSUE, '### Topic\n' + ISSUE))
        self.assertIn(f'contracts/one.md:4: {UNEXPECTED}', validate())

    def test_group_error_keeps_later_claim_errors(self):
        self.write(self.grouped(ITEM + '### Topic\n' + ITEM) + '\n'
                   + self.claim('later', text=' '))
        self.assertCountEqual(validate(), [f'contracts/one.md:6: {LOOSE}',
                                           'contracts/one.md:10: claim must be nonblank'])

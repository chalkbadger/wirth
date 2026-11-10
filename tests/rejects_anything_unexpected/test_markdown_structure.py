from wirth.validate import validate
from validator_support import ISSUE, TESTS, TESTS_SHAPE, ValidatorTestCase


UNEXPECTED = 'unexpected content; expected a claim heading or evidence item'
ITEM_SHAPE = "expected '- <result> `file::test_name`', ending with the test in a code span"


class MarkdownStructureTests(ValidatorTestCase):
    def test_tests_line_delimiters_are_required(self):
        for line in ['Tests: [tests/complete_contracts/(../tests/complete_contracts/)',
                     'Tests: [tests/complete_contracts/]../tests/complete_contracts/)',
                     'Tests: [tests/complete_contracts/](../tests/complete_contracts/',
                     'Tests: [tests/complete_contracts/] (../tests/complete_contracts/)',
                     'Tests: [tests/complete_contracts/](../tests/complete_contracts/) extra',
                     'Tests: tests/complete_contracts/', 'Tests:[tests/complete_contracts/](../tests/complete_contracts/)']:
            with self.subTest(line=line):
                self.write(self.text.replace(TESTS, line + '\n'))
                self.assertCountEqual(validate(), [f"contracts/one.md:5: expected '{TESTS_SHAPE}'"])
        self.write(self.text.replace('An observation', 'An observation (first): A result'))
        self.assertEqual(validate(), [])

    def test_unrecognized_content_is_not_silently_ignored(self):
        for extra, reason in [('Notes: something', UNEXPECTED), ('### Notes', UNEXPECTED),
                              ('# A second title', UNEXPECTED),
                              ('Issue: https://github.com/a/b/issues/2', UNEXPECTED),
                              (TESTS.rstrip('\n'), UNEXPECTED),
                              ('  indented prose', UNEXPECTED), ('```', UNEXPECTED),
                              ('- prose without a test name', ITEM_SHAPE),
                              ('- [check.py]: An observation', ITEM_SHAPE),
                              ('* An observation `check.py::test_observation`', UNEXPECTED)]:
            with self.subTest(extra=extra):
                self.write(self.text + extra + '\n')
                self.assertCountEqual(validate(), [f'contracts/one.md:7: {reason}'])

    def test_indented_headings_claim_lines_and_items_fail(self):
        for original, line in [('## [complete_contracts] A promise', 3), (ISSUE.rstrip('\n'), 4),
                               (TESTS.rstrip('\n'), 5),
                               ('- An observation `check.py::test_observation`', 6)]:
            for indentation in [' ', '    ', '\t']:
                with self.subTest(line=line, indentation=indentation):
                    self.write(self.text.replace(original, indentation + original))
                    self.assert_failure(UNEXPECTED, line=line)

    def test_only_spaces_and_tabs_are_blank_lines(self):
        self.write(self.text + ' \t \n')
        self.assertEqual(validate(), [])
        for whitespace in [' ', '\f', '　']:
            with self.subTest(whitespace=whitespace):
                self.write(self.text + whitespace + '\n')
                self.assertCountEqual(validate(), [f'contracts/one.md:7: {UNEXPECTED}'])

    def test_evidence_before_first_claim_fails(self):
        self.write(self.text.replace('## [complete_contracts] A promise\n' + ISSUE + TESTS, ''))
        self.assertCountEqual(validate(), [
            'contracts/one.md:3: evidence must follow a claim heading',
            'contracts/one.md:4: contract must have at least one claim'])

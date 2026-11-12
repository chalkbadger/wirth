from wirth.validate import validate
from validator_support import ISSUE, TESTS, ValidatorTestCase


ITEM = '- An observation `check.py::test_observation`\n'
ITEM_SHAPE = "expected '- <result> `file::test_name`', ending with the test in a code span"


class EvidenceItemTests(ValidatorTestCase):
    def test_items_name_a_file_in_the_tests_folder_and_a_test(self):
        self.evidence('nested/other.py', 'def test_first():\n    pass\n\ndef test_second():\n    pass\n')
        self.write(self.text + '- A `code` result `nested/other.py::test_second`\n\n'
                   '- Another result `nested/other.py::test_first`\n\n'
                   + self.claim('second', item='The same test name in its own folder `check.py::test_observation`'))
        self.assertEqual(validate(), [])

    def test_item_must_end_with_a_test_code_span(self):
        for item in ['- An observation', '- An observation check.py::test_observation',
                     '- An observation `check.py::test_observation` afterwards',
                     '- An observation`check.py::test_observation`', '- `check.py::test_observation`',
                     '- An observation `check.py::test_observation`.']:
            with self.subTest(item=item):
                self.write(self.text.replace(ITEM, item + '\n'))
                self.assertCountEqual(validate(), [f'contracts/one.md:6: {ITEM_SHAPE}'])

    def test_test_must_name_its_file_and_test(self):
        self.write(self.text.replace('`check.py::test_observation`', '`test_observation`'))
        self.assertCountEqual(validate(), [
            "contracts/one.md:6: test 'test_observation' must be written `file::test_name`, "
            "with the file relative to the claim's tests folder"])

    def test_test_name_without_its_class(self):
        self.write(self.text.replace('`check.py::test_observation`', '`check.py::CheckTests::test_observation`'))
        self.assertCountEqual(validate(), [
            "contracts/one.md:6: test 'check.py::CheckTests::test_observation' includes a class; "
            "write `file::test_name` without it"])

    def test_test_name_must_be_an_identifier(self):
        for name in ['test observation', 'test-observation', '1test', 'Tests.test_observation',
                     'test_observation()', '']:
            with self.subTest(name=name):
                self.write(self.text.replace('::test_observation`', f'::{name}`'))
                self.assertCountEqual(validate(), [
                    f'contracts/one.md:6: test name {name!r} must match `[A-Za-z_][A-Za-z0-9_]*`'])
        for name in ['_private', 'TestCase', 'test2']:
            with self.subTest(name=name):
                self.evidence('check.py', f'def {name}():\n    pass\n')
                self.write(self.text.replace('::test_observation`', f'::{name}`'))
                self.assertEqual(validate(), [])

    def test_one_test_may_prove_several_results(self):
        self.write(self.text + '- Another observation `check.py::test_observation`\n')
        self.assertEqual(validate(), [])

    def test_item_file_stays_inside_the_tests_folder(self):
        self.evidence('../outside.py')
        for path, segment in [('../outside.py', '..'), ('/outside.py', '')]:
            with self.subTest(path=path):
                self.write_check(path)
                self.assertCountEqual(validate(), [
                    f'contracts/one.md:6: evidence reference: invalid evidence-path segment {segment!r}'])

    def test_items_under_a_failed_tests_folder_report_only_its_error(self):
        self.write(self.text.replace(TESTS, 'Tests: [tests/missing/](../tests/missing/)\n')
                   + '- Another result `missing.py::test_missing`\n')
        self.assertCountEqual(validate(), ['contracts/one.md:5: tests folder: path does not exist'])
        # A later claim's broken Tests line must not fall back to the previous claim's folder.
        self.write(self.text + '## [second] Another promise\n' + ISSUE +
                   'Tests: [tests/second/](../tests/second/)\n- A result `check.py::test_missing`\n')
        self.assertCountEqual(validate(), ['contracts/one.md:9: tests folder: path does not exist'])
        self.write(self.text + '- Another result `missing.py::test_missing`\n')
        self.assertCountEqual(validate(), ['contracts/one.md:7: evidence reference: path does not exist'])


from wirth.validate import validate
from validator_support import ValidatorTestCase


class CheckReferenceTests(ValidatorTestCase):
    def test_references_require_existing_regular_files(self):
        (self.folder / 'directory').mkdir()
        for check, reason in [('missing', 'path does not exist'),
                              ('directory', 'must resolve to a regular file')]:
            with self.subTest(check=check):
                self.write_check(check)
                self.assertCountEqual(validate(), [f'contracts/one.md:6: evidence reference: {reason}'])

    def test_tests_folder_must_be_an_existing_directory(self):
        (self.root / 'tests/plain').touch()
        for label, reason in [('tests/missing/', 'path does not exist'),
                              ('tests/plain/', 'must resolve to a directory'),
                              ('tests/complete_contracts/check.py/', 'must resolve to a directory')]:
            with self.subTest(label=label):
                self.write_tests_link(label)
                self.assertCountEqual(validate(), [f'contracts/one.md:5: tests folder: {reason}'])

    def test_tests_folder_link_target_is_exactly_parent_then_displayed_path(self):
        label = 'tests/complete_contracts/'
        for link in ['../tests/other/', 'tests/complete_contracts/', '.././tests/complete_contracts/',
                     '../tests/complete_contracts', '../tests/complete_contracts/#part',
                     '../tests/%63omplete_contracts/', '/tests/complete_contracts/']:
            with self.subTest(link=link):
                self.write_tests_link(label, link)
                self.assertCountEqual(validate(), [
                    "contracts/one.md:5: tests folder: link target must be exactly '../' followed by the displayed path"])

    def test_tests_folder_path_ends_with_a_slash(self):
        self.write_tests_link('tests/complete_contracts')
        self.assertCountEqual(validate(), [
            "contracts/one.md:5: tests folder: tests folder path must end with '/'"])

    def test_tests_folder_is_named_after_the_claim_id(self):
        (self.root / 'checks/complete_contracts').mkdir(parents=True)
        (self.root / 'checks/complete_contracts/check.py').write_text('def test_observation():\n')
        self.write_tests_link('checks/complete_contracts/')
        self.assertEqual(validate(), [])
        for other in ['other', 'xcomplete_contracts', 'complete_contracts_x']:
            with self.subTest(folder=other):
                (self.root / 'tests' / other).mkdir()
                self.write_tests_link(f'tests/{other}/')
                self.assertCountEqual(validate(), [
                    f"contracts/one.md:5: tests folder: folder '{other}' must be named after the claim ID 'complete_contracts'"])

    def test_tests_folder_path_follows_the_naming_rule(self):
        for parent in ['.ci', 'my tests', 'a..b']:
            with self.subTest(parent=parent):
                (self.root / parent / 'complete_contracts').mkdir(parents=True)
                self.write_tests_link(f'{parent}/complete_contracts/')
                self.assertCountEqual(validate(), [
                    f"contracts/one.md:5: tests folder: invalid evidence-path segment {parent!r}"])

    def test_nested_regular_evidence_file_passes(self):
        self.evidence('checks/nested/proof.py')
        self.write_check('checks/nested/proof.py')
        self.assertEqual(validate(), [])

    def test_regular_file_cannot_be_a_directory_component(self):
        self.write_check('check.py/child.py')
        self.assertCountEqual(validate(), [
            'contracts/one.md:6: evidence reference: path requires a directory component'])

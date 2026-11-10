from wirth.validate import validate
from validator_support import ValidatorTestCase


class TestNameTests(ValidatorTestCase):
    def test_python_test_needs_a_def_at_any_indentation(self):
        for content in ['def test_observation():\n',
                        'class Tests:\n    def test_observation(self):\n        pass\n',
                        'class Tests:\n\tdef test_observation(self):\n',
                        'import x\r\ndef test_observation():\r\n',
                        'async def test_observation():\n']:
            with self.subTest(content=content):
                self.evidence('check.py', content)
                self.assertEqual(validate(), [])

    def test_python_test_without_its_def_fails(self):
        for content in ['', 'test_observation()\n', '# def test_observation():\n',
                        'test_observation = make_test()\n', 'def test_observation_extra():\n',
                        'def my_test_observation():\n', 'x = "def test_observation()"\n',
                        'def test_observation\n', 'class test_observation:\n']:
            with self.subTest(content=content):
                self.evidence('check.py', content)
                self.assertCountEqual(validate(), [
                    "contracts/one.md:6: test 'test_observation' is not defined in tests/complete_contracts/check.py"])

    def test_other_files_need_the_name_as_a_whole_word(self):
        self.write_check('checks/delivery.test.ts')
        for content, defined in [('it("sends", test_observation);\n', True),
                                 ('test_observation\n', True), ('(test_observation)', True),
                                 ('', False), ('test_observations()\n', False),
                                 ('my_test_observation\n', False), ('test_observation1\n', False),
                                 ('Test_Observation\n', False)]:
            with self.subTest(content=content):
                self.evidence('checks/delivery.test.ts', content)
                self.assertCountEqual(validate(), [] if defined else [
                    "contracts/one.md:6: test 'test_observation' is not defined in tests/complete_contracts/checks/delivery.test.ts"])

    def test_each_item_is_checked_against_its_own_file(self):
        self.evidence('other.py', 'def test_other():\n    pass\n')
        self.write(self.text + '- Second `check.py::test_other`\n'
                   '- Third `other.py::test_other`\n- Fourth `other.py::test_observation`\n')
        self.assertCountEqual(validate(), [
            "contracts/one.md:7: test 'test_other' is not defined in tests/complete_contracts/check.py",
            "contracts/one.md:9: test 'test_observation' is not defined in tests/complete_contracts/other.py"])

    def test_renamed_test_is_named_with_its_line(self):
        self.evidence('check.py', 'def test_renamed_observation():\n    pass\n')
        result = self.cli('validate')
        self.assert_cli_errors(result, [
            "contracts/one.md:6: test 'test_observation' is not defined in tests/complete_contracts/check.py"])

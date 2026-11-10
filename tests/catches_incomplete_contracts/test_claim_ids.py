from wirth.validate import validate
from validator_support import ISSUE, ValidatorTestCase


class ClaimIdTests(ValidatorTestCase):
    def test_same_id_in_different_contracts_fails(self):
        self.write(self.text, name='two.md')
        self.assertCountEqual(validate(), [
            "contracts/two.md:3: duplicate claim ID 'complete_contracts', first used at contracts/one.md:3"])

    def test_duplicate_ids_fail_even_when_separated_by_another_claim(self):
        for middle in ['', self.claim('second')]:
            with self.subTest(middle=middle):
                self.write(self.text + middle + self.claim('complete_contracts', 'A different promise'))
                line = 7 if not middle else 11
                self.assertCountEqual(validate(), [
                    f"contracts/one.md:{line}: duplicate claim ID 'complete_contracts'"])

    def test_missing_invalid_and_uppercase_claim_ids_fail(self):
        message = ("claim ID must start with a lowercase ASCII letter or digit and contain only "
                   "lowercase letters, digits, '_' or '-'")
        for identifier in ['', 'with space', '-starts-with-dash', 'a.b', 'é']:
            with self.subTest(identifier=identifier):
                self.write(self.text.replace('[complete_contracts]', f'[{identifier}]'))
                self.assertCountEqual(validate(), [f'contracts/one.md:3: {message}'])
        self.write(self.text + self.claim('x', 'Lowercase promise') + '## [X] Uppercase promise\n' + ISSUE +
                   'Tests: [tests/x/](../tests/x/)\n- Result `check.py::test_observation`\n')
        self.assertCountEqual(validate(), [f'contracts/one.md:11: {message}'])

    def test_digit_initial_claim_id_passes(self):
        self.write('# Title\n\n' + self.claim('2nd_claim'))
        self.assertEqual(validate(), [])

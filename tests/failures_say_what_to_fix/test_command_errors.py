from validator_support import ValidatorTestCase


class CommandErrorTests(ValidatorTestCase):
    def test_invalid_content_reports_lines_without_success(self):
        self.write(self.text.replace('A promise', '').replace('An observation', ''))
        result = self.cli('validate')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
        self.assertCountEqual(result.stderr.splitlines(), [
            'contracts/one.md:3: claim must be nonblank',
            'contracts/one.md:6: evidence result must be nonblank'])

    def test_only_validate_command(self):
        for args in [(), ('check',), ('validate', '--validate-only')]:
            with self.subTest(args=args):
                result = self.cli(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, '')
                self.assertIn('usage:', result.stderr)

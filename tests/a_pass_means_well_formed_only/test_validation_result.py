from wirth.validate import validate
from validator_support import ValidatorTestCase


class StructureOnlyTests(ValidatorTestCase):
    def test_valid_cli_is_structure_only_and_does_not_execute(self):
        marker = self.root / 'executed'
        self.evidence('test_execution.py', f'from pathlib import Path\nPath({str(marker)!r}).touch()\n'
                      'raise RuntimeError("must never execute")\n'
                      'def test_observation():\n    pass\n')
        self.write_check('test_execution.py')
        self.assertFalse((self.root / 'wirth.json').exists())
        self.assertFalse((self.root / '.git').exists())
        result = self.cli('validate')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout,
                         'contract structure valid; checks were not run and evidence adequacy was not assessed\n')
        self.assertEqual(result.stderr, '')
        self.assertFalse(marker.exists(), 'the absolute marker detects execution from any working directory')

    def test_referenced_file_need_not_be_a_check_or_readable_text(self):
        for content in [b'\xffnot a test test_observation\xff', b'test_observation']:
            with self.subTest(content=content):
                (self.folder / 'facts.bin').write_bytes(content)
                self.write_check('facts.bin')
                self.assertEqual(validate(), [])

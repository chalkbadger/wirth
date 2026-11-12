from wirth.validate import validate
from validator_support import ValidatorTestCase


class ContractInputTests(ValidatorTestCase):
    def test_invalid_contract_name_on_a_directory_fails(self):
        path = self.root / 'contracts/.hidden.md'
        path.mkdir()
        self.assertCountEqual(validate(), [
            "contracts/.hidden.md: invalid contract filename '.hidden.md'",
            'contracts/.hidden.md: must resolve to a regular file'])

    def test_contract_files_must_not_be_directories(self):
        path = self.root / 'contracts/one.md'
        path.unlink()
        path.mkdir()
        self.assertCountEqual(validate(), ['contracts/one.md: must resolve to a regular file'])

    def test_unexpected_entries_are_reported(self):
        for name in ['new.MD', 'new.md.bak', 'old.json', 'notes', '.hidden']:
            path = self.root / 'contracts' / name
            path.write_text('{}')
            with self.subTest(name=name):
                self.assertCountEqual(validate(), [
                    f'contracts/{name}: unexpected entry; expected a direct *.md regular file'])
            path.unlink()
        nested = self.root / 'contracts/nested'
        nested.mkdir()
        (nested / 'x.md').write_text('{}')
        self.assertCountEqual(validate(), [
            'contracts/nested: unexpected entry; expected a direct *.md regular file'])

    def test_discovery_directory_that_is_a_file_fails(self):
        directory = self.root / 'contracts'
        directory.rename(self.root / 'inputs')
        directory.write_text('not a directory')
        self.assertEqual(validate(), ['cannot discover contracts/: must resolve to a directory'])

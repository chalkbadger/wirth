from itertools import product
import os

from wirth.validate import validate
from validator_support import ValidatorTestCase

# Windows forbids '\\' (a path separator) and characters 1 through 31 in file names:
# https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file
WINDOWS_FORBIDDEN_NAMES = {'check\\name.md', 'name\n.md'}


class NameTests(ValidatorTestCase):
    def test_evidence_segments_accept_ascii_alphanumerics_and_single_internal_separators(self):
        for name in ['A', 'z', '0', 'Z9', 'a.b', 'a-b', 'a_b',
                     'a.b-c_d/e.py', 'A1_b2-C3.d4/E5.py']:
            with self.subTest(name=name):
                self.evidence(name)
                self.write_check(name)
                self.assertCountEqual(validate(), [])

    def test_contract_filenames_accept_ascii_alphanumerics_and_single_internal_separators(self):
        for name in ['A.md', 'z.md', '0.md', 'A1.b2-c3_d4.md', 'delivery-checks.md']:
            with self.subTest(name=name):
                self.write(name=name)
                self.assertCountEqual(validate(), [])
                (self.root / 'contracts' / name).unlink()

    def test_evidence_rejects_invalid_segments_and_names_each_segment(self):
        names = ['.hidden', '-leading', '_leading', 'trailing.', 'trailing-', 'trailing_',
                 'check name.py', 'check+name.py', 'chéck.py',
                 'report(1).py', 'tests/report(1).py', 'report].py', 'tests/report[1].py',
                 'check%20name.py', 'check\\name.py', 'check\0name.py',
                 '_check_.py', '__check__.py', 'tests/_claim_/test_name.py',
                 'module/.git', '.git/config', 'sub/.git/config', '.GIT/config',
                 '.Git/config', 'x/.GIT/y', '.git./x', '.github/workflows/ci.yml',
                 '.gitignore']
        names += ['x' + a + b + 'y' for a, b in product('._-', repeat=2)]
        for name in names:
            with self.subTest(name=name):
                invalid = next(part for part in name.split('/') if part not in
                               ['tests', 'test_name.py', 'module', 'config', 'sub', 'x',
                                'y', 'workflows', 'ci.yml'])
                if '\0' not in name:
                    path = self.folder / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.touch()
                self.write_check(name)
                try:
                    self.assertCountEqual(validate(), [
                        f'contracts/one.md:6: evidence reference: invalid evidence-path segment {invalid!r}'])
                finally:
                    if '\0' not in name:
                        path.unlink()

    def test_evidence_rejects_empty_and_dot_segments(self):
        self.evidence('directory/check.py')
        # Contracts separate segments with '/' on every OS, so write the absolute path that way.
        absolute = '/' + (self.folder / 'check.py').relative_to(self.root.anchor).as_posix()
        for name, segment in [('', ''), ('./check.py', '.'), ('directory/../check.py', '..'),
                              ('check.py/', ''), ('check.py/.', '.'),
                              ('directory//check.py', ''), (absolute, '')]:
            with self.subTest(name=name):
                self.write_check(name)
                self.assertCountEqual(validate(), [
                    f'contracts/one.md:6: evidence reference: invalid evidence-path segment {segment!r}'])

    def test_contract_filenames_reject_invalid_names_and_identify_them(self):
        names = ['.md', '.x.md', '-leading.md', '_leading.md', 'chéck.md',
                 'check name.md', 'check+name.md', 'check\\name.md', 'name\n.md']
        names += ['x' + a + b + 'y.md' for a, b in product('._-', repeat=2)]
        for name in names:
            with self.subTest(name=name):
                if os.name == 'nt' and name in WINDOWS_FORBIDDEN_NAMES:
                    # No such contract can exist on Windows; show that rather than assume it.
                    with self.assertRaises(OSError):
                        self.write(name=name)
                    continue
                self.write(name=name)
                try:
                    self.assertCountEqual(validate(), [
                        f'contracts/{name}: invalid contract filename {name!r}'])
                finally:
                    (self.root / 'contracts' / name).unlink()

    def test_invalid_name_has_command_failure_without_false_success(self):
        self.evidence('.gitignore')
        self.write_check('.gitignore')
        result = self.cli('validate')
        self.assert_cli_errors(result, [
            "contracts/one.md:6: evidence reference: invalid evidence-path segment '.gitignore'"])

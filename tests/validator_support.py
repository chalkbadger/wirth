import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from wirth.validate import validate


PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
DEFINITION = 'def test_observation():\n    pass\n'
ISSUE = 'Issue: https://github.com/chalkbadger/wirth/issues/6\n'
ISSUE_SHAPE = 'Issue: https://github.com/<owner>/<repo>/issues/<positive integer>'
TESTS = 'Tests: [tests/complete_contracts/](../tests/complete_contracts/)\n'
TESTS_SHAPE = 'Tests: [tests/<claim_id>/](../tests/<claim_id>/)'


class ValidatorTestCase(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.addCleanup(os.chdir, Path.cwd())
        os.chdir(self.root)
        (self.root / 'contracts').mkdir()
        self.others = []
        self.folder = self.root / 'tests/complete_contracts'
        self.evidence('check.py')
        self.text = ('# Local contract\n\n'
                     '## [complete_contracts] A promise\n' + ISSUE + TESTS +
                     '- An observation `check.py::test_observation`\n')
        self.write()

    def evidence(self, name, content=DEFINITION):
        path = self.folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def write(self, text=None, name='one.md'):
        if text is None:
            # Claim IDs are unique across contract files, so other files get their own claim.
            text = self.text if name == 'one.md' else '# Local contract\n\n' + self.claim(f'claim_{len(self.others)}')
            if name != 'one.md':
                self.others.append(name)
        # The validator reads UTF-8; Python 3.11 on Windows would otherwise write the locale encoding.
        (self.root / 'contracts' / name).write_text(text, encoding='utf-8')

    def claim(self, identifier, text='Another promise', item='A result `check.py::test_observation`'):
        folder = self.root / 'tests' / identifier
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'check.py').write_text(DEFINITION)
        return (f'## [{identifier}] {text}\n{ISSUE}Tests: [tests/{identifier}/](../tests/{identifier}/)\n'
                f'- {item}\n')

    def other_contract(self, text='Another promise'):
        # A second contract file needs its own claim ID, because IDs are unique across files.
        return '# Local contract\n\n' + self.claim('other_claim', text)

    def write_check(self, check):
        self.write(self.text.replace('`check.py::', f'`{check}::'))

    def write_tests_link(self, label, link=None):
        link = '../' + label if link is None else link
        self.write(self.text.replace(TESTS, f'Tests: [{label}]({link})\n'))

    def cli(self, *args):
        return self.run_command([sys.executable, '-m', 'wirth', *args])

    def denied_cli(self, target, listing_only=False):
        # Keep the audit hook in a subprocess so it cannot affect other tests.
        # https://docs.python.org/3.12/library/audit_events.html
        script = '''import os
import sys
target = os.path.realpath(sys.argv.pop(1))
events = sys.argv.pop(1).split(',')
def deny(event, args):
    if event in events and isinstance(args[0], (str, bytes, os.PathLike)):
        if os.path.realpath(os.fsdecode(args[0])) == target:
            raise PermissionError('denied by fixture')
sys.addaudithook(deny)
from wirth.__main__ import main
sys.exit(main())
'''
        events = 'os.listdir,os.scandir' if listing_only else 'open,os.listdir,os.scandir'
        return self.run_command([sys.executable, '-c', script, str(target), events, 'validate'])

    def run_command(self, command):
        return subprocess.run(command, cwd=self.root,
                              env={'PATH': os.environ.get('PATH', ''), 'PYTHONPATH': PROJECT_ROOT,
                                   'PYTHONDONTWRITEBYTECODE': '1',
                                   'GIT_CEILING_DIRECTORIES': str(self.root.parent)},
                              text=True, capture_output=True, timeout=5)

    def assert_failure(self, reason, label='contracts/one.md', line=None):
        errors = validate()
        location = f'{label}:' if line is None else f'{label}:{line}:'
        self.assertTrue(any(error.startswith(location) and reason in error for error in errors), errors)

    def assert_cli_errors(self, result, expected_lines):
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, '')
        self.assertCountEqual(result.stderr.splitlines(), expected_lines)

    def assert_cli_failure(self, reason, label='contracts/one.md'):
        result = self.cli('validate')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(label, result.stderr)
        self.assertIn(reason, result.stderr)
        self.assertNotIn('contract structure valid', result.stdout)

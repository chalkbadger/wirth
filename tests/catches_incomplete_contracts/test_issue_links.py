from wirth.validate import validate
from validator_support import ISSUE, ISSUE_SHAPE, TESTS, TESTS_SHAPE, ValidatorTestCase


class IssueLinkTests(ValidatorTestCase):
    def test_issue_url_format(self):
        for url in ['http://github.com/a/b/issues/1', 'https://example.com/a/b/issues/1',
                    'https://githubxcom/a/b/issues/1',
                    'https://github.com/a/b/pull/1', 'https://github.com/a/b/issues/0',
                    'https://github.com/a/b/issues/-1', 'https://github.com/a/b/issues/1?x=y',
                    'https://github.com/a/b/issues/1#x', 'https://github.com/a/b/issues/1/',
                    'https://github.com//b/issues/1', 'https://github.com/./b/issues/1',
                    'https://github.com/../b/issues/1', 'https://github.com/a/./issues/1',
                    'https://github.com/a/../issues/1']:
            with self.subTest(url=url):
                self.write(self.text.replace('https://github.com/chalkbadger/wirth/issues/6', url))
                self.assertCountEqual(validate(), [
                    'contracts/one.md:4: expected Issue: https://github.com/<owner>/<repo>/issues/<positive integer>'])

    def test_mixed_case_dotted_repository_and_multiple_digits_pass(self):
        self.write(self.text.replace('https://github.com/chalkbadger/wirth/issues/6',
                                    'https://github.com/MixedOwner/Mixed.Repo/issues/123'))
        self.assertEqual(validate(), [])

    def test_each_claim_cites_its_own_issue(self):
        self.write(self.text + '\n' + self.claim('second').replace(
            ISSUE, '\nIssue: https://github.com/other/repo/issues/42\n\n'))
        self.assertEqual(validate(), [])

    def test_issue_then_tests_lines_directly_follow_each_claim_heading(self):
        missing_issue = f'claim must be followed by {ISSUE_SHAPE}'
        missing_tests = f'claim must be followed by {TESTS_SHAPE}'
        unexpected = 'unexpected content; expected a claim heading or evidence item'
        for text, expected in [
                (self.text.replace(ISSUE, ''), [f'3: {missing_issue}']),
                (self.text.replace(TESTS, ''), [f'3: {missing_tests}']),
                (self.text.replace(ISSUE + TESTS, TESTS + ISSUE), [f'3: {missing_issue}', f'5: {unexpected}']),
                ('# Title\n\n## [a] A promise\n', [f'3: {missing_issue}', f'3: {missing_tests}',
                                                   '3: claim must have at least one evidence item']),
                (self.text + '## [second] Another promise\n- A result `check.py::test_observation`\n',
                 [f'7: {missing_issue}', f'7: {missing_tests}']),
                (self.text.replace(ISSUE, '') + ISSUE, [f'3: {missing_issue}', f'6: {unexpected}'])]:
            with self.subTest(text=text):
                self.write(text)
                self.assertCountEqual(validate(), ['contracts/one.md:' + error for error in expected])

    def test_file_level_issue_line_shows_the_new_shape(self):
        self.write(self.text.replace('# Local contract\n', '# Local contract\n' + ISSUE))
        self.assertCountEqual(validate(), [
            "contracts/one.md:2: Issue lines now go under each claim heading; expected '## [id] <claim>' "
            f"followed by '{ISSUE_SHAPE}'"])

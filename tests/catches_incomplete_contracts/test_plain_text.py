from wirth.validate import validate
from validator_support import ValidatorTestCase


TEXT_MESSAGE = 'must contain only ASCII letters, digits, spaces, allowed punctuation or printable ASCII code spans'


class PlainTextTests(ValidatorTestCase):
    def test_ascii_words_punctuation_and_code_spans_pass(self):
        for text in ['Delivery at 12:30:59', 'A, 2; (yes)! "Fine" - isn\'t it?',
                     'The `[link](url) &amp; @name $x^2$ :a: WWW.example.com` text is literal.',
                     '`code_only`', '42', 'A ` ` span', 'A `~` span']:
            self.write(self.text.replace('Local contract', text).replace('A promise', text)
                       .replace('An observation', text))
            self.assertEqual(validate(), [], text)

    def test_title_claim_and_result_follow_the_ascii_rule(self):
        cases = [(text, TEXT_MESSAGE) for text in
                 ['Café', 'Cafe\u0301', 'नमस्ते', 'Digits ١٢٣', 'snake_case',
                  'A \u200b', 'A \x00', 'A `<é>`', 'A `\t`', 'A `\x7f`',
                  '[text](url)', '<b>text</b>', '$`\\phantom{x}`$', 'A ###']]
        cases += [(text, 'must contain at least one ASCII letter or digit') for text in ['...', '`!?`']]
        cases += [(text, 'must not contain www. outside code spans') for text in ['www.example.com', 'AWWW.example.com']]
        cases += [(text, 'must use nonempty, paired single-backtick code spans') for text in ['`unclosed', 'A ``', '``nested``']]
        for text, message in cases:
            for original, field, line in [('Local contract', 'title', 1), ('A promise', 'claim', 3),
                                          ('An observation', 'evidence result', 6)]:
                with self.subTest(text=text, field=field):
                    self.write(self.text.replace(original, text))
                    self.assertCountEqual(validate(), [f'contracts/one.md:{line}: {field} {message}'])

    def test_bare_claim_heading_reports_blank_text_cleanly(self):
        self.write(self.text.replace('## [complete_contracts] A promise', '## [complete_contracts]'))
        self.assertCountEqual(validate(), ['contracts/one.md:3: claim must be nonblank'])

import re

from wirth.validate import validate
from validator_support import ValidatorTestCase


# Each heading with the anchor GitHub gave it, in file order, as rendered at
# https://github.com/chalkbadger/wirth/blob/6cf9159d751c0d4ec4a2d3ef32598073ab51fc58/probe/anchors.md
# and, for padded code spans, at
# https://github.com/chalkbadger/wirth/blob/984fe036d80987fbdef6dcc0be4aabcf580ef6c8/probe/anchors.md
RENDERED = [
    ('# Probe', 'probe'),
    ('## [dup] Same text', 'dup-same-text'),
    ('## [dup] Same text', 'dup-same-text-1'),
    ('## [dup] Same text', 'dup-same-text-2'),
    ('## [dup] Same text 1', 'dup-same-text-1-1'),
    ('## [natural] Clash 1', 'natural-clash-1'),
    ('## [natural] Clash', 'natural-clash'),
    ('## [natural] Clash', 'natural-clash-2'),
    ('## [a] b c', 'a-b-c'),
    ('## [a-b] c', 'a-b-c-1'),
    ('## [quote] It\'s "quoted": a, b; c? d! (e) - f.', 'quote-its-quoted-a-b-c-d-e---f'),
    ('## [code] I run `wirth validate` and `a::b_c` and `x/y.z` and `[q](r)`',
     'code-i-run-wirth-validate-and-ab_c-and-xyz-and-qr'),
    ('## [space] two  spaces\ttab', 'space-two--spacestab'),
    ('## [Digits9] 123 Num', 'digits9-123-num'),
    ('## [pad] I run ` x ` now', 'pad-i-run-x-now'),
    ('## [pad2] I run `  y  ` and ` z` and `   `', 'pad2-i-run--y--and--z-and----'),
    ('## [mixed] Ab `C D` e', 'mixed-ab-c-d-e'),
    ('### Group heading', 'group-heading'),
    ('### Group heading', 'group-heading-1'),
    ('## Probe', 'probe-1'),
    ('# Probe', 'probe-2'),
]


class AnchorTests(ValidatorTestCase):
    def test_links_match_the_anchors_github_renders(self):
        title, *headings = [heading for heading, _ in RENDERED]
        self.write(title + '\n\n- [A claim](#a-claim)\n\n' + '\n\n'.join(headings) + '\n')
        expected = [f'- [{heading.split("] ", 1)[1]}](#{anchor})'
                    for heading, anchor in RENDERED if re.match(r'## \[', heading)]
        contents = [error for error in validate() if 'contents list' in error]
        self.assertEqual(len(contents), 1, validate())
        self.assertEqual(contents[0].split('\n')[1:], expected)

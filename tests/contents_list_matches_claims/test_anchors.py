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

# A title that takes a later claim's anchor, as rendered at
# https://github.com/chalkbadger/wirth/blob/9e2f2630998da0a010ecc5425385dab47003b408/probe/title.md
TITLE_COLLISION = [('# Receipt saved', 'receipt-saved'), ('## [receipt] Saved', 'receipt-saved-1')]
# A group that takes a later claim's anchor, as rendered at
# https://github.com/chalkbadger/wirth/blob/9e2f2630998da0a010ecc5425385dab47003b408/probe/group.md
GROUP_COLLISION = [('# Probe', 'probe'), ('## [first] A claim', 'first-a-claim'),
                   ('### Receipt saved', 'receipt-saved'), ('## [receipt] Saved', 'receipt-saved-1')]


def expected_list(rendered):
    return [f'- [{heading.split("] ", 1)[1]}](#{anchor})'
            for heading, anchor in rendered if re.match(r'## \[', heading)]


class AnchorTests(ValidatorTestCase):
    def contents_shown(self, rendered):
        title, *headings = [heading for heading, _ in rendered]
        self.write(title + '\n\n- [A claim](#a-claim)\n\n' + '\n\n'.join(headings) + '\n')
        contents = [error for error in validate() if 'contents list' in error]
        self.assertEqual(len(contents), 1, validate())
        return contents[0].split('\n')[1:]

    def test_links_match_the_anchors_github_renders(self):
        for name, rendered in [('probe', RENDERED), ('title collision', TITLE_COLLISION),
                               ('group collision', GROUP_COLLISION)]:
            with self.subTest(fixture=name):
                self.assertEqual(self.contents_shown(rendered), expected_list(rendered))

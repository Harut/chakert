# -*- coding: utf-8 -*-

from .base import BaseTests


class EnTests(BaseTests):

    lang = 'en'

    # XXX cleanup tests

    def test_months(self):
        self.assertText(
            u'It was very rainy at March 20, at Apr. 1 was marmelade snow,'
                u' and today is Apr 29 and it is sunny. What a different 3 days!',
            u'It was very rainy at␣March␣20, at␣Apr.␣1 was marmelade snow,'
                u' and␣today is Apr␣29 and␣it is sunny. What a␣different 3 days!')

    def test_nested_quotes(self):
        self.assertText(
            u'He said, "She yelled, "I\'m going to kill you!""',
            u'He said, ”She yelled, ‘I\'m going to␣kill you!’“')

    def test_unclosed_quotes(self):
        self.assertText(
            u'He said, "She yelled, "I\'m going to kill you!"',
            u'He said, ”She yelled, ‘I\'m going to␣kill you!’')

    def test_quote_start(self):
        self.assertText(
            u'"She yelled"',
            u'”She yelled“')

    def test_quote_in_braces(self):
        self.assertText(
            u'No ("She yelled")',
            u'No (”She yelled“)')

    def test_en_dash(self):
        self.assertText(
            u'Ages 5 - 8. Ages 5-8.',
            u'Ages 5␣– 8. Ages 5–8.')

    def test_em_dash(self):
        self.assertText(
            u'An em-dash is used to indicate a break in thought - as illustrated here',
            u'An␣em-dash is used to␣indicate a␣break in␣thought␣— as␣illustrated here')

    def test_dash_at_end(self):
        # no replacement
        self.assertText(u'Yes -', u'Yes -')

    def test_ellipse(self):
        self.assertText(
            u'A long time ago in a galaxy far away...',
            u'A␣long time ago in␣a␣galaxy far away…')

    def test_ellipse_combined(self):
        self.assertText(
            u'Yes.... No...! May be...? Anyway..., it\'s fine!',
            u'Yes…. No…! May be…? Anyway…, it\'s fine!')

    def test_double_hyphen(self):
        self.assertText(
            u'Double -- hyphen.',
            u'Double␣\N{EM DASH} hyphen.')
        self.assertText(
            u'Double---hyphen.',
            u'Double\N{EM DASH}hyphen.')

        # Check if all hyphen rules are applied on double hyphen
        self.assertText(
            u'--3 °C outdoor',
            u'\N{MINUS SIGN}3 °C outdoor') # XXX nbsp before degree sign?

    def test_minus(self):
        self.assertText(
            u'There is -3 °C outdoor',
            u'There is \N{MINUS SIGN}3 °C outdoor') # XXX nbsp before degree sign?

        self.assertText(
            u'-3 °C outdoor',
            u'\N{MINUS SIGN}3 °C outdoor') # XXX nbsp before degree sign?

    def test_dialog(self):
        self.assertText(
            u'- Hello!',
            u'- Hello!')


    def test_ignored_default(self):
        self.assertHtml(
            u'The code <code>function("hello")</code> is not called',
            u'The␣code <code>function("hello")</code> is not called')

        self.assertHtml(
            u'The code <CODE>function("hello")</CODE> is not called',
            u'The␣code <code>function("hello")</code> is not called')

    def test_ignored_custom(self):
        self.assertHtml(
            u'The code <cite>function("hello")</cite> is not called',
            u'The␣code <cite>function("hello")</cite> is not called',
            ignored=['cite'])

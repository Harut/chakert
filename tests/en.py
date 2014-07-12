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

    def test_en_dash(self):
        self.assertText(
            u'Ages 5 - 8. Ages 5-8.',
            u'Ages 5 – 8. Ages 5–8.')

    def test_en_dash(self):
        self.assertText(
            u'An em-dash is used to indicate a break in thought - as illustrated here',
            u'An␣em-dash is used to␣indicate a␣break in␣thought␣— as␣illustrated here')

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


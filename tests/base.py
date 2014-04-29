# -*- coding: utf-8 -*-

import unittest
from etree_typo import Typograph

def highlight(txt):
    return txt.replace(u'\u00a0', u'␣')\
              .replace(u'\N{NON-BREAKING HYPHEN}', u'=')


class BaseTests(unittest.TestCase):

    def assertText(self, text, *args):
        value = Typograph.typograph_text(text, self.lang)
        value_hl = highlight(value)
        if not value_hl in args:
            print '\n'
            print value_hl
            for arg in args:
                print arg
            print '\n'
        self.assertIn(value_hl, args)

        value2 = Typograph.typograph_html(value, self.lang)
        if value != value2:
            print '\n', highlight(value), '\n', highlight(value2)
        self.assertEqual(highlight(value), highlight(value2))

    def assertHtml(self, text, *args):
        value = Typograph.typograph_html(text, self.lang)
        value_hl = highlight(value)
        if not value_hl in args:
            print '\n'
            print value_hl
            for arg in args:
                print arg
            print '\n'
        self.assertIn(value_hl, args)

        value2 = Typograph.typograph_html(value, self.lang)
        if value != value2:
            print '\n', highlight(value), '\n', highlight(value2)
        self.assertEqual(highlight(value), highlight(value2))

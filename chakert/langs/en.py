# -*- coding: utf-8 -*-
import re
from ..tokens import Token, WordToken as BaseWordToken, SpaceToken, NbspToken,\
    DigitsToken as BaseDigitsToken, OtherToken
from ..tokenizer import TokenString

import logging
logger = logging.getLogger(__name__)

try: #python3 support
    unicode
except NameError:
    unicode = str


def _ignorecase_repl(m):
    s = m.group()
    return '['+s+s.upper()+']'

PREPOSITIONS = frozenset(u'at|or|and|the|a|by|an|in|on|of|for|to|as|i|or|my'
                         u''.split(u'|'))
#PARTICLES = frozenset(u'б|бы|ж|же|ли|ль'.split(u'|'))
#HYPHEN_PARTICLES = frozenset(u'то|либо|нибудь|ка|де|таки'.split(u'|'))
#HYPHEN_PREPOSITIONS = frozenset(u'во|в|кое|из|по'.split(u'|'))

ALL_PARTICLES = (PREPOSITIONS #| PARTICLES |
                #HYPHEN_PARTICLES | HYPHEN_PREPOSITIONS
                 )

class WordToken(BaseWordToken):

    __slots__ = ['owner']

    def __new__(cls, content, owner):
        if content.lower() in ALL_PARTICLES:
            cls = ParticleToken
        # XXX does inlining make it really faster?
        self = unicode.__new__(cls, content)
        self.owner = owner
        return self


class ParticleToken(BaseWordToken):

    __slots__ = ['owner']

    regexp = None

    def morph(self, prev, next):
        lower = self.lower()
        #if lower in PARTICLES:
        #    if prev[0].__class__ is SpaceToken:
        #        # Non-breaking space
        #        prev[0] = prev[0].replace(NbspToken(u'\u00a0', self.owner))
        #        return

        #if lower in HYPHEN_PARTICLES:
        #    if prev[0].__class__ is DashToken and prev[0] == u'-':
        #        prev[0] = prev[0].replace(NbspToken(u'\N{NON-BREAKING HYPHEN}', self.owner))
        #        return
        #    elif prev[0] == u'\N{NON-BREAKING HYPHEN}':
        #        return

        if lower in PREPOSITIONS:
            if next[0].__class__ is SpaceToken:
                # Non-breaking space
                next[0] = next[0].replace(NbspToken(u'\u00a0', self.owner))
                return

        #if lower in HYPHEN_PREPOSITIONS:
        #    if next[0].__class__ is DashToken and next[0] == '-':
        #        if lower == u'кое' and \
        #                next[1] in PREPOSITIONS and \
        #                next[2].__class__ is DashToken and next[2] == '-':
        #            # кое-с-кем, кое-к-кому
        #            next[2] = next[2].replace(DashToken(u'\N{NON-BREAKING HYPHEN}', self.owner))
        #        next[0] = next[0].replace(DashToken(u'\N{NON-BREAKING HYPHEN}', self.owner))
        #        return


class DigitsToken(BaseDigitsToken):

    __slots__ = ['owner']

    MONTHS = frozenset([u'january', u'february', u'march', u'april', u'may', 
                        u'june', u'july', u'august', u'september', u'october',
                        u'november', u'december'])
    SHORT_MONTHS = frozenset([x[:3] for x in MONTHS])
    ALL_MONTHS = MONTHS | SHORT_MONTHS

    def morph(self, prev, next):
        if len(self) <= 2 and prev[0].__class__ is SpaceToken:
            if (prev[1].__class__ is WordToken and \
                    prev[1].lower() in self.ALL_MONTHS
                ) or (
                    prev[1] == '.' and \
                    prev[2].__class__ is WordToken and \
                    prev[2].lower() in self.SHORT_MONTHS):
                prev[0] = prev[0].replace(NbspToken(u'\u00a0', self.owner))


class PunctuationToken(Token):

    __slots__ = ['owner']

    regexp = re.compile(u'[\.,;\'?!%&…+­@]')

    def morph(self, prev, next):
        if '.' == self == next[0] == next[1] \
                and not isinstance(prev[0], PunctuationToken):
            self = self.replace(PunctuationToken(u'…', self.owner))
            next.pop(0).drop()
            next.pop(0).drop()


class QuoteToken(Token):

    __slots__ = ['owner']

    regexp = re.compile(u'["«»'
                        u'\N{DOUBLE LOW-9 QUOTATION MARK}'
                        u'\N{SINGLE LOW-9 QUOTATION MARK}'
                        u'\N{LEFT SINGLE QUOTATION MARK}'
                        u'\N{RIGHT SINGLE QUOTATION MARK}'
                        u'\N{RIGHT DOUBLE QUOTATION MARK}'
                        u'\N{LEFT DOUBLE QUOTATION MARK}]')

    open_quotes = (u'\N{RIGHT DOUBLE QUOTATION MARK}'
                   u'\N{LEFT SINGLE QUOTATION MARK}')
    close_quotes = (u'\N{LEFT DOUBLE QUOTATION MARK}'
                    u'\N{RIGHT SINGLE QUOTATION MARK}')
    quotes_dict = dict(zip(open_quotes, close_quotes))

    def morph(self, prev, next):
        quote_stack = self.owner.typograph.quote_stack
        if self in u'«\N{DOUBLE LOW-9 QUOTATION MARK}\N{SINGLE LOW-9 QUOTATION MARK}':
            self = self.replace(QuoteToken(u"\N{RIGHT DOUBLE QUOTATION MARK}", self.owner))

        if self == u'»':
            self = self.replace(QuoteToken(u"\N{LEFT DOUBLE QUOTATION MARK}", self.owner))

        if self == u'"':
            if isinstance(prev[0], SpaceToken) or \
                    prev[0] == '(' or prev[0] is None:
                quote = self.open_quotes[len(quote_stack)] if \
                            len(quote_stack) < len(self.open_quotes) else \
                            self.open_quotes[-1]
                quote_stack.append(quote)
                self.replace(QuoteToken(quote, self.owner))
            else:
                if quote_stack:
                    quote = self.quotes_dict[quote_stack.pop()]
                else:
                    quote = self.close_quotes[0]
                self.replace(QuoteToken(quote, self.owner))
        elif self in self.open_quotes:
            quote_stack.append(self)
        elif self in self.close_quotes:
            if not quote_stack:
                prevs_str = u''.join(reversed([prev[i]
                                               for i in range(20)
                                               if prev[i]]))
                logger.warn(u'Unmatched closing quote after: %s', prevs_str)
            else:
                quote_stack.pop()

        # XXX not complete!


class DashToken(Token):

    __slots__ = ['owner']

    regexp = re.compile(u'[-\N{NON-BREAKING HYPHEN}\N{FIGURE DASH}'
                        u'\N{EN DASH}\N{EM DASH}\N{Hyphen}]') # XXX \u2043 ?
    hyphens = list(u'-\N{Hyphen}')

    def morph(self, prev, next):
        if self in u'-\N{Hyphen}':
            while next[0] in self.hyphens:
                # replace double hyphen to EM DASH in all cases
                # Afterwards it can be replaced to MINUS, EN DASH according 
                # correspondent replacement rules
                self = self.replace(DashToken(u'\N{EM DASH}', self.owner))
                next.pop(0).drop()

            if (isinstance(prev[0], SpaceToken) and
                    isinstance(next[0], SpaceToken)):

                if (isinstance(prev[1], DigitsToken)
                        and isinstance(next[1], DigitsToken)):
                    self = self.replace(DashToken(u'\N{EN DASH}', self.owner))
                else:
                    self = self.replace(DashToken(u'\N{EM DASH}', self.owner))

            elif isinstance(next[0], DigitsToken):
                # XXX how exactly determine if self is minus or EN DASH?
                if isinstance(prev[0], DigitsToken):
                    self = self.replace(
                            DashToken(u'\N{EN DASH}', self.owner))
                elif isinstance(prev[0], SpaceToken) or prev[0] is None:
                    self = self.replace(
                            DashToken(u'\N{MINUS SIGN}', self.owner))

        if self in u'\N{EN DASH}\N{EM DASH}' and prev[0].__class__ is SpaceToken:
            prev[0] = prev[0].replace(NbspToken(u'\u00A0', self.owner))


class EnTokenString(TokenString):

    token_classes = [SpaceToken, NbspToken, PunctuationToken, QuoteToken,
                     DashToken, DigitsToken, WordToken, OtherToken]



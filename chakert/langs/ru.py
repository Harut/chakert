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

PREPOSITIONS = frozenset(u'а|ай|в|во|да|до|за|и|из|к|ко|на'
                         u'|не|ни|но|ну|о|об|ой|от|по|с|со|то|у|уж|№'
                         u''.split(u'|'))
# XXX stick short pronouns to the next word or not?
SHORT_PRONOUNS = frozenset(u'вы|ее|её|ей|их|мы|он|ты|я'.split(u'|'))
PARTICLES = frozenset(u'б|бы|ж|же|ли|ль'.split(u'|'))
HYPHEN_PARTICLES = frozenset(u'то|либо|нибудь|ка|де|таки'.split(u'|'))
HYPHEN_PREPOSITIONS = frozenset(u'во|в|кое|из|по'.split(u'|'))

ALL_PARTICLES = (PREPOSITIONS | PARTICLES |
                 HYPHEN_PARTICLES | HYPHEN_PREPOSITIONS)

class WordToken(BaseWordToken):

    __slots__ = ['owner']

    regexp = re.compile(u'[\d\w\N{ACUTE ACCENT}¹²³№]+', re.UNICODE)

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
        if lower in PARTICLES:
            if prev[0].__class__ is SpaceToken:
                # Non-breaking space
                prev[0] = prev[0].replace(NbspToken(u'\u00a0', self.owner))
                return

        if lower in HYPHEN_PARTICLES:
            if prev[0].__class__ is DashToken and prev[0] == u'-':
                prev[0] = prev[0].replace(NbspToken(u'\N{NON-BREAKING HYPHEN}', self.owner))
                return
            elif prev[0] == u'\N{NON-BREAKING HYPHEN}':
                return

        if lower in PREPOSITIONS:
            if next[0].__class__ is SpaceToken:
                # Non-breaking space
                next[0] = next[0].replace(NbspToken(u'\u00a0', self.owner))
                return

        if lower in HYPHEN_PREPOSITIONS:
            if next[0].__class__ is DashToken and next[0] == '-':
                if lower == u'кое' and \
                        next[1] in PREPOSITIONS and \
                        next[2].__class__ is DashToken and next[2] == '-':
                    # кое-с-кем, кое-к-кому
                    next[2] = next[2].replace(DashToken(u'\N{NON-BREAKING HYPHEN}', self.owner))
                next[0] = next[0].replace(DashToken(u'\N{NON-BREAKING HYPHEN}', self.owner))
                return


class AbbrToken(BaseWordToken):

    __slots__ = ['owner']

    ABBRS_RE = u'W(?: w)+(?=\.)'.replace(u'W', u'[а-яА-Я][а-я]?')\
                                .replace(u'w', u'[а-я]{1,2}')\
                                .replace(u' ', u'\.(?:\N{NON-BREAKING HYPHEN}|-|\s*)')
    regexp = re.compile(ABBRS_RE, re.UNICODE)

    def __new__(cls, content, owner):
        content = re.sub(u'\.[\s\u00A0]*', u'.\u00a0', content)
        content = content.replace(u'-', u'\N{NON-BREAKING HYPHEN}')
        self = unicode.__new__(cls, content)
        self.owner = owner
        return self


class DigitsToken(BaseDigitsToken):

    __slots__ = ['owner']

    year_re = re.compile(u'(?:г|гг|год[а-я]{,3})$',
                         re.IGNORECASE | re.UNICODE)
    months_re = re.compile(u'(?:января|февраля|марта|апреля|мая|июня|июля|'
                           u'августа|сентября|ноября|декабря)$',
                           re.IGNORECASE | re.UNICODE)

    def morph(self, prev, next):

        if len(self) <= 4 and \
                next[0].__class__ is SpaceToken and\
                next[1].__class__ is WordToken and \
                self.year_re.match(next[1]):
            next[0] = next[0].replace(NbspToken(u'\u00a0', self.owner))

        elif len(self) <= 2 and \
                next[0].__class__ is SpaceToken and\
                next[1].__class__ is WordToken and \
                self.months_re.match(next[1]):
            next[0] = next[0].replace(NbspToken(u'\u00a0', self.owner))


class PunctuationToken(Token):

    __slots__ = ['owner']

    regexp = re.compile(u'[\.,;\'?!%&…+­@]')

    def morph(self, prev, next):
        if '.' == self == next[0] and prev[0] not in list('!?'):
            self = self.replace(PunctuationToken(u'…', self.owner))
            while next[0] == '.':
                next.pop(0).drop()


class QuoteToken(Token):

    __slots__ = ['owner']

    regexp = re.compile(u'["«»„“\N{LEFT SINGLE QUOTATION MARK}'
                        u'\N{RIGHT SINGLE QUOTATION MARK}'
                        u'\N{RIGHT DOUBLE QUOTATION MARK}]')

    open_quotes = u'«„'
    all_open_quotes = open_quotes + u''
    close_quotes = u'»“'
    quotes_dict = dict(zip(open_quotes, close_quotes))

    def morph(self, prev, next):
        quote_stack = self.owner.typograph.quote_stack
        if self == u'\N{RIGHT DOUBLE QUOTATION MARK}':
            self = self.replace(QuoteToken(u"„", self.owner))

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
                        u'\N{MINUS SIGN}\N{EN DASH}\N{EM DASH}\N{Hyphen}]')
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

            elif (isinstance(prev[0], PunctuationToken) and 
                    (prev[0] == u'…' or 
                        (prev[0] == u'.' and 
                         isinstance(prev[1], PunctuationToken))) and
                    isinstance(next[0], SpaceToken)):
                # Em dash after ellipsis:
                # Вы уверены?..— сказал медведь.
                # Да…— сказали звери
                self = self.replace(DashToken(u'\N{EM DASH}', self.owner))

            elif isinstance(next[0], DigitsToken):
                # XXX how exactly determine if self is minus or EN DASH?
                if isinstance(prev[0], DigitsToken):
                    self = self.replace(
                            DashToken(u'\N{EN DASH}', self.owner))
                elif isinstance(prev[0], SpaceToken) or prev[0] is None:
                    self = self.replace(
                            DashToken(u'\N{MINUS SIGN}', self.owner))

        if prev[0] is None and self in u'-\N{EN DASH}\N{Hyphen}':
            self = self.replace(DashToken(u'\N{EM DASH}', self.owner))

        if self in u'\N{EN DASH}\N{EM DASH}' and prev[0].__class__ is SpaceToken:
            prev[0] = prev[0].replace(NbspToken(u'\u00A0', self.owner))

# XXX emails!
# XXX phone numbers!
# XXX person names
# XXX Привязка союзов и предлогов в предыдущим словам в случае конца предложения.

class RuTokenString(TokenString):

    token_classes = [SpaceToken, NbspToken, PunctuationToken, QuoteToken,
                     DashToken, DigitsToken, AbbrToken, WordToken, OtherToken]



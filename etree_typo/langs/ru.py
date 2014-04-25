# -*- coding: utf-8 -*-
import re
from ..tokens import Token, WordToken, SpaceToken, NbspToken, \
    DigitsToken as BaseDigitsToken, OtherToken
from ..tokenizer import TokenString


#_ABBRS = (u'т. д|'
#          u'т. п|'
#          u'т. к|'
#          u'т. ч|'
#          u'т. е|'
#          u'т. н|'
#          u'н. э|'
#          u'н. в|'
#          u'и. о|'
#          u'вр. и. о|'
#          u'п. п|'
#          u'(?:к|д). [а-я]. н|'
#          u'(?:к|д). [а-я].-[а-я]. н|'
#          u'P. S|'
#          u'P. P. S')

PREPOSITIONS = frozenset(u'а|ай|в|вы|во|да|до|ее|её|ей|за|и|из|их|к|ко|мы|на'
                         u'|не|ни|но|ну|о|об|ой|он|от|по|с|со|то|ты|у|уж'
                         u'|я'.split(u'|'))
PARTICLES = frozenset(u'б|бы|ж|же|ли|ль'.split(u'|'))
HYPHEN_PARTICLES = frozenset(u'то|либо|нибудь|ка|де|таки'.split(u'|'))
HYPHEN_PREPOSITIONS = frozenset(u'во|в|кое|из|по'.split(u'|'))

ALL_PARTICLES = u'|'.join(PREPOSITIONS | PARTICLES | HYPHEN_PARTICLES | HYPHEN_PREPOSITIONS)


class ParticleToken(WordToken):

    regexp = re.compile(u'({})(?![\d\w¹²³])'.format(ALL_PARTICLES),
                        re.UNICODE|re.IGNORECASE)

    def morph(self, prev, next):
        lower = self.lower()
        if lower in PARTICLES:
            if prev[0].__class__ is SpaceToken:
                # Non-breaking space
                prev[0] = prev[0].replace(NbspToken(u'\u00a0', self.owner))
                return

        if lower in HYPHEN_PARTICLES:
           if prev[0].__class__ is DashToken and prev[0] == '-':
                # Non-breaking hyphen
                prev[0] = prev[0].replace(NbspToken(u'\N{NON-BREAKING HYPHEN}', self.owner))
                return

        if lower in PREPOSITIONS:
            if next[0].__class__ is SpaceToken:
                # Non-breaking space
                next[0] = next[0].replace(NbspToken(u'\u00a0', self.owner), morphed=False)
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


class AbbrToken(WordToken):

    ABBRS_RE = u'W(?: w)+(?=\.)'.replace(u'W', u'[а-яА-Я][а-я]?')\
                                .replace(u'w', u'[а-я]{1,2}')\
                                .replace(u' ', u'\.(?:N{NON-BREAKING HYPHEN}|-|\s*)')
    regexp = re.compile(ABBRS_RE, re.UNICODE)

    def __new__(cls, content, owner):
        content = re.sub(u'\.\s*', u'.\u00a0', content)
        content = content.replace(u'-', u'\N{NON-BREAKING HYPHEN}')
        return WordToken.__new__(cls, content, owner)


class DigitsToken(BaseDigitsToken):

    year_re = re.compile(u'(?:г|гг|год[а-я]{,3})$')
    months_re = re.compile(u'(?:января|февраля|марта|апреля|мая|июня|июля|'
                           u'августа|сентября|ноября|декабря)$')

    def morph(self, prev, next):
        if len(self) <= 4 and \
                next[0].__class__ is SpaceToken and\
                next[1].__class__ is WordToken and \
                self.year_re.match(next[1]):
            next[0] = next[0].replace(NbspToken(u'\u00a0', self.owner), morphed=False)

        elif len(self) <= 2 and \
                next[0].__class__ is SpaceToken and\
                next[1].__class__ is WordToken and \
                self.months_re.match(next[1]):
            next[0] = next[0].replace(NbspToken(u'\u00a0', self.owner), morphed=False)


class PunctuationToken(Token):

    regexp = re.compile(u'[\.,;\'?!%&№…+­@]')

    def morph(self, prev, next):
        if '.' == self == next[0]:
            self = self.replace(PunctuationToken(u'…', self.owner))
            while next[0] == '.':
                next.pop(0).drop()


class QuoteToken(Token):

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
            if isinstance(prev[0], SpaceToken):
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
            quote_stack.pop()

        # XXX not complete!


class DashToken(Token):

    regexp = re.compile(u'[-\N{NON-BREAKING HYPHEN}\N{FIGURE DASH}'
                        u'\N{EN DASH}\N{EM DASH}\N{Hyphen}]') # XXX \u2043 ?

    def morph(self, prev, next):
        if self != u'\N{EM DASH}' and prev[0] is None:
            self = self.replace(DashToken(u'\N{EM DASH}', self.owner))

        if (self == u'-' and isinstance(prev[0], SpaceToken)
                         and isinstance(next[0], SpaceToken)):
            self = self.replace(DashToken(u'\N{EM DASH}', self.owner))

        if (self == u'-' and isinstance(prev[0], DigitsToken)
                         and isinstance(next[0], DigitsToken)):
            # XXX how determine if self is minus or figure dash?
            self = self.replace(DashToken(u'\N{FIGURE DASH}', self.owner))

        if self in u'\N{EN DASH}\N{EM DASH}' and prev[0].__class__ is SpaceToken:
            prev[0] = prev[0].replace(NbspToken(u'\u00A0', self.owner))

# XXX emails!
# XXX phone numbers!
# XXX person names
# XXX Привязка союзов и предлогов в предыдущим словам в случае конца предложения.

class RuTokenString(TokenString):

    token_classes = [SpaceToken, PunctuationToken, QuoteToken, DashToken,
                     DigitsToken, AbbrToken, ParticleToken, WordToken]
    default_token_class = OtherToken



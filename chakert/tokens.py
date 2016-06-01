# -*- coding: utf-8 -*-
import re

try: #python3 support
    unicode
except NameError:
    unicode = str


class Token(unicode):

    __slots__ = ['owner']

    def __new__(cls, content, owner):
        self = unicode.__new__(cls, content)
        self.owner = owner
        return self

    def morph(self, prev, next):
        pass

    def drop(self):
        # we can't use remove because as string comparison two
        # different tokens with equal content are equal
        tokens = self.owner.tokens
        for i, el in enumerate(tokens):
            if el is self:
                tokens.pop(i)
                typograph = self.owner.typograph
                if typograph.active_token is self:
                    typograph.active_token = None
                    typograph.ti -= 1
                break

    def replace(self, token):
        assert isinstance(token, Token)
        # we can't use remove because as string comparison two
        # different tokens with equal content are equal
        tokens = self.owner.tokens
        for i, el in enumerate(tokens):
            if el is self:
                tokens[i] = token
                return token

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.encode('utf-8'))


class WordToken(Token):

    __slots__ = ['owner']

    regexp = re.compile(u'[\d\w\N{ACUTE ACCENT}¹²³]+', re.UNICODE)


class SpaceToken(Token):

    __slots__ = ['owner']

    regexp = re.compile(u'[ \t\r\n]+')

    def __repr__(self):
        return b'{}({})'.format(self.__class__.__name__, unicode.__repr__(self))


class NbspToken(SpaceToken):

    __slots__ = ['owner']

    regexp = re.compile(u'[\u00A0]+')


class DigitsToken(Token):

    __slots__ = ['owner']

    regexp = re.compile(u'[\d¹²³]+(?!\w)', re.UNICODE)


class CodeToken(Token):

    __slots__ = ['owner']

    def morph(self, prev, next):
        pass

    def drop(self):
        pass

    def replace(self, token):
        pass

    def __bool__(self):
        return True
    __nonzero__ = __bool__


class OtherToken(Token):

    __slots__ = ['owner']

    regexp = re.compile(u'.', re.UNICODE)

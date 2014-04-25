# -*- coding: utf-8 -*-
import re


class Token(unicode):

    morphed = False

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

    def replace(self, token, morphed=True):
        assert isinstance(token, Token)
        # we can't use remove because as string comparison two
        # different tokens with equal content are equal
        tokens = self.owner.tokens
        for i, el in enumerate(tokens):
            if el is self:
                token.morphed = morphed
                tokens[i] = token
                return token

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.encode('utf-8'))


class WordToken(Token):

    regexp = re.compile(u'[\d\w\N{ACUTE ACCENT}¹²³]+', re.UNICODE)


class SpaceToken(Token):

    regexp = re.compile(u'[ \t\r\n\u00A0]+')

    def __new__(cls, content, owner):
        if u'\u00a0' in content:
            cls = NbspToken
            content = u'\u00a0'
        content = content[:1]
        return Token.__new__(cls, content, owner)

    def morph(self, prev, next):
        while isinstance(next[0], SpaceToken):
            if isinstance(next[0], NbspToken):
                self, _ = next.pop(0), self.drop()
            else:
                next.pop(0).drop()


    def __repr__(self):
        return b'{}({})'.format(self.__class__.__name__, unicode.__repr__(self))


class NbspToken(SpaceToken):

    regexp = re.compile(u'[\u00A0]+')


class DigitsToken(Token):

    regexp = re.compile(u'[\d¹²³]+(?!\w)', re.UNICODE)


class OtherToken(Token):
    pass

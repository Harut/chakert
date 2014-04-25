# -*- coding: utf-8 -*-
import re
from lxml import html
from .util import LazyList, inner_html



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

    def replace(self, token):
        assert isinstance(token, Token)
        # we can't use remove because as string comparison two
        # different tokens with equal content are equal
        tokens = self.owner.tokens
        for i, el in enumerate(tokens):
            if el is self:
                token.morphed = True
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

    def __repr__(self):
        return b'{}({})'.format(self.__class__.__name__, unicode.__repr__(self))


class NbspToken(SpaceToken):

    regexp = re.compile(u'[\u00A0]+')


class DigitsToken(Token):

    regexp = re.compile(u'[\d¹²³]+(?!\w)', re.UNICODE)


class OtherToken(Token):
    pass


class TokenString(object):

    token_classes = NotImplemented

    def __init__(self, typograph, text, element=None, apply_to=None):
        self.typograph = typograph
        self.element = element
        self.apply_to = apply_to
        self.tokens = self._tokenize(text)

    def _tokenize(self, text):
        tokens = []
        while text:
            for cls in self.token_classes:
                match = cls.regexp.match(text)
                if match is not None:
                    matched = match.group()
                    break
            else:
                matched, cls = text[0], OtherToken
            token = cls(matched, self)
            tokens.append(token)
            text = text[len(matched):]
        return tokens

    @property
    def text(self):
        return u''.join(self.tokens)

    def apply(self):
        if self.apply_to is not None:
            setattr(self.element, self.apply_to, self.text)

    def __repr__(self):
        childs = b',\n    '.join(repr(x) for x in self.tokens)
        return b'{}(\n    {})'.format(self.__class__.__name__, childs)


class Typograph(object):

    TokenString = TokenString

    def __init__(self):
        self.token_strings = []
        self.quote_stack = []

    def new_alone_node(self, text):
        token_string = self.TokenString(self, text)
        self.token_strings.append(token_string)

    def new_text_node(self, element):
        token_string = self.TokenString(self, element.text, element,
                                        apply_to='text')
        self.token_strings.append(token_string)

    def new_tail_node(self, element):
        token_string = self.TokenString(self, element.tail, element,
                                       apply_to='tail')
        self.token_strings.append(token_string)

    def morph(self):
        for token in self:
            if not token.morphed:
                token.morphed = True
                token.morph(self.prev(), self.next())
        for token_string in self.token_strings:
            token_string.apply()

    def __iter__(self):
        for tsi, token_string in enumerate(self.token_strings):
            self.tsi = tsi
            self.ti = 0
            while self.ti < len(token_string.tokens):
                self.active_token = token_string.tokens[self.ti]
                yield self.active_token
                self.ti += 1

    def _prev(self):
        tsi, ti = self.tsi, self.ti-1
        while tsi >= 0:
            while ti >= 0:
                yield self.token_strings[tsi].tokens[ti]
                ti -= 1
            tsi -= 1
            ti = len(self.token_strings[tsi].tokens) - 1
        while 1:
            yield None

    def _next(self):
        tsi, ti = self.tsi, self.ti+1
        while tsi < len(self.token_strings):
            while ti < len(self.token_strings[tsi].tokens):
                yield self.token_strings[tsi].tokens[ti]
                ti += 1
            tsi += 1
            ti = 0
        while 1:
            yield None

    def prev(self):
        return LazyList(self._prev)

    def next(self):
        return LazyList(self._next)

    @property
    def text(self):
        return u''.join([x.text for x in self.token_strings])

    def __repr__(self):
        childs = b',\n   '.join(repr(x) for x in self.token_strings)
        return b'{}(\n  {})'.format(self.__class__.__name__, childs)


    @classmethod
    def typograph_tree(cls, tree, strings=None):
        strings = strings or cls()
        if tree.text:
            strings.new_text_node(tree)
        for child in tree.iterchildren():
            if child.tag in ['p', 'blockquote', 'div']:
                # block element, flush context
                strings.morph()
                cls.typograph_tree(child)
                strings = cls()
            else:
                cls.typograph_tree(child, strings)
            if child.tail:
                strings.new_tail_node(child)
        strings.morph()

    @classmethod
    def typograph_html(cls, markup):
        #markup = markup.encode('utf-8')
        doc = html.fragment_fromstring(markup, create_parent=True)
        cls.typograph_tree(doc)
        return inner_html(doc)

    @classmethod
    def typograph_text(cls, text):
        strings = cls()
        strings.new_alone_node(text)
        strings.morph()
        return strings.text


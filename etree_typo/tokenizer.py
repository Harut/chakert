# -*- coding: utf-8 -*-
from lxml import html
from .util import LazyList, inner_html


# XXX name of class is not perfect
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
                matched, cls = text[0], self.default_token_class
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


class BaseTypograph(object):

    # XXX name of attribute is not perfect
    rules_by_language = {}

    def __init__(self, lang):
        self.lang = lang
        self.token_strings = []
        self.quote_stack = []
        self.TokenString = self.rules_by_language.get(lang)

    def new_alone_node(self, text):
        if self.TokenString is not None:
            token_string = self.TokenString(self, text)
            self.token_strings.append(token_string)
        # else: typography rules for language are not implemented, skip

    def new_text_node(self, element):
        if self.TokenString is not None:
            token_string = self.TokenString(self, element.text, element,
                                            apply_to='text')
            self.token_strings.append(token_string)
        # else: typography rules for language are not implemented, skip

    def new_tail_node(self, element):
        if self.TokenString is not None:
            token_string = self.TokenString(self, element.tail, element,
                                           apply_to='tail')
            self.token_strings.append(token_string)
        # else: typography rules for language are not implemented, skip

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
    def typograph_tree(cls, tree, lang=None, typograph=None):
        if 'lang' in tree.attrib:
            lang = tree.attrib['lang'].split('_')[1]
        if typograph is None:
            typograph = cls(lang)
        if tree.text:
            typograph.new_text_node(tree)
        for child in tree.iterchildren():
            if child.tag in ['p', 'blockquote', 'div']:
                # block element, flush context
                typograph.morph()
                cls.typograph_tree(child, lang).morph()
                typograph = cls(lang)
            else:
                cls.typograph_tree(child, lang, typograph)
            if child.tail:
                typograph.new_tail_node(child)
        return typograph

    @classmethod
    def typograph_html(cls, markup, lang=None):
        doc = html.fragment_fromstring(markup, create_parent=True)
        cls.typograph_tree(doc, lang=lang).morph()
        return inner_html(doc)

    @classmethod
    def typograph_text(cls, text, lang=None):
        typograph = cls(lang)
        typograph.new_alone_node(text)
        typograph.morph()
        return typograph.text


# -*- coding: utf-8 -*-
import re
from lxml import html
from .util import LazyList, inner_html

class TokenCompileMeta(type):

    def __init__(cls, name, bases, dict_):
        token_classes = dict_['token_classes']
        if token_classes is not NotImplemented:
            for c in token_classes:
                assert c.regexp.groups == 0, \
                        u"{} {}".format(c, c.regexp.pattern)
            r = (u'(' +
                 u')|('.join(x.regexp.pattern for x in token_classes) +
                 u')')
            cls._compiled_re = re.compile(r, re.UNICODE)
            dict_ = dict(dict_, _compiled_re=cls._compiled_re)
        type.__init__(cls, name, bases, dict_)


# XXX name of class is not perfect
class TokenString(object):

    token_classes = NotImplemented
    __metaclass__ = TokenCompileMeta

    def __init__(self, typograph, text, element=None, apply_to=None):
        self.typograph = typograph
        self.element = element
        self.apply_to = apply_to
        self.init_text = text
        self.tokens = self._tokenize(text)

    def _tokenize(self, text):
        tokens = []
        f_match = self.__class__._compiled_re.match
        offset = 0
        length = len(text)
        while offset < length:
            match = f_match(text, offset)
            matched = match.group()
            tokens.append(self.token_classes[match.lastindex-1](matched, self))
            offset += len(matched)
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


_space = u'[ \t\r\n\u00A0]'
_end_space_re = re.compile(_space + u'$')
_start_space_re = re.compile(u'^'+_space+u'+')
_space_re = re.compile(_space + u'{2,}')


class BaseTypograph(object):

    # XXX name of attribute is not perfect
    rules_by_language = {}

    def __init__(self, lang):
        self.lang = lang
        self.token_strings = []
        self.quote_stack = []
        self.TokenString = self.rules_by_language.get(lang)

    def new_node(self, text, element=None, apply_to=None):
        # normalize whitespaces
        if self.token_strings:
            last_string = self.token_strings[-1].text
            if _end_space_re.search(last_string) is not None:
                text = _start_space_re.sub(u'', text)
        text = _space_re.sub(u' ', text)

        if not text and apply_to is not None:
            setattr(element, apply_to, text)

        elif self.TokenString is not None:
            token_string = self.TokenString(self, text, element, apply_to)
            self.token_strings.append(token_string)
        # else: typography rules for language are not implemented, skip

    def morph(self):
        _next, _prev = LazyList(self._prev), LazyList(self._next)
        for token in self:
            _next.reset()
            _prev.reset()
            token.morph(_next, _prev)
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

    @property
    def text(self):
        return u''.join([x.text for x in self.token_strings])

    def __repr__(self):
        childs = b',\n   '.join(repr(x) for x in self.token_strings)
        return b'{}(\n  {})'.format(self.__class__.__name__, childs)


    @classmethod
    def _typograph_tree(cls, tree, lang=None, typograph=None):
        if 'lang' in tree.attrib:
            lang = tree.attrib['lang'].split('_')[1]
        if typograph is None:
            typograph = cls(lang)
        if tree.text:
            typograph.new_node(tree.text, tree, apply_to="text")
        for child in tree.iterchildren():
            # XXX full list of block tags!
            if child.tag in ['p', 'blockquote', 'div']:
                # block element, flush context
                typograph.morph()
                cls._typograph_tree(child, lang).morph()
                typograph = cls(lang)
            else:
                cls._typograph_tree(child, lang, typograph)
            if child.tail:
                typograph.new_node(child.tail, child, apply_to='tail')
        return typograph

    @classmethod
    def typograph_tree(cls, tree, lang):
        cls._typograph_tree(tree, lang).morph()

    @classmethod
    def typograph_html(cls, markup, lang):
        doc = html.fragment_fromstring(markup, create_parent=True)
        cls.typograph_tree(doc, lang)
        return inner_html(doc)

    @classmethod
    def typograph_text(cls, text, lang):
        typograph = cls(lang)
        typograph.new_node(text)
        typograph.morph()
        return typograph.text


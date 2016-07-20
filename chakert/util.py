# -*- coding: utf-8 -*-
try:
    from lxml import html
except ImportError:
    html = None

class LazyList(object):

    __slots__ = ['data', 'constructor', 'iterator']

    def __init__(self, constructor):
        self.data = []
        self.constructor = constructor
        self.iterator = None#constructor()

    def __setitem__(self, index, value):
        self.data[index] = value

    def __getitem__(self, index):
        if self.iterator is None:
            self.iterator = self.constructor()
        while len(self.data) <= index:
            self.data.append(next(self.iterator))
        return self.data[index]

    def reset(self):
        # re-init generator
        self.data = []
        self.iterator = None#self.constructor()

    def pop(self, index):
        self[index]
        value = self.data.pop(index)
        self.reset()
        return value


def inner_html(tag):
    assert html is not None, 'Install lxml to work with html'
    # XXX encode/decode everywhere is really HELL
    txt = (tag.text or u'')
    txt2 = b''.join([html.tostring(x, encoding='utf-8')
                     for x in tag.iterchildren()])
    return txt + txt2.decode('utf-8')



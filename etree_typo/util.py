# -*- coding: utf-8 -*-
from lxml import html

class LazyList(object):
    def __init__(self, constructor):
        self.data = [ ]
        self.constructor = constructor
        self.iterator = constructor()

    def __setitem__(self, index, value):
        self.data[index] = value

    def __getitem__(self, index):
        while len(self.data) <= index:
            self.data.append(self.iterator.next())
        return self.data[index]

    def pop(self, index):
        self[index]
        value = self.data.pop(index)

        # re-init generator
        self.data = [ ]
        self.iterator = self.constructor()
        return value

def inner_html(tag):
    # XXX encode/decode everywhere is really HELL
    txt = (tag.text or u'')
    txt2 = b''.join([html.tostring(x, encoding='utf-8')
                     for x in tag.iterchildren()])
    return txt + txt2.decode('utf-8')



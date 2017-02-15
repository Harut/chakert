'''Example implementation of typography tag and filter for jinja2'''

from jinja2 import nodes, contextfilter
from jinja2.ext import Extension
from chakert import Typograph


class TypographExtension(Extension):
    # a set of names that trigger the extension.
    tags = set(['typograph'])

    def parse(self, parser):
        # the first token is the token that started the tag.  In our case
        # we only listen to ``'typograph'`` so this will be a name token with
        # `typograph` as value.  We get the line number so that we can give
        # that line number to the nodes we create by hand.
        lineno = next(parser.stream).lineno

        # now we parse the body of the block up to `endtypograph` and
        # drop the needle (which would always be `endtypograph` in that case)
        body = parser.parse_statements(['name:endtypograph'], drop_needle=True)

        # pass the context as an argument to called method
        ctx_ref = nodes.ContextReference()

        # now return a `CallBlock` node that calls our _typograph_support
        # helper method on this extension.
        node = self.call_method('_typograph_support', [ctx_ref], lineno=lineno)
        return nodes.CallBlock(node, [], [], body, lineno=lineno)

    def _typograph_support(self, context, caller=None):
        return Typograph.typograph_html(caller(), context['lang'])


@contextfilter
def do_typograph(context, value):
    return Typograph.typograph_text(value, context['lang'])

# Typography tool for lxml.html or plain text

Tool applying a set of common typography rules 
(such as non-breaking spaces, dashes ellipsyses replacements) 
to the text.

## Usage

For html:

    from etree_typo import Typograph
    markup = '<p><b>Typography</b> is the art and technique of arranging type.</p>'
    result_markup = Typograph.typograph_html(markup)

For parsed lxml.html tree:

    from etree_typo import Typograph
    from lxml import html
    markup = '<p><b>Typography</b> is the art and technique of arranging type.</p>'
    tree = html.fromstring(markup)
    result_tree = Typograph.typograph_tree(tree)

For plain text:

    from etree_typo import Typograph
    text = 'Typography is the art and technique of arranging type.'
    result_text = Typograph.typograph_text(text)


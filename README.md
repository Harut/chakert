# Typography for lxml.html or plain text

Tool applying a set of common typography rules 
(such as non-breaking spaces, dashes and ellipsyses replacements, etc) 
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

## Replacement rules

The typograph parses given text and splits it into tokens. 
Each token is instance of `etree_typo.tokens.Token` subclass.
Each `Token` subclass represents a class of specific lexems with
defined replacement rules. `Token` subclasses are, for example, 
`WordToken`, `ParticleToken`, `AbbrToken`, `SpaceToken`,
`PunctuationTokn`, `QuoteToken`, `DashToken`,
`NbspToken`, `DigitsToken`.

### Russian

A set of rules for Russian language.

1. Проставление неразрывных пробелов после предлогов, союзов, частиц а также перед частицами (бы, же и др.).
2. Проставление неразрывных дефисов (во-первых, кое-с-кем, кто-то).
3. Проставление неразрывных пробелов и дефисов в сокращениях (в т. ч., д. ф.-м. н.).
4. Пробел между числом длиной до 2 символов и названием месяца заменяется на неразрывный.
5. Пробел между числом длиной до 4 символов и словом “год” в различных вариациях заменяется на неразрывный.
6. Объединение пробелов, если пробельных символов несколько, то они заменяются на один обычный пробел.
7. Дефис в начале параграфа/текста заменяется на длинное тире.
8. Если дефис окружён пробелами, то он заменяется на длинное тире, а пробел перед ним - на неразрывный.
9. Если дефис окружен цифрами, то он преобразуется в короткое тире.
10. Пробел + дефис перед числом на минус (−3 °C).
11. Две и более точки подряд заменяются на многоточие, если перед ними не стоит другой знак препинания (?.. , !.. , ?!.) (кавычки и запятые не в счёт).
12. Двойные кавычки (") заменяются на ёлочки («»). Если кавычка прилеплена к слову слева, то она считается открывающей, иначе — закрывающей.
13. Вложенные кавычки заменяются на двойные косые нижнюю и верхнюю („“).

### English

A set of rules for Russian language.

1. Non-breaking spaces after prepositions, conjunctions and articles.
2. Non-breaking space between month name and number of one or two digits.
3. If there are multiple spaces in line, they are merged into one.
4. If the hyphen is surrounded by spaces, it is replaced by em dash, and the space before is replaced y non-breaking space.
5. If the hyphen is surrounded by numbers, it is replaced by en dash.
6. Space + hyphen before a number is replaced by minus sign (−3 °C)
7. Exactly 3 points are replaced by ellipsys (it can be 4 points in line in English https://dl.dropboxusercontent.com/u/351006/ellipsis.png).
8. Double quotes (") are replaced by left and right double quotes.
9. Nested quotes are replaced to left and right single quotes.


# Typography for lxml.html or plain text

[![Build Status](https://travis-ci.org/Harut/chakert.svg?branch=master)](https://travis-ci.org/Harut/chakert)

Tool applying a set of common typography rules to the text:
non-breaking spaces, dashes and ellipsyses replacements, etc.


Tested under python 2.7 and 3.4.

## Usage

For html:

```python
from chakert import Typograph
markup = '<p><b>Typography</b> is the art and technique of arranging type.</p>'
result_markup = Typograph.typograph_html(markup)
```

For parsed lxml.html tree:

```python
from chakert import Typograph
from lxml import html
markup = '<p><b>Typography</b> is the art and technique of arranging type.</p>'
tree = html.fromstring(markup)
result_tree = Typograph.typograph_tree(tree)
```

For plain text:

```python
from chakert import Typograph
text = 'Typography is the art and technique of arranging type.'
result_text = Typograph.typograph_text(text)
```

## Replacement rules

The typograph parses given text and splits it into tokens. 
Each token is instance of `chakert.tokens.Token` subclass.
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
11. Два и более дефиса подряд заменяются на тире или минус так же, как одиночный дефис. Если ни одно правил не подходит, заменяются на длинное тире.
12. Две и более точки подряд заменяются на многоточие, если перед ними не стоит другой знак препинания (?.. , !.. , ?!.) (кавычки и запятые не в счёт).
13. Двойные кавычки (") заменяются на ёлочки («»). Если кавычка прилеплена к слову слева, то она считается открывающей, иначе — закрывающей.
14. Вложенные кавычки заменяются на двойные косые нижнюю и верхнюю („“).

### English

A set of rules for English language.

1. Non-breaking spaces after prepositions, conjunctions and articles.
2. Non-breaking space between month name and number of one or two digits.
3. If there are multiple spaces in line, they are merged into one.
4. If the hyphen is surrounded by spaces, it is replaced by em dash, and the space before is replaced y non-breaking space.
5. If the hyphen is surrounded by numbers, it is replaced by en dash.
6. Space + hyphen before a number is replaced by minus sign (−3 °C)
7. Two or more hyphens in a row are replaced as they are single hyphen. If any replacement rules do not match, they are replaced by em dash.
8. Exactly 3 points are replaced by ellipsys (it can be 4 points in line in English https://dl.dropboxusercontent.com/u/351006/ellipsis.png).
9. Double quotes (") are replaced by left and right double quotes.
10. Nested quotes are replaced to left and right single quotes.

## Adding own rules and languages

In contrast with regexp-based typography fixers, the key feature of chakert is readability of
rules and expected simplicity of adding new rules.

The library uses tokenizer, splitting given text to the tokens of various classes. Each token
class defines own replacement rules in `morph` method. In this method, it is allowed to iterate
over sibling nodes in forward and backward direction and perform simple text changing operations
through provied API: remove token, replace one token with another.

The only thing you should really carry about is to keep iterator state up-to date while removing
or adding a token. It may be useful to learn chakert implementation to understand how it works.

If you are ready to suggest new rules or new languages, but you're not sure if you can implement
them well, fill free to send pull requests with test cases!

General policy for rules included by default is that they should be appliable on any general text,
and they should not be complicated.



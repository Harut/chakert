# -*- coding: utf-8 -*-
from .base import BaseTests
from unittest import skip


class RuTests(BaseTests):

    lang = 'ru'

    # XXX cleanup tests

    def test_1(self):
        self.assertText(
            u'Кролики -  это   не только ценный мех, но и 3-4 кг ценного мяса',
            u'Кролики␣— это не␣только ценный мех, но␣и␣3\N{EN DASH}4 кг ценного мяса')

    def test_ellipsis(self):
        self.assertText(
            u'Если бы люди летали как птицы...',
            u'Если␣бы люди летали как птицы…')


    def test_ellipsis_combined(self):
        self.assertText(
            u'Да ладно?.. Что, правда?!. Ну дела!..',
            u'Да␣ладно?.. Что, правда?!. Ну␣дела!..')

    def test_ellipsis_dash(self):
        self.assertText(
            u'-Вы уверены?..- сказал Медведь.',
            u'—Вы уверены?..— сказал Медведь.')

        self.assertText(
            u'-Да...- сказали звери.',
            u'—Да…— сказали звери.')

        self.assertText(
            u'-Что?!.- возразил Лось.',
            u'—Что?!.— возразил Лось.')

    def test_dash_at_end(self):
        # no replacement
        self.assertText(u'Дар -', u'Дар -')

    def test_3(self):
        self.assertText(
            u'А в ответ ему: "Таити, Таити! Не были мы на вашем "Таити"!".',
            u'А␣в␣ответ ему: «Таити, Таити! Не␣были мы на␣вашем „Таити“!».')

    @skip('Not implemented')
    def test_3_1(self):
        self.assertText(
            u'А в ответ ему: «Таити, Таити! Не были мы на вашем «Таити»!».',
            u'А␣в␣ответ ему: «Таити, Таити! Не␣были мы на␣вашем „Таити“!».')

    def test_quote_start(self):
        self.assertText(
            u'"Тяжело было" - да',
            u'«Тяжело было»␣— да')

    def test_quote_in_braces(self):
        self.assertText(
            u'Спроси ("Тяжело было") - да',
            u'Спроси («Тяжело было»)␣— да')

    def test_4(self):
        self.assertText(
            u'Оно было светло-красного цвета и \N{RIGHT DOUBLE QUOTATION MARK}улыбалось" по-доброму.',
            u'Оно было светло-красного цвета и␣„улыбалось“ по=доброму.')

    def test_5(self):
        self.assertText(
            u'- Во-первых, 20 июня 2000 года был ненастный понедельник, - ответил он. '
                u'- Во-вторых, было уже поздно, а в-третьих, я уже был дома. '
                u'Вы меня кое-с-кем перепутали. Как-то так.',
            u'— Во=первых, 20␣июня 2000␣года был ненастный понедельник,␣— ответил он.␣'
                u'— Во=вторых, было уже поздно, а␣в=третьих, я уже был дома. '
                u'Вы меня кое=с=кем перепутали. Как=то так.')


    def test_6(self):
        self.assertText(
            u'Авторы: к.т.н. Петров, к.ф.-м.н. Иванов, д. х.  н. Васильев и т. д. и т. п.',
            u'Авторы: к.␣т.␣н. Петров, к.␣ф.␣=м.␣н. Иванов, д.␣х.␣н. Васильев и␣т.␣д. и␣т.␣п.')

    def test_minus(self):
        self.assertText(
            u'На улице -3 °C',
            u'На␣улице \N{MINUS SIGN}3 °C') # XXX nbsp before degree sign?

        self.assertText(
            u'-3 °C ночью',
            u'\N{MINUS SIGN}3 °C ночью') # XXX nbsp before degree sign?

    def test_double_hyphen(self):
        self.assertText(
            u'На улице -- мороз',
            u'На␣улице␣\N{EM DASH} мороз')

        self.assertText(
            u'На улице---мороз',
            u'На␣улице\N{EM DASH}мороз')

        # Check if all hyphen rules are applied on double hyphen
        self.assertText(
            u'На улице --3 °C',
            u'На␣улице \N{MINUS SIGN}3 °C')

    def test_normalize_whitespaces(self):
        self.assertText(
            # XXX the second case is disputed!
            u'Пробел\u00a0неразрывный,  два\u00a0\u00a0пробела, два\u00a0 разных',
            u'Пробел␣неразрывный, два пробела, два разных')

    def test_number_mark(self):
        self.assertHtml(
            u'№ 42',
            u'№␣42')

    def test_month(self):
        self.assertHtml(
            u'Поздравляю с 8 Марта!',
            u'Поздравляю с␣8␣Марта!')

    def test_line_breaks(self):
        def strip(txt):
            return '\n'.join([x.strip() for x in txt.strip().splitlines()])

        self.assertText(
            strip(u'''
            - Да!
            - Нет!

            Договориться они так и не сумели...
            '''),
            strip(u'''
            \N{EM DASH} Да!
            \N{EM DASH} Нет!

            Договориться они так и␣не␣сумели…
            '''),
            check_html=False)

        self.assertText(
            strip(u'''
            - Да!
            - Нет!
            '''),
            strip(u'''
            \N{EM DASH} Да!␣\N{EM DASH} Нет!
            '''),
            line_breaks=False)

    def test_block(self):
        self.assertHtml(
            u'<p>- Да!</p><p>- Нет!</p>',
            u'<p>— Да!</p><p>— Нет!</p>')

        self.assertHtml(
            u'<P>- Да!</P><P>- Нет!</P>',
            u'<p>— Да!</p><p>— Нет!</p>')

        self.assertHtml(
            u'- Да!<br>- Нет!',
            u'— Да!<br>— Нет!')

    def test_block_custom(self):
        self.assertHtml(
            u'<span>- Да!</span><span>- Нет!</span>',
            u'<span>— Да!</span><span>- Нет!</span>')

        self.assertHtml(
            u'<span>- Да!</span><span>- Нет!</span>',
            u'<span>— Да!</span><span>— Нет!</span>',
            block_tags=['span'])

    def test_nested_tags(self):
        self.assertHtml(
            u'<p><b>Ученье </b>- свет!</p>',
            u'<p><b>Ученье␣</b>— свет!</p>')

    def test_normalize_whitespaces_in_tags(self):
        self.assertHtml(
            u'<p><b>Неученье </b> - тьма!</p>',
            u'<p><b>Неученье</b>␣— тьма!</p>',
            u'<p><b>Неученье␣</b>— тьма!</p>')

    def test_normalize_whitespaces_in_tags2(self):
        self.assertHtml(
            u'<p><b>Неученье </b> <b>\u00a0</b> - тьма!</p>',
            u'<p><b>Неученье␣</b><b></b>— тьма!</p>')

    def test_ignored_default(self):
        self.assertHtml(
            u'Код <code>function("hello")</code> не выполняется',
            u'Код <code>function("hello")</code> не␣выполняется')

        self.assertHtml(
            u'Код <CODE>function("hello")</CODE> не выполняется',
            u'Код <code>function("hello")</code> не␣выполняется')

    def test_ignored_custom(self):
        self.assertHtml(
            u'Код <cite>function("hello")</cite> не выполняется',
            u'Код <cite>function("hello")</cite> не␣выполняется',
            ignored=['cite'])

    def test_ignored_whitespaces(self):
        self.assertHtml(
            u'Код <code>function("hello")</code>- не выполняется',
            u'Код <code>function("hello")</code>- не␣выполняется')

        self.assertHtml(
            u'Код <pre>function("hello")</pre>- не выполняется',
            u'Код <pre>function("hello")</pre>— не␣выполняется')

    def test_lang_switch(self):
        self.assertHtml(
            u'<p>A difference</p><p lang="en">A difference</p>',
            u'<p>A difference</p><p lang="en">A␣difference</p>')

        self.assertHtml(
            u'<p lang="en_US">A difference</p>',
            u'<p lang="en_US">A␣difference</p>')

    def test_comment(self):
        self.assertHtml(
            u'<p>А комментарии</p> <!-- не обрабатываются --> и хвост',
            u'<p>А␣комментарии</p> <!-- не обрабатываются --> и␣хвост')

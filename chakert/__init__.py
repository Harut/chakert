from .tokenizer import BaseTypograph
from .langs import rules_by_language


class Typograph(BaseTypograph):

    rules_by_language = rules_by_language

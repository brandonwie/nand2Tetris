import os
import sys


class JackTokenizer(object):
    """Handles the compiler's input
    - ignore white space
    - Advancing the input, one token at a time
    - Getting the value and type of current token
    """

    def __init__(self, jack_file_path):
        """Opens the input .jack file and gets ready to tokenize it

        @param
        - input file / stream
        """
        # open Jack file
        self.jack = open(jack_file_path, "r")

        # need current token and next token
        self.curr_token: str
        self.next_token: str
        # token type

    def initialize(self):
        # read line
        line = self.jack.readline()
        # strip line
        line.strip()
        if self.is_instruction(line):
            pass
        # if first index has '/', '*', or empty: comments

    def has_more_tokens(self):
        pass

    def advance(self):
        """Gets the next token from the input
        and makes it the current token

        NOTE: this method should be called
        only `if` `has_more_tokens == true`
        """

        pass

    def token_type(self):
        """Returns the type of the current token, as a constant

        @return
        - KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST
        """
        pass

    def is_instruction(self, line):
        first_char = line[0]
        return True if (first_char in ["/", "*", "\n"]) else False

    def get_next_token(self):
        self.jack.readline()

    def keyword_set(self):
        return set(
            [
                "class",
                "constructor",
                "function",
                "method",
                "field",
                "static",
                "var",
                "int",
                "char",
                "boolean",
                "void",
                "true",
                "false",
                "null",
                "this",
                "let",
                "do",
                "if",
                "else",
                "while",
                "return",
            ]
        )

    def symbol(self):
        return set(
            [
                "{",
                "}",
                "(",
                ")",
                "[",
                "]",
                ".",
                ",",
                ";",
                "+",
                "-",
                "*",
                "/",
                "&",
                "|",
                "<",
                ">",
                "=",
                "~",
            ]
        )

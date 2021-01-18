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
        self.initialize()
        self.keyword = self.keyword_set()
        self.symbol = self.symbol_set()

    def initialize(self):
        """Set first current and next token"""
        # read line
        line = self.jack.readline()
        # strip line
        line.strip()
        # read line until not comment
        while self.is_comment(line):
            line = self.jack.readline()
        # deal with comment after code
        line = line.split("//")[0].strip()

    def is_comment(self, line):
        first_char = line[0]
        # if first index has '/', '*', or is empty: comments
        return True if (first_char in ["/", "*", "\n"]) else False

    def get_next_token(self):
        self.jack.readline()

    # ANCHOR API
    def has_more_tokens(self):
        pass

    def advance(self):
        """Gets the next token from the input
        and makes it the current token

        NOTE: this method should be called
        only `if` `has_more_tokens == true`
        """
        if self.has_more_tokens() == True:
            self.curr_token = self.next_token

    def token_type(self):
        """Returns the type of the current token, as a constant

        @return
        - KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST
        """
        pass

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

    def symbol_set(self):
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

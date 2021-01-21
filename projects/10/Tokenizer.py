import os, re


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
        txml_file_path = jack_file_path.replace(".jack", "T.xml")
        self.txml = open(txml_file_path, "w")
        self.txml.write("<token>\n")
        # need current token and next token
        self.token_list: list
        self.curr_index: int
        self.curr_token: str
        self.next_token: str
        self.initialize()
        self.keyword: set = self.keyword_set()
        self.symbol: set = self.symbol_set()
        self.EOL = False

    def initialize(self):
        """Set first current and next token"""
        # read first line
        line = self.jack.readline()
        # strip line
        line.strip()
        # read line until not comment
        while self.is_comment(line):
            line = self.jack.readline()
        line = line.split("//")[0].strip()  # deal with comment after code

    # receive striped line and parse the line
    def process_line(self, line):
        self.token_list = self.line_to_tokens(line)
        enum = enumerate(self.token_list)
        while not self.EOL:
            self.advance(enum)

    def is_comment(self, line) -> bool:
        first_char = line[0]
        # if first index has '/' or is empty: comments
        return True if first_char in ["/", "*", "\n"] else False

    # ANCHOR API
    def has_more_tokens(self) -> bool:
        return self.EOL

    def line_to_tokens(self, line: str) -> list:
        """get whole line and parse it
        @param
        - line with no comment

        @return
        - array of tokens
        """
        regex = r"[_a-zA-Z]?[_a-zA-Z0-9]+|[0-9]+|[{}().,;+\-*/&|<>=~]|\".+\""
        return re.findall(regex, line)

    def advance(self, enum: enumerate):
        """Gets next token from the input and makes it the current token

        NOTE: this method should be called only `if` `has_more_tokens == true`
        """
        # use enumerate & next() to manually advance
        if self.has_more_tokens():
            try:
                (index, value) = next(enum)  # call next line
                self.curr_token = self.next_token
                token_type = self.token_type(self.curr_token)
                self.write(token_type, self.curr_token)
                self.next_token = value

            except:  # if no more next, declare "End Of Line"
                self.EOL = True

    def token_type(self, token: str) -> str:
        """Returns the type of the current token, as a constant

        @param
        - current token in current token array

        @return
        - KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST
        """
        if token in self.keyword:
            return "keyword"
        elif token in self.symbol:
            return "symbol"
        elif '"' in token:
            return "stringConstant"
        elif token.isnumeric():
            return "integerConstant"
        else:
            return "identifier"

    # write single token
    def write(self, type, token):
        self.txml.write(f"<{type}> {token} </{type}>\n")

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

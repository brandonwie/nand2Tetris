import re


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
        self.jack = open(jack_file_path, "r")  # read Jack file
        txml_file_path = jack_file_path.replace(".jack", "T.xml")
        self.txml = open(txml_file_path, "w")  # write txml file
        self.curr_tokens: list  # will be first mounted after calling advance()
        self.next_tokens: list  # will be first mounted after calling init()
        self.keyword: set = self.keyword_set()
        self.symbol: set = self.symbol_set()
        self.EOF = False
        self.init()

    def init(self):
        """load first line and parse it to tokens, mount it to next_tokens"""
        self.jack.seek(0)  # goto start
        # if you call advance(), becomes current line tokens
        self.load_next_line()

    #! Actual writing happens here
    def translate(self):
        self.txml.write("<tokens>\n")
        # has more tokens == more lines left
        while self.has_more_tokens:
            self.advance()  # mount curr_tokens from next_tokens
            for token in self.curr_tokens:  # write curr_tokens
                token_type = self.token_type(token)
                self.write(token_type, token)
            self.load_next_line()  # prepare next_tokens
        self.txml.write("</tokens>\n")

    # read a new line, parse it to tokens,
    # mount it to "next_tokens"
    def load_next_line(self):
        loaded = False
        while not loaded and self.has_more_tokens:
            current_position = self.jack.tell()
            line = self.jack.readline().strip()
            if not self.is_comment(line):
                # remove comments after code
                line = line.split("//")[0].strip()
                # mount next line tokens
                self.next_tokens = self.parse_line_to_tokens(line)
                loaded = True
            if current_position == self.jack.tell():
                self.EOF = True

    def is_comment(self, line) -> bool:
        # if first index has '/' or is empty: comments
        return True if len(line) > 0 and line[0] in ["/", "*", "\n"] else False

    # ANCHOR API
    @property
    def has_more_tokens(self) -> bool:
        return not self.EOF

    def parse_line_to_tokens(self, line: str) -> list:
        """get whole line and parse it
        @param
        - line with no comment

        @return
        - array of tokens
        """
        # custom made regex
        regex = r"[_a-zA-Z]?[_a-zA-Z0-9]+|[0-9]+|[\[\]{}().,;+\-*/&|<>=~]|\".+\""
        return re.findall(regex, line)

    def advance(self):
        """Gets next token from the input and makes it the current token

        NOTE: this method should be called only `if` `has_more_tokens == true`
        """
        self.curr_tokens = self.next_tokens

    def token_type(self, token: str) -> str:
        """Returns the type of the current token, as a constant

        @param
        - current token in current token array

        @return
        - KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST
        """
        # didn't use CAPITAL letters not to avoid verbose
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

    # API END

    # write single token
    def write(self, type, token):
        if token == "<":
            token = "&lt"
        if token == ">":
            token = "&gt"
        if token == "&":
            token = "&amp"
        if type == "stringConstant":
            token = token.replace('"', "")
        self.txml.write(f"<{type}> {token} </{type}>\n")

    def close(self):
        self.jack.close()
        self.txml.close()

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

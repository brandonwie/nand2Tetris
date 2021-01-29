import re
from typing import Iterable, Iterator

# ANCHOR RegEx
# positive lookahead/lookbehind: no character should found before/after the keyword
KEYWORD = r"(?<![\w])(class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)(?![\w])"
# Nothing special about symbols
SYMBOL = r"([{}()[\].,;+\-*/&|<>=~])"
# Match INT_CONST if no word character right before/after digits (*max num 32767 is not considered)
INT_CONST = r"(?<![\w])(\d+)(?![\w])"
# Any character between double quote: () <- automatically exclude double quotes
STRING_CONST = r'"([^\n]*)"'
# A sequence of letters, digits, and underscore not starting with a digit
IDENTIFIER = r"([_a-zA-Z]\w*)"

# leftmost checked first, so IDENTIFIER comes last
LEXICAL_ELEMENTS = f"{KEYWORD}|{SYMBOL}|{INT_CONST}|{STRING_CONST}|{IDENTIFIER}"
# the list below matches the order of LEXICAL_ELEMENTS above
LEXICAL_ELEMENTS_LIST = ["KEYWORD", "SYMBOL", "INT_CONST", "STRING_CONST", "IDENTIFIER"]

# ANCHOR Compile RegEx
LEXICAL_ELEMENTS_REGEX = re.compile(LEXICAL_ELEMENTS)
SINGLE_LINE_COMMENT_REGEX = re.compile(r"//.*")
MULTI_LINE_COMMENT_REGEX = re.compile(r"/\*.*?\*/", flags=re.DOTALL)


class JackTokenizer:
    """Handles the compiler's input
    - Parse all tokens one token at a time
    - Getting the value and type of current token
    """

    def __init__(self, jack_file_path):
        """Opens the input .jack file and gets ready to tokenize it

        @param
        - input file / stream
        """
        self.jack = open(jack_file_path, "r")  # open Jack file
        self.jack_file = self.jack.read()  # read whole file
        self.tokens = self.tokenize()  # all tokens
        self.next_token = self.tokens.pop(0)  # load first token in next_token

    # ANCHOR API
    def has_more_tokens(self):
        return bool(self.next_token)

    def advance(self):
        """Gets next token from the input and makes it the current token

        NOTE: this method should be called only `if` `has_more_tokens == true`
        """
        self.curr_token = self.next_token
        if len(self.tokens) > 0:
            self.next_token = self.tokens.pop(0)
        else:
            self.next_token = None

    def tokenize(self):
        """remove comments and tokenize whole file
        @return
        - tuple (token, type) of tokens
        """
        trimmed_file = self.remove_comments()
        #! IMPORTANT TO REMEMBER
        # NOTE re.findall() will return an array of all non-overlapping regex matches in the string. “Non-overlapping” means that the string is searched through from left to right, and the next match attempt starts beyond the previous match. If the regex contains one or more capturing groups, re.findall() returns an array of tuples, with each tuple containing text matched by all the capturing groups
        token_tuples = LEXICAL_ELEMENTS_REGEX.findall(trimmed_file)
        types = map(
            lambda token_tuple: LEXICAL_ELEMENTS_LIST[
                next(index for index, value in enumerate(token_tuple) if value)
            ],
            token_tuples,
        )
        tuples_to_tokens = map(
            lambda token: next(value for index, value in enumerate(token) if value),
            token_tuples,
        )
        # NOTE The zip() function returns a zip object, which is an iterator of tuples where the first item in each passed iterator is paired together, and then the second item in each passed iterator are paired together etc.
        token_type_tuples = zip(types, tuples_to_tokens)
        # Convert to list by unpacking
        return [*token_type_tuples]

    def remove_comments(self):
        remove_single_line_comments = re.sub(
            SINGLE_LINE_COMMENT_REGEX, "", self.jack_file
        )
        remove_multi_line_comments = re.sub(
            MULTI_LINE_COMMENT_REGEX, "", remove_single_line_comments
        )
        return remove_multi_line_comments

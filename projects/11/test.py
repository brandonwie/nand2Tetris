import re, itertools

f = open("ComplexArrays/Main.jack", "r")
file = f.read()
# Grouping RegExs
# positive lookahead/lookbehind: no character should found before/after the keyword

KEYWORD = "(?<![\w])(class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return)(?![\w])"
# Nothing special about symbols
SYMBOL = "([{}()[\].,;+\-*/&|<>=~])"
# Match INT_CONST if no word character right before/after digits
INT_CONST = "(?<![\w])(\d+)(?![\w])"
STRING_CONST = '"([^\n]*)"'
IDENTIFIER = "([A-Za-z_]\w*)"
# leftmost checked first, so IDENTIFIER comes last
LEXICAL_ELEMENTS = f"{KEYWORD}|{SYMBOL}|{INT_CONST}|{STRING_CONST}|{IDENTIFIER}"
LEXICAL_ELEMENTS_REGEX = re.compile(LEXICAL_ELEMENTS)
INLINE_COMMENT_REGEX = re.compile("//.*")
MULTILINE_COMMENT_REGEX = re.compile("/\*.*?\*/", flags=re.S)

# regex = r"[_a-zA-Z]?[\w]+|[0-9]+|[\[\]{}().,;+\-*/&|<>=~]|\".+\""
# reg_comment = r"^\/\/.*\n|\/\*.+\n|\*.*\n|\/\/.*"

removed1 = re.sub(MULTILINE_COMMENT_REGEX, "", file)
removed2 = re.sub(INLINE_COMMENT_REGEX, "", removed1)
tokens = LEXICAL_ELEMENTS_REGEX.findall(removed2)


ALL_TYPES = ["KEYWORD", "SYMBOL", "INT_CONST", "STRING_CONST", "IDENTIFIER"]

types = map(
    lambda type: ALL_TYPES[next(index for index, value in enumerate(type) if value)],
    tokens,
)

flat_matches = list(itertools.chain(*tokens))
# print(flat_matches)
tuples_to_tokens = map(
    lambda token: next(value for index, value in enumerate(token) if value), tokens
)
print(type(tuples_to_tokens))

token_list = [match for match in flat_matches if match]
result = [*zip(tuples_to_tokens, types)]
# for token, type in result:
#     print(token, type)
print(result)
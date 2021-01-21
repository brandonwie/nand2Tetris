import re


# class Test(object):
#     """
#     docstring
#     """

#     def __init__(self):
#         line = "constructor Square new(int Ax, int Ay, int Asize) {"
#         # there are three OR so it prints as tuples
#         regex = r"[a-zA-Z_]+|[0-9]+|[{}().,;+\-*/&|<>=~]"
#         token_array = re.findall(regex, line)
#         enum: enumerate = enumerate(token_array)
#         curr_index = 0

#     def advance(self, enum: enumerate) -> None:
#         (index, val) = next(enum)
#         self.curr_index = index
#         print(val)

#     # think about condition to make it stop
#     def get_tokens(self):
#         while self.curr_index < len(self.token_array):
#             self.advance(test_enum)


line = "constructor Square new(int Ax, int Ay, int Asize) { 52 + 3"

regex = r"[_a-zA-Z]?[_a-zA-Z0-9]+|[0-9]+|[{}().,;+\-*/&|<>=~]|\".+\""

token_array = re.findall(regex, line)

print(token_array)

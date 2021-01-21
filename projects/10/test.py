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

with open("text.txt", "r") as f:
    line = f.readline()
    arr = line.split(" ")
    enum = enumerate(arr)
    li1 = next(enum)
    print(li1)
    li2 = next(enum)
    print(li2)
    li3 = next(enum)
    print(li3)

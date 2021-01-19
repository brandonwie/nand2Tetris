import re

line = "constructor Square new(int Ax, int Ay, int Asize) {"
# there are three OR so it prints as tuples
regex = r"[a-zA-Z_]+|[0-9]+|[{}().,;+\-*/&|<>=~]"

result = re.findall(regex, line)

print(result)
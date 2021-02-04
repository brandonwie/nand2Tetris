# count = 0


# def divide(x, y):
#     global count
#     count += 1
#     print(f"loop count: {count}")
#     print(f"x: {x}, y: {y}")
#     if x < y:
#         print("reached bottom, return 0")
#         return 0  # return 0 when divider is greater than dividend
#     # ? escape the recursion if x < y
#     #! recursion
#     q = divide(x, 2 * y)  # quotient becomes the half of original q value
#     ####################### because divider is doubled
#     # ? reaches here if escaped,
#     print(f"x:{x} y:{y} quotient:{2*q}")
#     remainder = x - (2 * q) * y
#     quotient = 2 * q
#     print(f"if?: {x - quotient * y} < {y}")  # double q to compensate
#     if remainder < y:  # no more 'y' can be substracted
#         print(f"if(next Q val): {quotient}\n")
#         return quotient
#     else:  # one more 'y' can be substracted
#         print(f"else(next Q val): {quotient+1}\n")
#         return quotient + 1
#     # return values become the value of 'q'


# divide(589, 100)

x = 3
y = 20
twoToThe = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]

print(y & twoToThe[0] == 0)
print(y & twoToThe[1] == 0)
print(y & twoToThe[2] == 0)
print(y & twoToThe[3] == 0)
print(y & twoToThe[4] == 0)
print(y & twoToThe[5] == 0)
print(y & twoToThe[6] == 0)
print(y & twoToThe[7] == 0)
print(y & twoToThe[8] == 0)

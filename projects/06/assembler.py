import c_inst as C
import symbol as S
import os, sys


# remove comment and empty space from line
def trim(line):
    # ignore line breaks
    if line[0] == "\n":
        return ""
    # remove all white spaces
    trimmed = "".join(line.split())
    # ignore comments
    try:
        idx = trimmed.index("//")
        if trimmed[0] != "/":  # detect comments next to code
            return trimmed[:idx]
        else:  # otherwise full-line comments
            return ""
    except ValueError:
        return trimmed


# convert C instruction as (dest = comp ; jump)
def normalize(line):
    line = line.strip()
    if not ";" in line:  # e.g. D=M => D=M;null
        line = line + ";null"
    if not "=" in line:  # e.g. D;JMP => null=D;JMP
        line = "null=" + line
    return line


var_idx = 16  # next available memory location for variables

# add variables and return variable index
def add_var(label):
    global var_idx
    S.table[label] = var_idx
    var_idx += 1
    return S.table[label]


# convert A instructions: either [(TEMP) or @temp] or [@21]
def a_convert(line):
    if line[1].isalpha():  # (TEMP) or @temp
        label = line[
            1:-1
        ]  # remove paranthesis / also last letter of @tem'p' will be cut, but no need to worry since all values are treated the same
        var_idx = S.table.get(label, -1)  # find variable
        if var_idx == -1:  # don't exist?
            var_idx = add_var(label)  # add variable

    else:  # convert number to binary except line[0]
        var_idx = int(line[1:])
    bValue = bin(var_idx)[2:].zfill(16)
    return bValue


# convert C instructions:
def c_convert(line):
    line = normalize(line)  # normalize (dest=comp;jump)
    tmp = line.split("=")  # first dest vs rest
    dest = C.dest.get(tmp[0])
    tmp = tmp[1].split(";")  # second comp vs jump
    comp = C.comp.get(tmp[0])
    jump = C.jump.get(tmp[1])
    return comp, dest, jump


def translate(line):
    # distinguishes a- and c-instructions, calls appropriate function
    # to translate each
    if line[0] == "@":
        return a_convert(line)
    else:
        [comp, dest, jump] = c_convert(line)
        return "111" + comp + dest + jump


# First Pass: check symbols only
def first_pass():
    rf = open(path + ".asm")
    wf = open(path + ".tmp", "w")

    line_num = 0
    for li in rf:
        trim_li = trim(li)
        if len(trim_li) > 0:
            if trim_li[0] == "(":
                label = trim_li[1:-1]  # e.g. (TEST) => TEST
                S.table[label] = line_num
                trim_line = ""
            else:
                line_num += 1
                wf.write(trim_li + "\n")
    rf.close()


def assemble():
    # takes file stripped of labels and translates it into .hack
    rf = open(path + ".tmp")
    wf = open(path + ".hack", "w")

    for li in rf:
        trans_li = translate(li)
        wf.write(trans_li + "\n")

    rf.close()
    wf.close()
    os.remove(path + ".tmp")


path1 = "./add/Add"
path2 = "./max/Max"
path3 = "./rect/Rect"
path = "./pong/Pong"
first_pass()
assemble()
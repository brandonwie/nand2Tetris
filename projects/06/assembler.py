import c_instruction as Cinst
import symbol as Symbol
import re
import os, sys


# remove comment and empty space from line
def trim(line):
    # ignore line breaks
    if line[0] == "\n":
        return ""
    # remove all white spaces
    line = "".join(line.split())
    # ignore comments
    commentIndex = line.find("//")
    if commentIndex == -1:  # if no comment
        return line  # return line
    else:
        if commentIndex == 0:  # detect comments next to code
            return ""
        else:  # otherwise full-line comments
            return line[:commentIndex]


# convert C instruction as (dest = comp ; jump)
def normalize(line):
    line = line.strip()
    if not ";" in line:  # e.g. D=M => D=M;null
        line = line + ";null"
    if not "=" in line:  # e.g. D;JMP => null=D;JMP
        line = "null=" + line
    return line


# memory location for variabels starts from index 16
variableIndex = 16

# add variables and return address
def addVariable(label):
    """Add a label to the table

    Args:
        label (`str`)

    Returns:
        `address` of new label
    """
    global variableIndex
    Symbol.table[label] = variableIndex
    variableIndex += 1  # increase index for next var
    return Symbol.table[label]


# convert A instructions: either @tmp or @TEMP or @21
def convertA(line):
    """Convert A instruction into binary or add variable

    Args:
        line (`str`)

    Returns:
        `binary code`
    """
    if line[1].isalpha():  # @temp or @R0
        removeSigns = re.search(r"[^\@\ ]+", line)
        var = removeSigns.group(0)  # remove parenthesis
        # Find address in Symbol table
        varAddress = Symbol.table.get(var, -1)

        if varAddress == -1:  # if NOT found
            varAddress = addVariable(var)  # add variable

    else:  # convert number to binary except first digit
        varAddress = int(line[1:])  # @3 => 3

    numToBinary = bin(varAddress)[2:].zfill(16)  # 3 => 0000000000000011
    return numToBinary


# convert C instructions
def convertC(line):
    """Slice C instruction into 3 pieces

    Args:
        line (`str`)

    Returns:
        `[comp, dest, jump]`
    """
    line = normalize(line)  # normalize (dest=comp;jump)
    tmp = line.split("=")  # first dest vs rest
    dest = Cinst.destination.get(tmp[0])
    tmp = tmp[1].split(";")  # second comp vs jump
    comp = Cinst.computation.get(tmp[0])
    jump = Cinst.jump.get(tmp[1])
    return "111" + comp + dest + jump


def translate(line):
    """Translate line to either A or C"""
    line = line.rstrip()  # strip \n
    if line[0] == "@":
        return convertA(line)
    else:
        return convertC(line)


# First Pass: check symbols only
def firstPass():
    """Trim assembly codes and register labels"""
    loadFile = open(path + ".asm")
    writeFile = open(path + ".tmp", "w")

    line_num = 0
    for li in loadFile:
        line = trim(li)  # remove comment,whitespace
        if len(line) > 0:  # if NOT empty line
            if line[0] == "(":  # if LABEL
                label = line[1:-1]  # e.g. (TEST) => TEST
                Symbol.table[label] = line_num  # set the line number to table
                continue  # move on to the next line
            else:  # if NOT label,
                line_num += 1  # increse line num only
                writeFile.write(line + "\n")  # write the line
    loadFile.close()


def assemble():
    loadFile = open(path + ".tmp")
    writeFile = open(path + ".hack", "w")

    for li in loadFile:
        line = translate(li)
        writeFile.write(line + "\n")

    loadFile.close()
    writeFile.close()
    # os.remove(path + ".tmp") # remove temp file


# Change path# of file you want to assemble
# as 'path' and this program will run with the file
path1 = "./add/Add"
path2 = "./max/Max"
path3 = "./rect/Rect"
path4 = "./pong/Pong"

firstPass()
assemble()

print(Symbol.table)
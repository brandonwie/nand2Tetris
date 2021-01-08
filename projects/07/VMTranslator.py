import os

COMMENT = "//"


class Parser(object):
    def __init__(self, vm_filename):
        self.vm_filename = vm_filename
        self.vm = open(vm_filename, "r")  # read file
        self.commands = self.commands_dict()  # load
        self.curr_instructions = None
        self.initialize()

    def initialize(self):
        line = self.vm.readline().strip()
        while not self.is_command(line):
            # read first line until there's no command
            line = self.vm.readline().strip()
        self.load_next_instruction(line)

    def load_next_instruction(self, line=None):
        # if line is not null keep it, else read new line
        line = line if line is not None else self.vm.readline().strip()
        # set next_instruction
        # including lines of codes with comments
        self.next_instruction = line.split(COMMENT)[0].strip().split()

    def is_command(self, line):
        return line and not COMMENT in line

    def get_command(self, n):
        if len(self.curr_instructions) >= n + 1:
            return self.curr_instructions[n]
        return None

    # Proposed Interface
    def advance(self):
        self.curr_instructions = self.next_instruction
        self.load_next_instruction()

    @property
    def has_more_command(self):
        return bool(self.next_instruction)

    @property
    def command_type(self):
        return self.commands.get(self.curr_instructions[0].lower())

    @property
    def arg1(self):
        if self.command_type == "C_ARITHMETIC":
            return self.get_command(0)
        return self.get_command(1)

    @property
    def arg2(self):
        return self.get_command(2)

    # Interface END

    def commands_dict(self):
        return {
            "add": "C_ARITHMETIC",
            "sub": "C_ARITHMETIC",
            "neg": "C_ARITHMETIC",
            "eq": "C_ARITHMETIC",
            "gt": "C_ARITHMETIC",
            "lt": "C_ARITHMETIC",
            "and": "C_ARITHMETIC",
            "or": "C_ARITHMETIC",
            "not": "C_ARITHMETIC",
            "push": "C_PUSH",
            "pop": "C_POP",
            "label": "C_LABEL",
            "goto": "C_GOTO",
            "if-goto": "C_IF",
            "function": "C_FUNCTION",
            "return": "C_RETURN",
            "call": "C_CALL",
        }


class CodeWriter(object):
    def __init__(self, asm_filename):
        self.asm = open(asm_filename, "w")
        self.curr_file = None  # to use as Label
        self.bool_count = 0  # to use as Label
        self.addresses = self.address_dict()

    def set_file_name(self, vm_filename):
        """Set file name as pointer"""
        self.curr_file = vm_filename.replace(".vm", "").split("/")[-1]

    def write_arithmetic(self, operation):
        """Apply operation to top of stack"""
        if operation not in ["neg", "not"]:  # Binary operator
            self.pop_stack_to_D()
        self.SP_decrement()
        self.A_is_RAM_SP()

        if operation == "add":  # Arithmetic operators
            self.write("M=M+D")
        elif operation == "sub":
            self.write("M=M-D")
        elif operation == "or":
            self.write("M=M|D")
        elif operation == "neg":
            self.write("M=-M")
        elif operation == "not":
            self.write("M=!M")
        elif operation == "and":
            self.write("M=M&D")

        elif operation in ["eq", "gt", "lt"]:  # Boolean operators
            self.write("D=M-D")
            self.write("@BOOL{}".format(self.bool_count))

            if operation == "eq":
                self.write("D;JEQ")  # if x == y, x - y == 0
            elif operation == "gt":
                self.write("D;JGT")  # if x > y, x - y > 0
            elif operation == "lt":
                self.write("D;JLT")  # if x < y, x - y < 0

            self.A_is_RAM_SP()
            self.write("M=0")  # False
            self.write("@ENDBOOL{}".format(self.bool_count))
            self.write("0;JMP")

            self.write("(BOOL{})".format(self.bool_count))
            self.A_is_RAM_SP()
            self.write("M=-1")  # True

            self.write("(ENDBOOL{})".format(self.bool_count))
            self.bool_count += 1
        else:
            self.raise_unknown(operation)
        self.SP_increment()

    def write_push_pop(self, command, segment, index):
        self.resolve_address(segment, index)
        if command == "C_PUSH":  # load M[address] to D
            if segment == "constant":
                self.write("D=A")  #   assign value to D
            else:
                self.write("D=M")  #   assign memory address to D
            self.push_D_to_stack()
        elif command == "C_POP":  # load D to M[address]
            self.write("D=A")
            self.write("@R13")  # Store resolved address in R13
            self.write("M=D")
            self.pop_stack_to_D()
            self.write("@R13")
            self.write("A=M")
            self.write("M=D")
        else:
            self.raise_unknown(command)

    # Interface END

    def write(self, command):
        self.asm.write(command + "\n")

    def raise_unknown(self, argument):
        raise ValueError("{} is an invalid argument".format(argument))

    def resolve_address(self, segment, i):
        """Resolve address to A register"""
        address = self.addresses.get(segment)
        if segment == "constant":
            self.write("@" + str(i))
        elif segment == "static":
            self.write("@" + self.curr_file + "." + str(i))  # @Foo.i
        elif segment in ["pointer", "temp"]:
            self.write("@R" + str(address + int(i)))  # integer only
        elif segment in ["local", "argument", "this", "that"]:
            self.write("@" + address)  # string only
            self.write("D=M")  # D = RAM[segmentPointer]
            self.write("@" + str(i))
            self.write("A=D+A")  # addr = RAM[segmentPointer + i]
        else:
            self.raise_unknown(segment)

    def address_dict(self):
        return {
            "local": "LCL",  # R1
            "argument": "ARG",  # R2
            "this": "THIS",  # R3
            "that": "THAT",  # R4
            "pointer": 3,  # 3+0 = R3(this), 3+1 = R4(that)
            "temp": 5,  # R5-R12
            # R13-R15 empty
            "static": 16,  # R16-255
        }

    def push_D_to_stack(self):
        """Push from D onto top of stack, increment SP
        D=A(constant) or D=M(local, argument, this, that)
        """
        self.write("@SP")
        self.write("A=M")  # Set address to current stack pointer
        self.write("M=D")
        self.write("@SP")
        self.write("M=M+1")  # Increment SP

    def pop_stack_to_D(self):
        """Decrement @SP, pop from top of stack onto D"""
        self.write("@SP")
        self.write("M=M-1")  # Decrement SP
        self.write("A=M")  # Set address to current stack pointer
        self.write("D=M")

    def SP_increment(self):
        self.write("@SP")
        self.write("M=M+1")

    def SP_decrement(self):
        self.write("@SP")
        self.write("M=M-1")

    def A_is_RAM_SP(self):
        self.write("@SP")
        self.write("A=M")


class Main(object):
    def __init__(self, file_name):
        self.convert_file_extension(file_name)
        self.vm_file = file_name
        self.cw = CodeWriter(self.asm_file)
        self.translate(self.vm_file)

    def convert_file_extension(self, file_path):
        asm_convert = file_path.replace(".vm", ".asm")
        self.asm_file = asm_convert

    def translate(self, vm_file):
        parser = Parser(vm_file)
        self.cw.set_file_name(vm_file)
        while parser.has_more_command:
            parser.advance()
            self.cw.write("// " + " ".join(parser.curr_instructions))
            if parser.command_type == "C_PUSH":
                self.cw.write_push_pop("C_PUSH", parser.arg1, parser.arg2)
            elif parser.command_type == "C_ARITHMETIC":
                self.cw.write_arithmetic(parser.arg1)
            elif parser.command_type == "C_POP":
                self.cw.write_push_pop("C_POP", parser.arg1, parser.arg2)
        # close writing
        self.cw.asm.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise Exception("you must enter a file name")
    else:
        file_name = sys.argv[1]
    Main(file_name)
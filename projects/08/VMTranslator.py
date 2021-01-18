import os

# comment symbol
COMMENT = "//"

# ANCHOR class Parser
class Parser:
    """parse a file, segregate operations per line
    - parsed line will be loaded into class `CodeWriter`

    @param `path_to_vm_file` full path to vm file
    """

    def __init__(self, vm_file_path):
        """
        EOF - end of file
        """
        self.vm = open(vm_file_path, "r")
        self.EOF = False
        self.commands = self.commands_dict()
        self.curr_instruction = []
        self.initialize_file()

    # API
    # NOTE advace() must be called once
    # before start translating since curr_instruction is None
    def advance(self):
        """
        - assign current instruction to next instruction
        - load next instruction
        """
        self.curr_instruction = self.next_instruction
        self.load_next_instruction()

    @property
    def has_more_commands(self):
        return not self.EOF

    @property
    def command_type(self):
        """check first element of current instruction
        - Arithmetic type: add, sub, neg, ...
        - Else: push, pop, goto, if, ...
        """
        return self.commands.get(self.curr_instruction[0].lower())

    @property
    def arg1(self):
        """process an argument - segments OR arithmetic operators
        - if `operator` - (e.g.) `add` :return - `arg(0)`
        - if `segment` - (e.g.) `push local 0` :return - `arg(1)`
        """
        if self.command_type == "C_ARITHMETIC":
            return self.argc(0)
        return self.argc(1)

    @property
    def arg2(self):
        """emit `int` part of instruction
        - only used if, `PUSH`, `POP`, `FUNCTION`, `CALL`
        """
        return self.argc(2)

    # API END

    def initialize_file(self):
        self.vm.seek(0)  # goto first
        self.load_next_instruction()

    def load_next_instruction(self):
        loaded = False
        while not loaded and not self.EOF:
            current_position = self.vm.tell()
            line = self.vm.readline().strip()
            if self.is_instruction(line):
                self.next_instruction = line.split(COMMENT)[0].strip().split()
                loaded = True
            # EOF if readline() doesn't change current position
            if current_position == self.vm.tell():
                self.EOF = True

    def is_instruction(self, line):
        """arg `line is already stripped"""
        return len(line) > 0 and not line.startswith(COMMENT)

    def argc(self, n):
        """retrieve an argument from instruction at position `n`"""
        return self.curr_instruction[n]

    # close opened file
    def close(self):
        self.vm.close()

    # commands with types
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


# ANCHOR
class CodeWriter:
    def __init__(self, asm_filename):
        self.asm = open(asm_filename, "w")
        self.addresses = self.address_dict()
        # variables for unique address
        self.curr_file = None  # for `Foo.i` format
        self.bool_count = 0
        self.call_count = 0

    # ANCHOR API
    def write_init(self):
        self.write("// Bootstrap code")
        self.write("@256")
        self.write("D=A")
        self.write("@SP")
        self.write("M=D")
        self.write("// call Sys.init")
        self.write_call("Sys.init", 0)
        # self.write('@Sys.init')
        # self.write('0;JMP')

    # NOTE it should be executed before start writing a new file
    # to give distinctive label
    def set_file_name(self, vm_filename):
        """distinctive label
        - `if-goto`, `goto`, `label`,
        - `static`: Foo.i
        """
        # get current file name
        self.curr_file = vm_filename.replace(".vm", "").split("/")[-1]
        # comment the file name on every start
        self.write(f"// Translate {self.curr_file}.vm")

    def write_arithmetic(self, operation):
        """Apply operation to top of stack"""
        if operation not in ["neg", "not"]:  # Binary operator
            self.pop_stack_to_D()  # SP--, D=*SP(n-1) (prev value)

        self.decrement_SP()  # SP--
        self.set_A_to_stack()  # A=*SP(n-2) (prev-prev value) => M
        # NOTE at this point, if not 'neg' or 'not' operation,
        # D holds X2 value address
        # A holds X1 value address (refer to M(right-side) below)
        # now you have 2 values to
        if operation == "add":  # Arithmetic operators
            self.write("M=M+D")
        elif operation == "sub":
            self.write("M=M-D")
        elif operation == "and":
            self.write("M=M&D")
        elif operation == "or":
            self.write("M=M|D")
        elif operation == "neg":
            self.write("M=-M")
        elif operation == "not":
            self.write("M=!M")
        elif operation in ["eq", "gt", "lt"]:  # Boolean operators
            self.write("D=M-D")
            self.write(f"@BOOL.{self.bool_count}")
            # if True, goto (BOOL.i label)
            if operation == "eq":
                self.write("D;JEQ")  # if X1==X2, X1-X2=0
            elif operation == "gt":
                self.write("D;JGT")  # if X1>X2, X1-X2>0
            elif operation == "lt":
                self.write("D;JLT")  # if X1<X2, X1-X2<0

            self.set_A_to_stack()
            self.write("M=0")  # False, *SP=0 (000000000000)
            # goto (ENDBOOL.i label)
            self.write(f"@END_BOOL.{self.bool_count}")
            self.write("0;JMP")
            # (BOOL.i label)
            self.write(f"(BOOL.{self.bool_count})")
            self.set_A_to_stack()  # set value to SP
            self.write("M=-1")  # True, *SP=-1 (111111111111)
            # (ENDBOOL.i label)
            self.write(f"(END_BOOL.{self.bool_count})")
            self.bool_count += 1
        else:
            self.raise_unknown(operation)
        self.increment_SP()

    def write_push_pop(self, command, segment, index):
        # Set address or value(iff constant) to A
        self.resolve_address(segment, index)
        # NOTE now @val,@addr are available with A register(right-side)

        # PUSH constant or *segment to SP
        if command == "C_PUSH":
            if segment == "constant":  # value
                self.write("D=A")
            else:
                self.write("D=M")  # segment address
            self.push_D_to_stack()
        # POP from SP to segment
        elif command == "C_POP":
            self.write("D=A")  # D = seg_addr
            self.write("@R13")  # Store resolved address in R13
            self.write("M=D")  # *R13 = seg_addr
            self.pop_stack_to_D()  # SP--, D = *SP(previously pushed value)
            self.write("@R13")
            self.write("A=M")  # pointer
            self.write("M=D")  # *(*R13) = *seg_addr = *SP // assigned to segment
        else:
            self.raise_unknown(command)

    def write_label(self, label):
        self.write(f"({self.curr_file}${label})")

    def write_goto(self, label):
        self.write(f"@{self.curr_file}${label}")
        self.write("0;JMP")

    def write_if(self, label):
        self.pop_stack_to_D()  # push processed result to D
        self.write(f"@{self.curr_file}${label}")
        self.write("D;JNE")  # if D!=0 (True=-1), JUMP to label
        # because if D=0, it means False

    def write_call(self, function_name, num_args):
        # set return-address: functionName$ret.i
        return_address = f"{function_name}$ret.{str(self.call_count)}"

        # 1. push return-address
        self.write(f"@{return_address}")
        self.write("D=A")
        self.push_D_to_stack()

        # 2. push LCL, ARG, THIS, THAT
        for address in ["@LCL", "@ARG", "@THIS", "@THAT"]:
            self.write(address)
            self.write("D=M")
            self.push_D_to_stack()

        # 3. Reposition *ARG = *SP-n-5 = *SP-(n+5)
        # NOTE nothing to do with SP,
        # so this block can come after LCL=SP command block
        self.write("@SP")
        self.write("A=M")  # A = *SP
        self.write("D=A")  # assign value to D
        self.write(f"@{str(5 + num_args)}")
        self.write("D=D-A")  # D = SP-(n+5)
        self.write("@ARG")
        self.write("M=D")  # *ARG = D

        # 4. LCL = SP
        self.write("@SP")
        self.write("D=M")
        self.write("@LCL")
        self.write("M=D")

        # 5. goto function
        self.write(f"@{function_name}")
        self.write("0;JMP")

        # 6. Declare a label for the (return_address)
        self.write(f"({return_address})")

        # increment call count
        self.call_count += 1

    def write_function(self, function_name, num_locals):
        self.write(f"({function_name})")

        # push local variables N(number of local vars) times
        for i in range(num_locals):
            self.write("D=0")  # set to 0
            self.push_D_to_stack()

    def write_return(self):
        # Temporary variables
        endFrame = "R13"
        retAddr = "R14"

        # endFrame = LCL
        self.write("@LCL")
        self.write("D=M")
        self.write(f"@{endFrame}")
        self.write("M=D")

        # retAddr = *(endFrame-5)
        self.write(f"@{endFrame}")
        self.write("D=M")  # D = endFrame
        self.write("@5")
        self.write("D=D-A")  # D = endFrame - 5
        self.write("A=D")  # A = endFrame - 5 (empty D)
        self.write("D=M")  # D = *(endFrame - 5)
        self.write(f"@{retAddr}")
        self.write("M=D")  # retAddr = D

        # *ARG = pop()
        self.pop_stack_to_D()
        self.write("@ARG")
        self.write("A=M")
        self.write("M=D")

        # SP = ARG+1
        self.write("@ARG")
        self.write("D=M")
        self.write("@SP")
        self.write("M=D+1")

        # THAT = *(endFrame-1)
        # THIS = *(endFrame-2)
        # ARG = *(endFrame-3)
        # LCL = *(endFrame-4)
        dist = 1
        for address in ["@THAT", "@THIS", "@ARG", "@LCL"]:
            self.write(f"@{endFrame}")
            self.write("D=M")  # D = endFrame
            self.write(f"@{str(dist)}")
            self.write("D=D-A")  # D = endFrame - dist
            self.write("A=D")  # A = endFrame - dist
            self.write("D=M")  # D = *(endFrame-dist)
            self.write(address)
            self.write("M=D")  # Segment =  *(endFrame-dist)
            dist += 1

        # goto retAddr
        self.write(f"@{retAddr}")
        self.write("A=M")
        self.write("0;JMP")

    # API END

    # NOTE Core function
    def write(self, command):
        self.asm.write(command + "\n")

    def close(self):
        self.asm.close()

    def raise_unknown(self, arg):
        raise ValueError(f"{arg} is an invalid argument")

    def resolve_address(self, segment, index):
        """Return address to A register"""
        address = self.addresses.get(segment)
        if segment == "constant":
            self.write(f"@{str(index)}")
        elif segment == "static":
            self.write(f"@{self.curr_file}.{str(index)}")  # Foo.i
        elif segment in ["pointer", "temp"]:
            self.write(f"@R{str(address + index)}")  # Address is an int
        elif segment in ["local", "argument", "this", "that"]:
            self.write(f"@{address}")  # *segment
            self.write("D=M")
            self.write(f"@{str(index)}")  # index within the segment
            self.write("A=D+A")  # A = *(segment base + index)
        else:
            self.raise_unknown(segment)

    def address_dict(self):
        return {
            # NOTE LCL, ARG, THIS and THAT are holding base address
            "local": "LCL",  # R1
            "argument": "ARG",  # R2
            "this": "THIS",  # R3
            "that": "THAT",  # R4
            # pointer 0 = 3+0 = 3 == THIS
            # pointer 1 = 3+1 = 4 == THAT
            "pointer": 3,
            "temp": 5,  # R5-R12
            # R13-R15 are free
            "static": 16,  # R16-R255
        }

    def push_D_to_stack(self):
        """Push from D onto top of stack, increment @SP"""
        self.write("@SP")  # Get current stack pointer
        self.write("A=M")  # A = *SP
        self.write("M=D")  # Write data to top of stack
        self.increment_SP()

    def pop_stack_to_D(self):
        """Decrement @SP, pop from top of stack onto D"""
        self.decrement_SP()
        self.write("A=M")  # Set address to current stack pointer
        self.write("D=M")  # Get data from top of stack

    def decrement_SP(self):
        self.write("@SP")
        self.write("M=M-1")

    def increment_SP(self):
        self.write("@SP")
        self.write("M=M+1")

    def set_A_to_stack(self):
        self.write("@SP")
        self.write("A=M")


# ANCHOR Main
class Main:
    def __init__(self, file_path):
        self.parse_argv(file_path)
        self.cw = CodeWriter(self.asm_file)
        # NOTE if array "vm_files" has "Main.vm":
        #         init Bootstrap + call Sys.init
        # Simplified due to some reasons (according to moderator)
        if len(self.vm_files) > 1:
            self.cw.write_init()
        for vm_file in self.vm_files:
            self.translate(vm_file)
        # close CodeWriter
        self.cw.close()

    def parse_argv(self, file_path):
        """search the tree top-down,
        :param
        :set `vm_files` and `asm_file`
        """
        path = os.getcwd()
        if ".vm" in file_path:
            file_name = file_path
            for dirpath, dirnames, filenames in os.walk(path):
                if file_name in filenames:
                    vm_file = f"{dirpath}/{file_name}"
                    self.vm_files = [vm_file]
                    self.asm_file = vm_file.replace(".vm", ".asm")
        else:
            dir_name = file_path
            for dirpath, dirnames, filenames in os.walk(path):
                if dir_name == dirpath.split("/")[-1]:
                    self.asm_file = f"{dirpath}/{dir_name}.asm"
                    vm_files = filter(lambda x: ".vm" in x, filenames)
                    self.vm_files = [dirpath + "/" + vm for vm in vm_files]

    def translate(self, vm_file):
        parser = Parser(vm_file)
        self.cw.set_file_name(vm_file)
        while parser.has_more_commands:
            parser.advance()
            self.cw.write("// " + " ".join(parser.curr_instruction))
            if parser.command_type == "C_PUSH":
                self.cw.write_push_pop("C_PUSH", parser.arg1, int(parser.arg2))
            elif parser.command_type == "C_POP":
                self.cw.write_push_pop("C_POP", parser.arg1, int(parser.arg2))
            elif parser.command_type == "C_ARITHMETIC":
                self.cw.write_arithmetic(parser.arg1)
            elif parser.command_type == "C_LABEL":
                self.cw.write_label(parser.arg1)
            elif parser.command_type == "C_GOTO":
                self.cw.write_goto(parser.arg1)
            elif parser.command_type == "C_IF":
                self.cw.write_if(parser.arg1)
            elif parser.command_type == "C_FUNCTION":
                self.cw.write_function(parser.arg1, int(parser.arg2))
            elif parser.command_type == "C_CALL":
                self.cw.write_call(parser.arg1, int(parser.arg2))
            elif parser.command_type == "C_RETURN":
                self.cw.write_return()
        # close parser
        parser.close()


if __name__ == "__main__":
    import sys

    file_path = sys.argv[1]
    Main(file_path)
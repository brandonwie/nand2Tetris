class VMWriter:
    def __init__(self, file_path: str):
        """Creates a new output .vm file and prepares it for writing

        Args:
            txml_path (str): path for .vm file
        """
        vm_file = file_path.replace(".jack", ".vm")
        self.vm = open(vm_file, "w")

    def write_push(self, segment, index):
        """Writes a VM push command

        Args:
            segment (str): CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
            index (int)
        """
        if segment == "CONST":
            self.vm.write(f"push constant {index}")
        elif segment == "ARG":
            self.vm.write(f"push argument {index}")
        else:
            self.vm.write(f"push {segment.lower()} {index}")

    def write_pop(self, segment, index):
        """Writes a VM pop command

        Args:
            segment (str): CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
            index (int)
        """
        if segment == "CONST":
            self.vm.write(f"pop constant {index}")
        elif segment == "ARG":
            self.vm.write(f"pop argument {index}")
        else:
            self.vm.write(f"pop {segment.lower()} {index}")

    def write_arithmetic(self, command):
        """Writes a VM arithmetic-logical command

        Args:
            command (str): ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT
        """
        self.vm.write(f"{command.lower()}")

    def write_label(self, label):
        self.vm.write(f"label {label}")

    def write_goto(self, label):
        self.vm.write(f"goto {label}")

    def write_if(self, label):
        self.vm.write(f"if-goto {label}")

    def write_call(self, name, num_args):
        self.vm.write(f"call {name} {num_args}")

    def write_function(self, name, num_locals):
        self.vm.write(f"function {name} {num_locals}")

    def write_return(self):
        self.vm.write("return")

    def write_anything(self, any):
        self.vm.write(any)

    def close(self):
        self.vm.close()

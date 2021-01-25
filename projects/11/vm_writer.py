class VMWriter:
    def __init__(self, txml_path: str):
        vm_file = txml_path.replace("T.xml", ".vm")
        self.vm = open(vm_file, "w")

    def write_push(self, segment: str, index: int):
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

    def write_pop(self, segment: str, index: int):
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

    def write_arithmetic(self, command: str):
        """Writes a VM arithmetic-logical command

        Args:
            command (str): ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT
        """
        self.vm.write(f"{command.lower()}")

    def write_label(self, label: str):
        self.vm.write(f"label {label}")

    def write_goto(self, label: str):
        self.vm.write(f"goto {label}")

    def write_if(self, label: str):
        self.vm.write(f"if-goto {label}")

    def write_call(self, name: str, num_args: int):
        self.vm.write(f"call {name} {num_args}")

    def write_function(self, name: str, num_locals: int):
        self.vm.write(f"function {name} {num_locals}")

    def write_return(self):
        self.vm.write("return")
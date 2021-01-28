class SymbolTable:
    # STATIC and FIELD have a class scope
    # ARG and VAR have a subroutine scope
    counts = {"STATIC": 0, "FIELD": 0, "ARG": 0, "VAR": 0}

    def __init__(self):
        # Create a new symbol table
        self.class_scope = {}
        self.subroutine = {}

    def start_subroutine(self):
        """Starts a new subroutine scope (reset symbol table)"""
        # clean subroutine table
        self.subroutine.clear()
        # reset subroutine counts
        self.counts["ARG"] = 0
        self.counts["VAR"] = 0

    def define(self, name, type, kind):
        """Defines a new identifier of the given name, type, and kind
        and assigns it a running index
        """
        index = self.counts[kind]  # get current index of kind
        self.counts[kind] += 1  # increase index of the kind
        if kind in ["STATIC", "FIELD"]:
            self.class_scope[name] = (type, kind, index)
        elif kind in ["ARG", "VAR"]:
            self.subroutine[name] = (type, kind, index)

    def kind_of(self, name):
        if name in self.class_scope.keys():
            return self.class_scope[name][1]
        elif name in self.subroutine.keys():
            return self.subroutine[name][0]
        else:
            return "NONE"

    def type_of(self, name):
        if name in self.class_scope.keys():
            return self.class_scope[name][0]
        elif name in self.subroutine.keys():
            return self.subroutine[name][0]
        else:
            return "NONE"

    def index_of(self, name):
        if name in self.class_scope.keys():
            return self.class_scope[name][2]
        elif name in self.subroutine.keys():
            return self.subroutine[name][2]
        else:
            return "NONE"

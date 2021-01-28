from symbol_table import SymbolTable
from jack_tokenizer import JackTokenizer
from vm_writer import VMWriter

CONVERT_KIND = {"ARG": "ARG", "STATIC": "STATIC", "VAR": "VAR", "FIELD": "THIS"}

ARITHMETIC = {
    "+": "ADD",
    "-": "SUB",
    "=": "EQ",
    ">": "GT",
    "<": "LT",
    "&": "AND",
    "|": "OR",
}

ARITHMETIC_UNARY = {"-": "NEG", "~": "NOT"}


class CompilationEngine:
    """NOTE remember that "is_xxx()" checks on the next token,
    and load the next token to curr_token before starting sub-methods
    using "load_next_token()" and you can use values with it
    """

    def __init__(self, jack_file):
        self.vm_writer = VMWriter(jack_file)
        self.tokenizer = JackTokenizer(jack_file)
        self.symbol_table = SymbolTable()
        self.queue = []

    # 'class' className '{' classVarDec* subroutineDec* '}'
    def compile_class(self):
        #! Beginning of all
        # * save name of the class and move on
        self.load_next_token()  # 'class'
        self.class_name = self.load_next_token()  # className
        self.load_next_token()  # curr_token = '{'

        # if next token == 'static' or 'field',
        while self.is_class_var_dec():  # check next token
            self.compile_class_var_dec()  # classVarDec*
        while self.is_subroutine_dec():
            self.compile_subroutine()  # subroutineDec*
        self.vm_writer.close()

    # ('static' | 'field' ) type varName (',' varName)* ';'
    def compile_class_var_dec(self):
        kind = self.load_next_token()  # curr_token = static | field
        type = self.load_next_token()  # curr_token = type
        name = self.load_next_token()  # curr_token = varName
        self.symbol_table.define(name, type, kind.upper())
        while self.check_next_token() != ";":  # (',' varName)*
            self.load_next_token()  # ','
            name = self.load_next_token()  # varName
            self.symbol_table.define(name, type, kind.upper())
        self.load_next_token()  # ';'
        # next_token = 'constructor' | 'function' | 'method'

    # subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
    # subroutineBody: '{' varDec* statements '}'
    # TODO
    def compile_subroutine(self):
        subroutine_kind = (
            self.load_next_token()
        )  # ('constructor' | 'function' | 'method')
        self.load_next_token()  # ('void' | type)
        subroutine_name = self.load_next_token()  # subroutineName

        self.symbol_table.start_subroutine()  # init subroutine table
        if subroutine_kind == "method":
            self.symbol_table.define("instance", self.class_name, "ARG")

        self.load_next_token()  # curr_token '('
        self.compile_parameter_list()  # parameterList
        # next_token == ')' when escaped
        self.load_next_token()  # ')'
        self.load_next_token()  # '{'
        while self.check_next_token() == "var":
            self.compile_var_dec()  # varDec*
        function_name = "{}.{}".format(self.class_name, subroutine_name)
        num_locals = self.symbol_table.var_count("VAR")
        self.vm_writer.write_function(function_name, num_locals)
        if subroutine_kind == "constructor":
            num_fields = self.symbol_table.var_count("FIELD")
            self.vm_writer.write_push("CONST", num_fields)
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("POINTER", 0)
        elif subroutine_kind == "method":
            self.vm_writer.write_push("ARG", 0)
            self.vm_writer.write_pop("POINTER", 0)
        self.compile_statements()  # statements
        self.get_token()  # '}

        # ( (type varName) (',' type varName)*)?

    def compile_parameter_list(self):
        # curr_token == '('
        if self.check_next_token() != ")":
            type = self.load_next_token()  # type
            name = self.load_next_token()  # varName
            self.symbol_table.define(name, type, "ARG")
        while self.check_next_token() != ")":
            self.load_next_token()  # ','
            type = self.load_next_token()  # type
            name = self.load_next_token()  # varName
            self.symbol_table.define(name, type, "ARG")
        # NOTE param compilation finishes when next_token == ')'

    def is_array(self):
        return self.check_next_token() == "["

    def is_class_var_dec(self):
        return self.check_next_token() in ["static", "field"]

    def is_subroutine_dec(self):
        return self.check_next_token() in ["constructor", "function", "method"]

    def is_statement(self):
        return self.check_next_token() in ["let", "if", "while", "do", "return"]

    def is_op(self):
        return self.check_next_token() in ["+", "-", "*", "/", "&", "|", "<", ">", "="]

    def is_unary_op_term(self):
        return self.check_next_token() in ["~", "-"]

    def check_next_token(self):
        return self.tokenizer.next_token[1]

    def check_next_type(self):
        return self.tokenizer.next_token[0]

    def load_next_token(self):
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()  # curr_token = next_token
            return self.tokenizer.curr_token[1]

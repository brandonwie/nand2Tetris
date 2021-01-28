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

        self.if_index = 0

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
        # NOTE next_token is neither 'var' or ';'
        # NOTE next_token is statements* (zero or more)

        # ANCHOR actual writing
        func_name = f"{self.class_name}.{subroutine_name}"  # Main.main
        num_locals = self.symbol_table.counts["VAR"]  # get 'var' count
        self.vm_writer.write_function(func_name, num_locals)
        if subroutine_kind == "constructor":
            num_fields = self.symbol_table.counts["FIELD"]
            self.vm_writer.write_push("CONST", num_fields)
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("POINTER", 0)
        elif subroutine_kind == "method":
            self.vm_writer.write_push("ARG", 0)
            self.vm_writer.write_pop("POINTER", 0)

        # NOTE statement starts here
        self.compile_statements()  # statements
        self.load_next_token()  # '}

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

        # 'var' type varName (',' varName)* ';'

    def compile_var_dec(self):
        self.load_next_token()  # 'var'
        type = self.load_next_token()  # type
        name = self.load_next_token()  #  # varName
        self.symbol_table.define(name, type, "VAR")
        while self.check_next_token() != ";":  # (',' varName)*
            self.load_next_token()  # ','
            name = self.load_next_token()  # varName
            self.symbol_table.define(name, type, "VAR")
        self.load_next_token()  # ';'

    # statement*
    # letStatement | ifStatement | whileStatement | doStatement | returnStatement
    def compile_statements(self):
        # if next_token == let | if | while | do | return
        while self.is_statement():
            statement = (
                self.load_next_token()
            )  # curr_token == let | if | while | do | return
            if statement == "let":
                self.compile_let()
            elif statement == "if":
                self.compile_if()
            elif statement == "while":
                self.compile_while()
            elif statement == "do":
                self.compile_do()
            elif statement == "return":
                self.compile_return()

        # 'let' varName ('[' expression ']')? '=' expression ';'

    def compile_let(self):
        var_name = self.load_next_token()  # curr_token == varName
        var_kind = CONVERT_KIND[self.symbol_table.kind_of(var_name)]
        var_index = self.symbol_table.index_of(var_name)
        # if next_token == "["
        if self.is_array():  # array assignment
            self.load_next_token()  # curr_token == '['
            self.compile_expression()  # expression
            self.load_next_token()  # curr_token == ']'
            self.vm_writer.write_push(var_kind, var_index)
            self.vm_writer.write_arithmetic("ADD")
            self.vm_writer.write_pop("TEMP", 0)
            self.load_next_token()  # curr_token == '='
            self.compile_expression()  # expression
            self.load_next_token()  # curr_token == ';'
            self.vm_writer.write_push("TEMP", 0)
            self.vm_writer.write_pop("POINTER", 1)
            self.vm_writer.write_pop("THAT", 0)
        else:  # regular assignment
            self.load_next_token()  # curr_token == '='
            self.compile_expression()  # expression
            self.load_next_token()  # ';'
            self.vm_writer.write_pop(var_kind, var_index)

    # 'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )?
    def compile_if(self):
        if_index = self.if_index
        #? CHECK LATER IF INDEXING IS OKAY
        self.if_index += 1
        self.load_next_token()  # '('
        self.compile_expression()  # expression
        self.load_next_token()  # ')'
        self.load_next_token()  # '{'
        self.vm_writer.write_if('IF_TRUE{}\n'.format(if_index))
        self.vm_writer.write_goto('IF_FALSE{}\n'.format(if_index))
        self.vm_writer.write_label('IF_TRUE{}\n'.format(if_index))
        self.compile_statements()  # statements
        self.vm_writer.write_goto('IF_END{}\n'.format(if_index))
        self.load_next_token()  # '}'
        self.vm_writer.write_label('IF_FALSE{}\n'.format(if_index))
        if self.peek() == 'else':  # ( 'else' '{' statements '}' )?
            self.load_next_token()  # 'else'
            self.load_next_token()  # '{'
            self.compile_statements()  # statements
            self.load_next_token()  # '}'
        self.vm_writer.write_label('IF_END{}\n'.format(if_index)

    # term (op term)*
    def compile_expression(self):
        self.compile_term()  # term
        while self.is_op():  # (op term)*
            op: str = self.load_next_token()  # op
            self.compile_term()  # term
            if op in ARITHMETIC.keys():
                self.vm_writer.write_arithmetic(ARITHMETIC[op])
            elif op == "*":
                self.vm_writer.write_call("Math.multiply", 2)
            elif op == "/":
                self.vm_writer.write_call("Math.divide", 2)

    # integerConstant | stringConstant | keywordConstant | varName |
    # varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
    def compile_term(self):
        # if next_token == '~' | '-'
        if self.is_unary_op_term():
            unary_op = self.load_next_token()  # curr_token == '~' | '-'
            self.compile_term()  # term (recursive)
            self.vm_writer.write_arithmetic(ARITHMETIC_UNARY[unary_op])
        # if next_token == '(' => '(' expression ')'
        elif self.check_next_token() == "(":
            self.load_next_token()  # '('
            self.compile_expression()  # expression
            self.load_next_token()  # ')'
        # if next_token == INTEGER(const)
        elif self.check_next_type() == "INT_CONST":  # integerConstant
            self.vm_writer.write_push("CONST", self.load_next_token())  # )
        # if next_token == STRING(const)
        elif self.check_next_type() == "STRING_CONST":  # stringConstant
            self.compile_string()
        # if next_token == KEYWORD(const)
        elif self.check_next_type() == "KEYWORD":  # keywordConstant
            self.compile_keyword()
        # varName | varName '[' expression ']' | subroutineCall
        else:
            #! (varName | varName for expression | subroutine)'s base
            var_name = self.load_next_token()  # curr_token = varName | subroutineCall
            #! next_token == '[' | '(' or '.' | just varName
            # varName '[' expression ']'
            if self.is_array():  # if next_token == '['
                self.load_next_token()  # '['
                self.compile_expression()  # expression
                self.load_next_token()  # ']'
                array_kind = self.symbol_table.kind_of(var_name)
                array_index = self.symbol_table.index_of(var_name)
                self.vm_writer.write_push(CONVERT_KIND[array_kind], array_index)
                self.vm_writer.write_arithmetic("ADD")
                self.vm_writer.write_pop("POINTER", 1)
                self.vm_writer.write_push("THAT", 0)
            # if next_token == "(" | "." => curr_token == subroutineCall
            elif self.is_subroutine_call():
                # NOTE curr_token == subroutineName | className | varName
                self.compile_subroutine_call()
            # varName
            else:
                # curr_token == varName
                var_kind = CONVERT_KIND[self.symbol_table.kind_of(var_name)]
                var_index = self.symbol_table.index_of(var_name)
                self.vm_writer.write_push(var_kind, var_index)

    # subroutineCall: subroutineName '(' expressionList ')' |
    # ( className | varName) '.' subroutineName '(' expressionList ')'
    def compile_subroutine_call(self):
        # NOTE curr_token == subroutineCall
        identifier = self.get_curr_token()
        func_name = identifier
        number_args = 0
        #! '.' or '(' 2 cases
        if self.check_next_token() == ".":
            self.load_next_token()  # curr_token == '.'
            subroutine_name = self.load_next_token()  # curr_token == subroutineName
            type = self.symbol_table.type_of(identifier)
            if type != "NONE":  # it's an instance
                kind = self.symbol_table.kind_of(identifier)
                index = self.symbol_table.index_of(identifier)
                self.vm_writer.write_push(CONVERT_KIND[kind], index)
                func_name = f"{type}.{subroutine_name}"
                number_args += 1
            else:  # it's a class
                class_name = identifier
                func_name = f"{class_name}.{subroutine_name}"
        elif self.check_next_token() == "(":
            subroutine_name = identifier
            func_name = f"{self.class_name}.{subroutine_name}"
            number_args += 1
            self.vm_writer.write_push("POINTER", 0)
        self.load_next_token()  # '('
        number_args += self.compile_expression_list()  # expressionList
        self.load_next_token()  # ')'
        self.vm_writer.write_call(func_name, number_args)

    # (expression (',' expression)* )?
    def compile_expression_list(self):
        number_args = 0
        if self.check_next_token() != ")":
            number_args += 1
            self.compile_expression()
        while self.check_next_token() != ")":
            number_args += 1
            self.load_next_token()  # curr_token == ','
            self.compile_expression()
        return number_args

    def compile_string(self):
        string = self.load_next_token()  # curr_token == stringConstant
        self.vm_writer.write_push("CONST", len(string))
        self.vm_writer.write_call("String.new", 1)
        for char in string:
            self.vm_writer.write_push("CONST", ord(char))
            self.vm_writer.write_call("String.appendChar", 2)

    def compile_keyword(self):
        keyword = self.load_next_token()  # curr_token == keywordConstant
        if keyword == 'this':
            self.vm_writer.write_push('POINTER', 0)
        else:
            self.vm_writer.write_push('CONST', 0)
            if keyword == 'true':
                self.vm_writer.write_arithmetic('NOT')

    def is_subroutine_call(self):
        return self.check_next_token() in [".", "("]

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

    def get_curr_token(self):
        return self.tokenizer.curr_token[1]

    def load_next_token(self):
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()  # curr_token = next_token
            return self.tokenizer.curr_token[1]
        else:
            return ""

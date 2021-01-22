import re


class CompilationEngine:
    """
    mount fileNameT.xml, output fileName.xml
    """

    def __init__(self, txml_file):
        self.txml = open(txml_file, "r")
        xml = txml_file.replace("T.xml", ".xml")
        self.xml = open(xml, "w")
        self.is_written = False  # check if line is written
        self.indent_count = 0
        self.txml.readline()  # remove <tokens> tag

    # REVIEW reading every line from xxxT.xml,
    # Need to deal two lines at a time
    # Starts and ends with class, meaning calling compile_class() will do the whole process

    # Grammer
    # statement: if/while/let

    # statements: statement* (zero or more)

    # ifStatement: if() {}

    # whileStatement: while () {}

    # letStatement: let varName = expression ;

    # expression: term (op term)? (one or more)

    # term: varName | constant

    # varName: a string not beginning with a digit

    # constant: a decimal number

    # op: + - = > <

    # ANCHOR PROGRAM STRUCTURE
    def compile_class(self):
        """
        'class' className '{'classVarDec* subroutineDec*'}'
        """
        self.write_opening_tag("class")
        self.write_next_token()  # class
        self.write_next_token()  # className
        self.write_next_token()  # {
        while self.is_class_var_dec():
            self.compile_class_var_dec()
            self.save_token_if_written()

        while self.is_subroutine_dec():
            self.compile_subroutine_dec()
            self.save_token_if_written()

        self.write_next_token()  # '}'
        self.write_closing_tag("class")

    def compile_class_var_dec(self):
        """
        ('static'|'field') type varName (',' varName)* ';'
        """
        self.write_opening_tag("classVarDec")
        self.write_next_token()  # (static|field)
        self.write_next_token()  # type
        self.write_next_token()  # varName
        self.compile_expression_list()

    def compile_subroutine_dec(self):
        """
        - `subroutineDec`: ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
        """
        self.write_opening_tag("subroutineDec")
        self.write_next_token()  # ('constructor' | 'function' | 'method')
        self.write_next_token()  # ('void' | type)
        self.write_next_token()  # subroutineName
        self.write_next_token()  # '('
        self.compile_parameter_list()  # parameterList
        self.write_next_token()  # ')'
        self.compile_subroutine_body()
        self.write_closing_tag("subroutineDec")

    def compile_parameter_list(self):
        """
        (type varName (, type varName)*)?
        """
        self.write_opening_tag("parameterList")
        self.save_token_if_written()
        if ")" not in self.curr_token:
            self.write_next_token()  # type
            self.write_next_token()  # varName
            self.save_token_if_written()
        while ")" not in self.curr_token:
            self.write_next_token()  # ','
            self.write_next_token()  # type
            self.write_next_token()  # varName
            self.save_token_if_written()
        self.write_closing_tag("parameterList")

    def compile_subroutine_body(self):
        """
        - `subroutineBody`: '{' varDec* statements '}'
        """
        self.write_opening_tag("subroutineBody")
        self.write_next_token()  # '{'
        self.save_token_if_written()
        while "var" in self.curr_token:
            self.compile_var_dec()  # varDec*
            self.save_token_if_written()
        self.compile_statements()  # statements
        self.write_next_token()  # '}'
        self.write_closing_tag("subroutineBody")

    def compile_var_dec(self):
        """
        'var' type varName (',' varName)* ';'
        """
        self.write_opening_tag("varDec")
        self.write_next_token()  # 'var'
        self.write_next_token()  # type
        self.write_next_token()  # varName
        self.compile_multiple(",", "identifier")  # (',' varName)*
        self.write_next_token()  # ';'
        self.write_closing_tag("varDec")

    # ANCHOR STATEMENTS

    def compile_statements(self):
        """`statement*`(zero or more)
        - letStatement | ifStatement | whileStatement | doStatement | returnStatement
        """
        self.write_opening_tag("statements")
        while self.is_statement():
            if "let" in self.curr_token:
                self.compile_let()
            elif "if" in self.curr_token:
                self.compile_if()
            elif "while" in self.curr_token:
                self.compile_while()
            elif "do" in self.curr_token:
                self.compile_do()
            elif "return" in self.curr_token:
                self.compile_return()
            self.save_token_if_written()
        self.write_closing_tag("statements")

    # ANCHOR SUB-FUNCTIONS FOR STATEMENTS
    def compile_let(self):
        pass

    def compile_if(self):
        pass

    def compile_while(self):
        pass

    def compile_do(self):
        pass

    def compile_return(self):
        pass

    # ANCHOR EXPRESSIONS

    def compile_expression(self):
        """
        term (op term)*
        """
        self.write_opening_tag("expression")
        self.compile_term()
        while self.is_op():
            self.write_next_token()  # op
            self.compile_term()  # term
        self.write_closing_tag("expression")

    def compile_term(self):
        """
        integerConstant | stringConstant | keywordConstant | varName | varName '[' expression ']' | subroutineCall | '(' expression ')' | unaryOp term
        """
        self.write_opening_tag("term")
        self.save_token_if_written()
        if self.is_unary_op_term():
            self.write_next_token()  # unaryOp
            self.compile_term()  # term
        elif "(" in self.curr_token:
            self.write_next_token()  # '('
            self.compile_expression()  # expression
            self.write_next_token()  # ')'
        else:  # first is an identifier
            self.write_next_token()  # identifier
            self.save_token_if_written()
            if "[" in self.curr_token:
                self.write_next_token()  # '['
                self.compile_expression()  # expression
                self.write_next_token()  # ']'
            elif "." in self.curr_token:
                self.write_next_token()  # '.'
                self.write_next_token()  # subroutineName
                self.write_next_token()  # '('
                self.compile_expression_list()  # expressionList
                self.write_next_token()  # ')'
            elif "(" in self.curr_token:
                self.write_next_token()  # '('
                self.compile_expression_list()  # expressionList
                self.write_next_token()  # ')'
        self.write_closing_tag("term")

    def compile_expression_list(self):
        self.write_opening_tag("expressionList")
        self.save_token_if_written()
        if ")" not in self.curr_token:
            self.compile_expression()  # expression
            self.save_token_if_written()  # for while
        while ")" not in self.curr_token:
            self.write_next_token()  # ','
            self.compile_expression()  # expression
            self.save_token_if_written()
        self.write_closing_tag("expressionList")

    #! This is not included in Proposed Instruction
    def compile_multiple(self, first_identifier, second_identifier):
        self.save_token_if_written()
        while (
            first_identifier in self.curr_token or second_identifier in self.curr_token
        ):
            self.write_next_token()
            self.save_token_if_written()

    # ANCHOR Boolean functions
    def is_class_var_dec(self) -> bool:
        self.save_token_if_written()
        return "static" in self.curr_token or "field" in self.curr_token

    def is_subroutine_dec(self) -> bool:
        self.save_token_if_written()
        return (
            "constructor" in self.curr_token
            or "function" in self.curr_token
            or "method" in self.curr_token
        )

    def is_statement(self) -> bool:
        self.save_token_if_written()
        return (
            "let" in self.curr_token
            or "if" in self.curr_token
            or "while" in self.curr_token
            or "do" in self.curr_token
            or "return" in self.curr_token
        )

    def is_op(self) -> bool:
        self.save_token_if_written()
        return bool(re.search(r"> (\+|-|\*|/|&amp;|\||&lt;|&gt;|=) <", self.curr_token))

    def is_unary_op_term(self) -> bool:
        self.save_token_if_written()
        return bool(re.search(r"> (-|~) <", self.curr_token))

    # ANCHOR Examine if current token is written or not
    def save_token_if_written(self):
        """
        if curr_token is already written but not yet next token is loaded in curr_token,
        * Mount next new token to curr_token
        * Set is_written to False
        """
        if self.is_written:
            self.curr_token = self.txml.readline()
            self.is_written = False

    # ANCHOR Writing part
    @property
    def curr_indent(self):
        return "\t" * self.indent_count

    def write_next_token(self):
        if self.is_written:
            self.curr_token = self.txml.readline()
        # write current token
        self.xml.write(f"{self.curr_indent}{self.curr_token}\n")
        self.is_written = True

    def write_opening_tag(self, tag):
        self.xml.write(f"<{tag}>\n")
        self.indent_count += 1

    def write_closing_tag(self, tag):
        self.indent_count -= 1
        self.xml.write(f"{self.curr_indent}</{tag}>\n")

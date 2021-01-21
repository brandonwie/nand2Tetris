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
    # Need to get content which is line.spilt(" ")[1]
    # Need to think two lines at a time
    # Starts with class

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

    def compile_class(self):
        self.write()

    def compile_class_var_dec(self):
        pass

    def compile_subroutine_dec(self):
        pass

    def compile_parameter_list(self):
        pass

    def compile_subroutine_body(self):
        pass

    def compile_var_dec(self):
        pass

    def compile_statements(self):
        pass

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

    def compile_expression(self):
        pass

    def compile_term(self):
        pass

    def compile_expression_list(self):
        pass

    @property
    def curr_indent(self):
        return "\t" * self.indent_count

    def write(self):
        if self.is_written:  # if curr_line is already written,
            # read new line and mount it to curr_token
            self.curr_token = self.txml.readline()
        else:
            # if not, set "is_written" to True bcs we're gonna write one
            self.is_written = True
        self.xml.write(f"{self.curr_indent}{self.curr_token}\n")

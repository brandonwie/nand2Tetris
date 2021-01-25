from jack_tokenizer import JackTokenizer
from symbol_table import SymbolTable
from compilation_engine import CompilationEngine


class JackCompiler:
    def __init__(self, file_name):
        tokenizer = JackTokenizer(file_name)
        symbol_table = SymbolTable
        compilation_engine = CompilationEngine
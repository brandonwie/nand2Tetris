from jack_tokenizer import JackTokenizer
from symbol_table import SymbolTable
from compilation_engine import CompilationEngine


class JackCompiler:
    def __init__(self, file_path):
        tokenizer = JackTokenizer(file_path)
        symbol_table = SymbolTable
        compilation_engine = CompilationEngine

        self.jack_files = self.parse_argv(file_path)
        for jack_file in self.jack_files:
            jack = JackTokenizer(jack_file)
            jack.translate()
            jack.close()
            txml_file = jack_file.replace(".jack", "T.xml")
            xml = CompilationEngine(txml_file)
            xml.compile_class()

    def parse_argv(self, file_path) -> list:
        if ".jack" in file_path:
            return [file_path]
        else:
            dirpath, dirnames, filenames = next(os.walk(file_path), [[], [], []])
            jack_files = filter(lambda x: ".jack" in x, filenames)
            return [file_path + "/" + jack for jack in jack_files]


if __name__ == "__main__":
    import sys

    file_path = sys.argv[1]
    JackCompiler(file_path)
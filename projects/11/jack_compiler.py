from compilation_engine import CompilationEngine
import os


class JackCompiler:
    def __init__(self, file_path):
        self.jack_files = self.parse_argv(file_path)

        for jack_file in self.jack_files:
            compiler = CompilationEngine(jack_file)
            compiler.compile_class()
            print(compiler.symbol_table.class_scope)
            print(compiler.symbol_table.subroutine)

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
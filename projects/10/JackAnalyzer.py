from Tokenizer import JackTokenizer
import os


class JackAnalyzer:
    def __init__(self, file_path):
        jack = JackTokenizer(file_path)
        jack.translate()
        jack.close()

    # def parse_argv(self, file_path):
    #     path = os.getcwd()
    #     if ".jack" in file_path:
    #         file_name = file_path
    #         for dirpath, dirnames, filenames in os.walk(path):
    #             if file_name in filenames:
    #                 jack_file = f"{dirpath}/{file_name}"
    #                 return [jack_file]
    #     else:
    #         dir_name = file_path
    #         for dirpath, dirnames, filenames in os.walk(path):
    #             if dir_name == dirpath.split("/")[-1]:
    #                 self.asm_file = f"{dirpath}/{dir_name}.asm"
    #                 vm_files = filter(lambda x: ".vm" in x, filenames)
    #                 return [dirpath + "/" + vm for vm in vm_files]


if __name__ == "__main__":
    import sys

    file_path = sys.argv[1]
    JackAnalyzer(file_path)

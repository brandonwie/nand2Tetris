import os, sys

# get current dir
curDir = os.getcwd()

# get file name with argv
if len(sys.argv) == 2:
    fn = sys.argv[1]
    print(fn)
    # find the file matches the arg filename
    # os.walk returns lists on 3-tuples respectively
    for dirpath, dirnames, filenames in os.walk(curDir):
        if fn in filenames:
            print(f"{dirpath}/{fn}")
else:
    raise Exception("You must put 1 file name.")
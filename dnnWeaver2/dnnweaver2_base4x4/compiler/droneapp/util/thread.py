import sys

def thread_print(string):
    sys.stdout.write("\r" + str(string) + "\n")
    sys.stdout.flush()


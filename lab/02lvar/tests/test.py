import ast
import sys

with open(sys.argv[1]) as f:

    prog = ast.parse(f.read())
    
prog = ast.dump(ast.parse(prog))
print(prog)
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ast import Constant
from x86_ast import Immediate
from compiler import Compiler

c = Compiler()
result = c.select_arg(Constant(value=42))
print(result)
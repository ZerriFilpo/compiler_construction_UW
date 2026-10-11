# Adapted by permission from https://github.com/IUCompilerCourse/python-student-support-code
# See EOC-LICENSE for details
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import ast
from ast import (expr, stmt, Module, Name, Expr, Call, Assign, Constant, UnaryOp, BinOp)
from x86_ast import (X86Program, instr, arg, Variable, Instr, Callq, Reg, Immediate, Deref, is_memory_arg)


Binding = tuple[Name, expr]
Temporaries = list[Binding]


class Compiler:


    ############################################################################
    # Remove Complex Operands
    ############################################################################

    def rco_exp(self, e: expr, need_atomic : bool) -> tuple[expr, Temporaries]:
        # YOUR CODE HERE
        pass        

    def rco_stmt(self, s: stmt) -> list[stmt]:
        # YOUR CODE HERE
        pass        

    def remove_complex_operands(self, p: Module) -> Module:
        # YOUR CODE HERE
        pass                

    ############################################################################
    # Select Instructions
    ############################################################################

    # The expression e passed to select_arg should furthermore be an atom.
    # (But there is no type for atoms, so the type of e is given as expr.)
    def select_arg(self, e: expr) -> arg:

        match e:

            case Constant(value=v):

                return Immediate(v)

            case Name(id=n):

                return Variable(n)

            case _:

                raise ValueError(f"Unknown statement: {e}")



    def select_stmt(self, s: stmt) -> list[instr]:

        instrs = []

        match s:

            case Expr(value=Call(func=Name(id='print'), args=[arg])):

                instrs.append(Instr('movq', [self.select_arg(arg), Reg('rdi')]))
                instrs.append(Callq('print_int', 1))

            case Assign(targets=[Name(id=var)], value=arg):

                match arg:

                    case Constant(value=v):

                        instrs.append(Instr('movq', [Immediate(v), Reg('rax')]))

                    case Name(id=n):

                        instrs.append(Instr('movq', [Variable(n), Reg('rax')]))
                
                    case Call(func=Name(id='input_int'), args=[]):

                        instrs.append(Callq('input_int', 0))

                    case UnaryOp(op=ast.USub(), operand=arg):

                        instrs.append(Instr('movq', [self.select_arg(arg), Reg('rax')]))
                        instrs.append(Instr('negq', [Reg('rax')]))

                    case BinOp(left=left, op=ast.Add(), right=right):

                        instrs.append(Instr('addq', [self.select_arg(right), self.select_arg(left),]))

                    case BinOp(left=left, op=ast.Sub(), right=right):
                        instrs.append(Instr('subq', [self.select_arg(right) ,self.select_arg(left)]))

                instrs.append(Instr('movq', [Reg('rax'), Variable(var)]))

        return instrs


    def select_instructions(self, p: Module) -> X86Program:

        instrs = []

        for s in p.body:

            instrs.extend(self.select_stmt(s))

        return X86Program(instrs)


  


                    

    ############################################################################
    # Assign Homes
    ############################################################################

    def assign_homes_arg(self, a: arg, home: dict[Variable, arg]) -> arg:
        
        if isinstance(a, Variable):

            return home[a]

        else:
            
            return a
                 

    def assign_homes_instr(self, i: instr,
                           home: dict[Variable, arg]) -> instr:

        match i:

            case Instr(instr=instr, args=args):

                new_args = []

                for a in args:

                    new_args.append(self.assign_homes_arg(a, home))

                return Instr(instr, new_args)

            case Callq(label=label, nargs=nargs):

                return Callq(label, nargs)

            case _:
                return i
        
    def assign_homes(self, p: X86Program) -> X86Program:

        varibles = set()

        for instr in p.body:

            if isinstance(instr, Instr):

                for arg in instr.args:

                    if isinstance(arg, Variable):

                        varibles.add(arg)

        home = {}
        offset = -8

        for var in varibles:

            home[var] = Deref('rbp', offset)
            offset -= 8

        new_body = []    

        for i in p.body:

            new_body.append(self.assign_homes_instr(i, home))

        return X86Program(new_body)

    

        
    ############################################################################
    # Patch Instructions
    ############################################################################

    def patch_instr(self, i: instr) -> list[instr]:

        instrs = []

        if isinstance(i, Instr):

            if i.instr == 'addq' or i.instr == 'subq':

                if is_memory_arg(i.args[0]) and is_memory_arg(i.args[1]):

                    instrs.append(Instr('movq', [i.args[1], Reg('rax')]))
                    instrs.append(Instr(i.instr, [i.args[0], Reg('rax')]))
                    
                    return instrs

            return [i]
    


    def patch_instructions(self, p: X86Program) -> X86Program:

        new_body = []
        
        for i in p.body:

            if isinstance(i, Instr):

                new_body.extend(self.patch_instr(i))

            else:

                new_body.append(i)

        return X86Program(new_body)

                    

                  

    ############################################################################
    # Prelude & Conclusion
    ############################################################################

    def prelude_and_conclusion(self, p: X86Program) -> X86Program:
        # YOUR CODE HERE
        pass        



if __name__ == '__main__':
    import sys
    with open(sys.argv[1]) as f:
        prog = ast.parse(f.read())
    
    c = Compiler()
    x86 = c.select_instructions(prog)
    x86 = c.assign_homes(x86)
    x86 = c.patch_instructions(x86)
    print(x86)
# Adapted by permission from https://github.com/IUCompilerCourse/python-student-support-code
# See EOC-LICENSE for details
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import ast
from ast import (expr, stmt, Module, Name, Expr, Call, Assign, Constant, UnaryOp, BinOp)
from x86_ast import (X86Program, instr, arg, Variable, Instr, Callq, Reg, Immediate, Deref)


Binding = tuple[Name, expr]
Temporaries = list[Binding]


class Compiler:

    count = 1

    ############################################################################
    # Remove Complex Operands
    ############################################################################

    def rco_exp(self, e: expr, need_atomic : bool) -> tuple[expr, Temporaries]:

        match e:

            case Constant(value=v):

                return (e, [])
            
            case Name(id=n):

                return (e, [])

            case BinOp(left=left, op=op, right=right):

                l, temp_l = self.rco_exp(left, True)
                r, temp_r = self.rco_exp(right, True)

                e = BinOp(left=l, op=op, right=r)

                if need_atomic:

                    t = Name(id=f'%tmp{self.count}')

                    self.count += 1

                    return (t, temp_l + temp_r + [(t, e)])

                return (e, temp_l + temp_r)

            case UnaryOp(op=ast.USub(), operand=arg):
                
                ar, temp = self.rco_exp(arg, True)
            
                e = UnaryOp(op=ast.USub(), operand=ar)

                if need_atomic:

                    t = Name(id=f'%tmp{self.count}')

                    self.count += 1

                    return (t, temp + [(t, e)])

                return (e, temp)

            case Call(func=Name(id='input_int'), args=[]):

                if need_atomic:

                    t = Name(id=f'%tmp{self.count}')

                    self.count += 1

                    return (t, [(t, e)])

                return (e, [])

            case _:

                raise ValueError(f"Unknown expression: {e}")
                    
            
    def rco_stmt(self, s: stmt) -> list[stmt]:

        stmts = []

        match s:       

            case Assign(targets=[Name(id=var)], value=arg):

                e, temp = self.rco_exp(arg, False)

                for t, exp in temp:

                    stmts.append(Assign(targets=[t], value=exp))

                stmts.append(Assign(targets=[Name(id=var)], value=e))

                return stmts 

            case Expr(value=Call(func=Name(id='print'), args=[arg])):

                e, temp = self.rco_exp(arg, True)

                for t, exp in temp:

                    stmts.append(Assign(targets=[t], value=exp))

                stmts.append(Expr(value=Call(func=Name(id='print'), args=[e])))

                return stmts

            case _:

                return [s]



    def remove_complex_operands(self, p: Module) -> Module:

        new_body = []

        self.count = 1

        for s in p.body:

            new_body.extend(self.rco_stmt(s))  

        return Module(body=new_body, type_ignores=[])           

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

                        instrs.append(Instr('movq', [Immediate(v), Variable(var)]))

                    case Name(id=n):

                        instrs.append(Instr('movq', [Variable(n), Variable(var)]))
                
                    case Call(func=Name(id='input_int'), args=[]):

                        instrs.append(Callq('input_int', 0))
                        instrs.append(Instr('movq', [Reg('rax'), Variable(var)]))

                    case UnaryOp(op=ast.USub(), operand=arg):

                        instrs.append(Instr('movq', [self.select_arg(arg), Variable(var)]))
                        instrs.append(Instr('negq', [Variable(var)]))

                    case BinOp(left=left, op=ast.Add(), right=right):

                        #instrs.append(Instr('movq', [self.select_arg(left), Reg('rax')]))
                        #instrs.append(Instr('addq', [self.select_arg(right), Reg('rax')]))

                        var = Variable(var)

                        if var == self.select_arg(left):

                            instrs.append(Instr('addq', [self.select_arg(right), self.select_arg(left)]))

                        elif var == self.select_arg(right):

                            instrs.append(Instr('addq', [self.select_arg(left), self.select_arg(right)]))

                        else:

                            instrs.append(Instr('movq', [self.select_arg(left), var]))
                            
                            instrs.append(Instr('addq', [self.select_arg(right), var]))

                    case BinOp(left=left, op=ast.Sub(), right=right):

                        #instrs.append(Instr('movq', [self.select_arg(left), Reg('rax')]))
                        #instrs.append(Instr('subq', [self.select_arg(right), Reg('rax')]))

                        #instrs.append(Instr('subq', [self.select_arg(left) ,self.select_arg(right)]))

                        var = Variable(var)
                        
                        if var == self.select_arg(left):

                            instrs.append(Instr('subq', [self.select_arg(right), self.select_arg(left)]))

                            # a = a - b
                            # subq b, a => a = a - b

                        elif var == self.select_arg(right):

                            instrs.append(Instr('subq', [self.select_arg(left), self.select_arg(right)]))
                            instrs.append(Instr('negq', [self.select_arg(right)]))

                            # a = b - a
                            # subq b, a => a = a - b
                            # negq a => -a = -(a - b) = b - a

                        else:

                            instrs.append(Instr('movq', [self.select_arg(left), var]))
                            
                            instrs.append(Instr('subq', [self.select_arg(right), var]))
                    
                    case BinOp(left=left, op=ast.Mult(), right=right):

                        var = Variable(var)
                        
                        if var == self.select_arg(left):

                            instrs.append(Instr('imulq', [self.select_arg(right), self.select_arg(left)]))

                        elif var == self.select_arg(right):

                            instrs.append(Instr('imulq', [self.select_arg(left), self.select_arg(right)]))

                        elif isinstance(self.select_arg(right), Immediate) and isinstance(self.select_arg(left), Variable):
                        
                            instrs.append(Instr('imulq', [self.select_arg(right), self.select_arg(left), var]))

                            return instrs
                        
                        elif isinstance(self.select_arg(left), Immediate) and isinstance(self.select_arg(right), Variable):
                        
                            instrs.append(Instr('imulq', [self.select_arg(left), self.select_arg(right), var]))

                            return instrs

                        else:

                            instrs.append(Instr('movq', [self.select_arg(left), var]))
                            
                            instrs.append(Instr('imulq', [self.select_arg(right), var]))


                    case BinOp(left=left, op=ast.FloorDiv(), right=right):

                        if isinstance(self.select_arg(right), Immediate):

                            temp = Variable(f'%tmp{self.count}')
                            self.count += 1

                            instrs.append(Instr('movq', [self.select_arg(right), temp]))
                            instrs.append(Instr('idivq', [self.select_arg(left), temp, Variable(var)]))

                            return instrs

                        instrs.append(Instr('idivq', [self.select_arg(left), self.select_arg(right), Variable(var)]))


                    case BinOp(left=left, op=ast.Mod(), right=right):

                        if isinstance(self.select_arg(right), Immediate):
                        
                            temp = Variable(f'%tmp{self.count}')
                            self.count += 1

                            instrs.append(Instr('movq', [self.select_arg(right), temp]))
                            instrs.append(Instr('idivq', [self.select_arg(left), temp]))
                            instrs.append(Instr('movq', [Reg('rdx'), Variable(var)]))

                            return instrs
                        
                        instrs.append(Instr('idivq', [self.select_arg(left), self.select_arg(right)]))
                        instrs.append(Instr('movq', [Reg('rdx'), Variable(var)]))

        return instrs


    def select_instructions(self, p: Module) -> X86Program:

        instrs = []

        for s in p.body:

            instrs.extend(self.select_stmt(s))

        return X86Program(instrs)

    def uncover_live(self, p: X86Program) -> X86Program:

        live = set()

        self.live_after = {}

        size = len(p.body) - 1

        for i in reversed(p.body):

            W = set()
            R = set()

            if isinstance(i, Callq):

                R |= set([Reg('rdi'), Reg('rsi'), Reg('rdx'), Reg('rcx'), Reg('r8'), Reg('r9')][:i.num_args])
                W |= {Reg('rax'), Reg('rcx'), Reg('rdx'), Reg('rsi'), Reg('rdi'), Reg('r8'), Reg('r9'), Reg('r10'), Reg('r11')}

            if isinstance(i, Instr):

                if i.instr == 'idivq':

                    if isinstance(i.args[1], Variable) or isinstance(i.args[1], Reg):
                                                        
                        R.add(i.args[1])

                    if isinstance(i.args[0], Variable) or isinstance(i.args[0], Reg):

                        R.add(i.args[0])

                    if len(i.args) == 3:

                        if isinstance(i.args[2], Variable) or isinstance(i.args[2], Reg):

                            W.add(i.args[2])

                    W.add(Reg('rax'))
                    W.add(Reg('rdx'))

                elif len(i.args) == 1:

                    d = i.args[0]

                    if isinstance(d, Variable) or isinstance(d, Reg):

                        if i.instr == 'negq':

                            R.add(d)
                            W.add(d)          

                if len(i.args) == 2:

                    s = i.args[0]
                    d = i.args[1]

                    if i.instr == 'movq':
                    
                        if isinstance(s, Variable) or isinstance(s, Reg):
    
                            R.add(s)
    
                        if isinstance(d, Variable) or isinstance(d, Reg):
    
                            W.add(d)


                    if i.instr == 'addq':
                    
                        if isinstance(s, Variable) or isinstance(s, Reg):

                            R.add(s)

                        if isinstance(d, Variable) or isinstance(d, Reg):

                            R.add(d)
                            W.add(d)

                    if i.instr == 'subq':
                    
                        if isinstance(s, Variable) or isinstance(s, Reg):

                            R.add(s)

                        if isinstance(d, Variable) or isinstance(d, Reg):

                            R.add(d)
                            W.add(d)

                    if i.instr == 'imulq':

                        if isinstance(s, Variable) or isinstance(s, Reg):

                            R.add(s)

                        if isinstance(d, Variable) or isinstance(d, Reg): 

                            R.add(d)
                            W.add(d)

                elif len(i.args) == 3:

                    s = i.args[1]
                    d = i.args[2]

                    if i.instr == 'imulq':

                        if isinstance(s, Variable) or isinstance(s, Reg):

                            R.add(s)

                        if isinstance(d, Variable) or isinstance(d, Reg):

                            W.add(d)

        self.live_after[size] = live
        size -= 1

        live = (live - W) | R
        
        return p
                    

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
            
            case _:
                return i
        
    def assign_homes(self, p: X86Program) -> X86Program:

        variables = []

        for instr in p.body:

            if isinstance(instr, Instr):

                for arg in instr.args:

                    if isinstance(arg, Variable):

                        if arg not in variables:

                            variables.append(arg)

        home = {}
        offset = -8

        for var in variables:

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

            if i.instr == 'movq':
                
                if isinstance(i.args[0], Immediate) and not(-2**31 <= i.args[0].value 
                                                            < 2**31) and not isinstance(i.args[1], Reg):

                    instrs.append(Instr('movq', [i.args[0], Reg('rax')]))
                    instrs.append(Instr('movq', [Reg('rax'), i.args[1]]))

                    return instrs

                if isinstance(i.args[0], Deref) and isinstance(i.args[1], Deref):

                    instrs.append(Instr('movq', [i.args[0], Reg('rax')]))
                    instrs.append(Instr('movq', [Reg('rax'), i.args[1]]))

                    return instrs
            

            if i.instr == 'addq' or i.instr == 'subq' or i.instr == 'imulq':

                if i.instr == 'imulq' and len(i.args) == 3:
                    
                    if not isinstance(i.args[2], Reg) or (isinstance(i.args[0], Immediate) and not(-2**31 <= i.args[0].value < 2**31 )):

                        instrs.append(Instr('movq', [i.args[0], Reg('rax')]))
                        instrs.append(Instr(i.instr, [i.args[1], Reg('rax')]))
                        instrs.append(Instr('movq', [Reg('rax'), i.args[2]]))

                        return instrs

                    return [i]

                if not isinstance(i.args[1], Reg): #if is_memory_arg(i.args[0]) or is_memory_arg(i.args[1]):
                
                    if i.instr == 'imulq':

                        instrs.append(Instr('movq', [i.args[0], Reg('rax')]))
                        instrs.append(Instr(i.instr, [i.args[1], Reg('rax')]))
                        instrs.append(Instr('movq', [Reg('rax'), i.args[1]]))

                        return instrs

                    instrs.append(Instr('movq', [i.args[0], Reg('rax')]))
                    instrs.append(Instr(i.instr, [Reg('rax'), i.args[1]]))
                    
                    return instrs

                if isinstance(i.args[0], Immediate) and not(-2**31 <= i.args[0].value < 2**31 ):

                    instrs.append(Instr('movq', [i.args[0], Reg('rax')]))
                    instrs.append(Instr(i.instr, [Reg('rax'), i.args[1]]))
                    
                    return instrs

            if i.instr == 'idivq':

                instrs.append(Instr('movq', [i.args[0], Reg('rax')]))
                instrs.append(Instr('cqto', []))
                instrs.append(Instr('idivq', [i.args[1]]))

                if len(i.args) == 3:

                    instrs.append(Instr('movq', [Reg('rax'), i.args[2]]))

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

        prelude = [

            Instr('pushq', [Reg('rbp')]),
            Instr('movq', [Reg('rsp'), Reg('rbp')]),

        ]

        offset = 0

        for i in p.body:

            if isinstance(i, Instr):

                for a in i.args:

                    if isinstance(a, Deref):

                        offset = max(offset, abs(a.offset)) 

        while offset % 16 != 0:

            offset += 8

        prelude.append(Instr('subq', [Immediate(offset), Reg('rsp')]))

        coclusion = [

            Instr('movq', [Reg('rbp'), Reg('rsp')]),
            Instr('movq', [Immediate(0), Reg('rax')]),
            Instr('popq', [Reg('rbp')]),
            Instr('retq', []),

        ]

        return X86Program(prelude + p.body + coclusion)



if __name__ == '__main__':
    import sys
    with open(sys.argv[1]) as f:
        prog = ast.parse(f.read())
    
    c = Compiler()
    prog = c.remove_complex_operands(prog)
    x86 = c.select_instructions(prog)
    x86 = c.assign_homes(x86)
    x86 = c.patch_instructions(x86)
    x86 = c.prelude_and_conclusion(x86)
    print(x86)
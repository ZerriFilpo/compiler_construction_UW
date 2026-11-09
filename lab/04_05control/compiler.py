# Adapted by permission from https://github.com/IUCompilerCourse/python-student-support-code
# See EOC-LICENSE for details
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import ast
from ast import (expr, stmt, Module, Name, Expr, Call, Assign, Constant, Compare, UnaryOp,
                  BinOp, BoolOp, IfExp, If, Return, While)
from x86_ast import (X86Program, instr, arg, Variable, Instr, Callq, Reg, ByteReg, Immediate, 
                     Deref, Jump, JumpIf)
from graph import UndirectedAdjList
from cif import (Begin, Goto, CProgram)
from collections import deque

Binding = tuple[Name, expr]
Temporaries = list[Binding]


class Compiler:

    b_size = 1
    count = 1

    ############################################################################
    # Remove Complex Operands
    ############################################################################

    def shrink_exp(self, e: expr) ->expr:

        match e:

            case BoolOp(op=op, values=values):


                a = self.shrink_exp(values[0])

                exp = None

                for v in range(len(values)):

                    if v + 1 >= len(values):

                        break 
                        
                    b = self.shrink_exp(values[v + 1])

                    if isinstance(op, ast.And):

                        if exp is None:
                    
                            exp = IfExp(test=a, body=b, orelse=Constant(False))

                        else:

                            exp = IfExp(test=exp, body=b, orelse=Constant(False))

                    if isinstance(op, ast.Or):

                        if exp is None:
                                            
                            exp = IfExp(test=a, body=Constant(True), orelse=b)

                        else:

                            exp = IfExp(test=exp, body=Constant(True), orelse=b)

                return exp
            
            case UnaryOp(op=op, operand=arg):

                return UnaryOp(op=op, operand=self.shrink_exp(arg))

            case Compare(left=left, ops=ops, comparators=comparators):

                new_comparators = []

                for c in comparators:

                    new_comparators.append(self.shrink_exp(c))

                return Compare(left=self.shrink_exp(left), ops=ops, comparators=new_comparators)

            case BinOp(left=left, op=op, right=right):

                return BinOp(left=self.shrink_exp(left), op=op, right=self.shrink_exp(right))

            case IfExp(test=test, body=body, orelse=orelse):

                return IfExp(test=self.shrink_exp(test), body=self.shrink_exp(body), orelse=self.shrink_exp(orelse))

            case _:

                return e
                    
    def shrink_stmt(self, s: stmt) -> stmt:

        match s:   
        
            case Assign(targets=targets, value=arg):

                return Assign(targets=targets, value=self.shrink_exp(arg))

            case If(test=test, body=body, orelse=orelse):

                new_test = self.shrink_exp(test)

                new_body = []

                new_orelse = []

                for s in body:

                    new_body.append(self.shrink_stmt(s))

                for s in orelse:

                    new_orelse.append(self.shrink_stmt(s))

                return If(test=new_test, body=new_body, orelse=new_orelse)

            case While(test=test, body=body, orelse=orelse):

                new_body = []

                for b in body:

                    new_body.append(self.shrink_stmt(b))

                return While(test=self.shrink_exp(test), body=new_body, orelse=[])

            case Expr(value=Call(func=Name(id='print'), args=[arg])):

                return Expr(value=Call(func=Name(id='print'), args=[self.shrink_exp(arg)]))

            case Expr(value=e):

                return Expr(value=self.shrink_exp(e))
                
            case _:

                return s

    def shrink(self, p: Module) -> Module:

        new_body = []

        self.count = 1

        for s in p.body:

            new_body.append(self.shrink_stmt(s))  

        return Module(body=new_body, type_ignores=[])           


    def rco_exp(self, e: expr, need_atomic : bool) -> tuple[expr, Temporaries]:

        match e:

            case Constant(value=v):

                return (e, [])
            
            case Name(id=n):

                return (e, [])

            case Compare(left=left, ops=ops, comparators=comparators):

                l, temp_l = self.rco_exp(left, True)
                r, temp_r = self.rco_exp(comparators[0], True)

                e = Compare(left=l, ops=ops, comparators=[r])

                if need_atomic:

                    t = Name(id=f'%tmp{self.count}')

                    self.count += 1

                    return (t, temp_l + temp_r + [(t, e)])

                return (e, temp_l + temp_r)

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

            case UnaryOp(op=ast.Not(), operand=arg):

                ar, temp = self.rco_exp(arg, not isinstance(arg, Compare))
            
                e = UnaryOp(op=ast.Not(), operand=ar)

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

            case IfExp(test=test, body=body, orelse=orelse):
            
                t, temp_t = self.rco_exp(test, False)

                b, temp_b = self.rco_exp(body, False)

                if temp_b:

                    stmts_b = []

                    for tmp, exp in temp_b:

                        stmts_b.append(Assign(targets=[tmp], value=exp))

                    b = Begin(body=stmts_b, result=b)


                o, temp_o = self.rco_exp(orelse, False)


                if temp_o:

                    stmts_b2 = []

                    for tmp, exp in temp_o:

                        stmts_b2.append(Assign(targets=[tmp], value=exp))

                    o = Begin(body=stmts_b2, result=o)

                e = IfExp(test=t, body=b, orelse=o)

                if need_atomic:
                
                    t = Name(id=f'%tmp{self.count}')

                    self.count += 1

                    return (t, temp_t + [(t, e)])

                return (e, temp_t)
            
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

            case If(test=test, body=body, orelse=orelse):

                e, temp = self.rco_exp(test, False)

                for t, exp in temp:

                    stmts.append(Assign(targets=[t], value=exp))

                new_body = []

                for b in body:

                    new_body.extend(self.rco_stmt(b))

                new_orelse = []

                for o in orelse:
                    
                    new_orelse.extend(self.rco_stmt(o))

                stmts.append(If(test=e, body=new_body, orelse=new_orelse))

                return stmts

            case While(test=test, body=body, orelse=[]):

                e, temp = self.rco_exp(test, False)

                if temp:

                    temp_stmts = []

                    for t, exp in temp:

                        temp_stmts.append(Assign(targets=[t], value=exp))

                    e = Begin(body=temp_stmts, result=e)

                new_body = []

                for b in body:

                    new_body.extend(self.rco_stmt(b))

                stmts.append(While(test=e, body=new_body, orelse=[]))

                return stmts

            case Expr(value=e):

                e, temp = self.rco_exp(e, False)

                for t, exp in temp:

                    stmts.append(Assign(targets=[t], value=exp))

                stmts.append(Expr(value=e))

                return stmts

            case _:

                return [s]



    def remove_complex_operands(self, p: Module) -> Module:

        new_body = []

        self.count = 1

        for s in p.body:

            new_body.extend(self.rco_stmt(s))  

        return Module(body=new_body, type_ignores=[]) 

    def explicate_pred(self, test: expr, body: list[stmt], orelse: list[stmt],
                        basic_blocks: dict[str, list[stmt]]) -> list[stmt]:

        match test:

            case Compare():

                return [If(test, self.create_block(body, basic_blocks), self.create_block(orelse, basic_blocks))]

            case Constant(value=True):

                return body

            case Constant(value=False):

                return orelse

            case UnaryOp(op=ast.Not(), operand=e):

                return self.explicate_pred(e, orelse, body, basic_blocks)

            case IfExp(test=t, body=b, orelse=o):

                thn_block = self.create_block(body, basic_blocks)

                els_block = self.create_block(orelse, basic_blocks)

                novo_thn = self.explicate_pred(b, thn_block, els_block, basic_blocks)
                novo_els = self.explicate_pred(o, thn_block, els_block, basic_blocks)

                return self.explicate_pred(t, novo_thn, novo_els, basic_blocks)

            case Begin(body=ss, result=r):

                return self.explicate_stmts(ss, self.explicate_pred(r, body, orelse, basic_blocks), basic_blocks)

            case Name() | Constant():

                return [If(Compare(left=test, ops=[ast.Eq()], comparators=[Constant(False)]),
                           self.create_block(orelse, basic_blocks), self.create_block(body, basic_blocks))]

            case _:

                t = Name(id=f'%tmp{self.count}')

                self.count += 1

                return [Assign(targets=[t], value=test)] + self.explicate_pred(t, body, orelse, basic_blocks)

    def create_block(self, stmts: list[stmt], basic_blocks: dict[str, list[stmt]]) -> list[stmt]:

        match stmts:

            case [Goto()]:

                return stmts

            case _:
            
                name = f'block{self.b_size}'

                self.b_size += 1
                
                basic_blocks[name] = stmts

                return [Goto(name)]

    def explicate_stmt(self, s: stmt, c: list[stmt], basic_blocks: dict[str, list[stmt]]) -> list[stmt]:

        match s:

            case If(test=test, body=body, orelse=orelse):

                block3 = self.create_block(c, basic_blocks)

                block1 = self.create_block(self.explicate_stmts(body, block3, basic_blocks), basic_blocks)
                block2 = self.create_block(self.explicate_stmts(orelse, block3, basic_blocks), basic_blocks)

                return self.explicate_pred(test, block1, block2, basic_blocks)

            case While(test=test, body=body):

                loop_label = f'block{self.b_size}'

                self.b_size += 1

                after_loop = self.create_block(c, basic_blocks)

                body_code = self.explicate_stmts(body, [Goto(loop_label)], basic_blocks)

                basic_blocks[loop_label] = self.explicate_pred(test, body_code, after_loop, basic_blocks)

                return [Goto(loop_label)]

            case Assign(targets=[lhs], value=rhs):

                return self.explicate_assign(rhs, lhs, c, basic_blocks)

            case Expr(value=Call(func=Name(id='print'))):

                return [s] + c

            case Expr(value=e):

                return self.explicate_effect(e, c, basic_blocks)

            case _:

                return [s] + c

    def explicate_stmts(self, ss: list[stmt], c: list[stmt], basic_blocks: dict[str, list[stmt]]) -> list[stmt]: 

        for s in reversed(ss):

            c = self.explicate_stmt(s, c, basic_blocks)

        return c

    def explicate_control(self, p: Module) -> CProgram:

        basic_blocks = {}

        self.b_size = 1

        c = [Return(Constant(0))]

        c = self.explicate_stmts(p.body, c, basic_blocks)

        basic_blocks['start'] = c

        return CProgram(body=basic_blocks)


    def explicate_assign(self, rhs: expr, lhs: Name, cont: list[stmt],
                        basic_blocks: dict[str, list[stmt]]) -> list[stmt]:

        match rhs:

            case IfExp(test=t, body=b, orelse=o):

                cont_block = self.create_block(cont, basic_blocks)

                thn = self.explicate_assign(b, lhs, cont_block, basic_blocks)
                els = self.explicate_assign(o, lhs, cont_block, basic_blocks)

                return self.explicate_pred(t, thn, els, basic_blocks)

            case Begin(body=ss, result=r):

                return self.explicate_stmts(ss, self.explicate_assign(r, lhs, cont, basic_blocks), basic_blocks)

            case _:

                return [Assign(targets=[lhs], value=rhs)] + cont


    def explicate_effect(self, e: expr, cont: list[stmt],
                         basic_blocks: dict[str, list[stmt]]) -> list[stmt]:

        match e:

            case IfExp(test=t, body=b, orelse=o):

                cont_block = self.create_block(cont, basic_blocks)

                thn = self.explicate_effect(b, cont_block, basic_blocks)
                els = self.explicate_effect(o, cont_block, basic_blocks)

                return self.explicate_pred(t, thn, els, basic_blocks)

            case Begin(body=ss, result=r):

                return self.explicate_stmts(ss, self.explicate_effect(r, cont, basic_blocks), basic_blocks)

            case Call(func=Name(id='input_int'), args=[]):

                return [Expr(value=e)] + cont

            case _:

                return cont

            
    ############################################################################
    # Select Instructions
    ############################################################################

    # The expression e passed to select_arg should furthermore be an atom.
    # (But there is no type for atoms, so the type of e is given as expr.)

    cc = {ast.Eq: 'e', ast.NotEq: 'ne', ast.Lt: 'l', ast.LtE: 'le', ast.Gt: 'g', ast.GtE: 'ge'}

    neg_cc = {'e': 'ne', 'ne': 'e', 'l': 'ge', 'ge': 'l', 'le': 'g', 'g': 'le'}

    def select_arg(self, e: expr) -> arg:

        match e:    

            case Constant(value=bool(v)):

                return Immediate(int(v))

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

                    case Constant():

                        instrs.append(Instr('movq', [self.select_arg(arg), Variable(var)]))

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


                    case Compare(left=l, ops=[op], comparators=[r]):

                        instrs.append(Instr('cmpq', [self.select_arg(r), self.select_arg(l)]))
                        instrs.append(Instr('set' + self.cc[type(op)], [ByteReg('al')]))
                        instrs.append(Instr('movzbq', [ByteReg('al'), Variable(var)]))

                    case UnaryOp(op=ast.Not(), operand=Compare(left=l, ops=[op], comparators=[r])):

                        instrs.append(Instr('cmpq', [self.select_arg(r), self.select_arg(l)]))
                        instrs.append(Instr('set' + self.neg_cc[self.cc[type(op)]], [ByteReg('al')]))
                        instrs.append(Instr('movzbq', [ByteReg('al'), Variable(var)]))

                    case UnaryOp(op=ast.Not(), operand=a):

                        instrs.append(Instr('movq', [self.select_arg(a), Variable(var)]))
                        instrs.append(Instr('xorq', [Immediate(1), Variable(var)]))


            case Goto(label=l):

                instrs.append(Jump(l))

            case Return(value=v):

                instrs.append(Instr('movq', [self.select_arg(v), Reg('rax')]))
                instrs.append(Jump('main_conclusion'))

            case If(test=Compare(left=l, ops=[op], comparators=[r]), body=[Goto(label=thn)], orelse=[Goto(label=els)]):

                instrs.append(Instr('cmpq', [self.select_arg(r), self.select_arg(l)]))
                instrs.append(JumpIf(self.cc[type(op)], thn))
                instrs.append(Jump(els))

            case Expr(value=Call(func=Name(id='input_int'), args=[])):

                instrs.append(Callq('input_int', 0))

        return instrs


    def select_instructions(self, p: CProgram) -> X86Program:

        blocks = {}

        for label, block in p.body.items():

            instrs = []

            for s in block:

                instrs.extend(self.select_stmt(s))

            blocks[label] = instrs

        return X86Program(blocks)

    def read_write(self, i: instr) -> tuple[set[arg], set[arg]]:

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

                if i.instr == 'addq' or i.instr == 'subq' or i.instr == 'imulq' or i.instr == 'xorq':

                    if isinstance(s, Variable) or isinstance(s, Reg):

                        R.add(s)

                    if isinstance(d, Variable) or isinstance(d, Reg):

                        R.add(d)
                        W.add(d)

                if i.instr == 'cmpq':

                    if isinstance(s, Variable) or isinstance(s, Reg):

                        R.add(s)

                    if isinstance(d, Variable) or isinstance(d, Reg):

                        R.add(d)

                if i.instr == 'movzbq':

                    # a origem é %al: ignora-se, só conta o destino
                    if isinstance(d, Variable) or isinstance(d, Reg):

                        W.add(d)

            elif len(i.args) == 3:

                s = i.args[1]
                d = i.args[2]

                if i.instr == 'imulq':

                    if isinstance(s, Variable) or isinstance(s, Reg):

                        R.add(s)

                    if isinstance(d, Variable) or isinstance(d, Reg):

                        W.add(d)

        return R, W

    
    def live_block(self, instrs: list[instr], live_before_block: dict[str, set[arg]]) -> tuple[set[arg], list[tuple[instr, set[arg], set[arg]]]]:

        live = set()

        info = []

        for i in reversed(instrs):

            match i:

                case Jump(label=l):

                    live = set(live_before_block.get(l, set()))

                case JumpIf(label=l):

                    live = live | live_before_block.get(l, set())

            R, W = self.read_write(i)

            info.append((i, W, live))

            live = (live - W) | R

        info.reverse()

        return live, info


    def uncover_live(self, p: X86Program) -> X86Program:

        preds = {label: set() for label in p.body}

        for label, instrs in p.body.items():

            for i in instrs:

                if isinstance(i, (Jump, JumpIf)) and i.label in preds:

                    preds[i.label].add(label)

        live_before_block = {label: set() for label in p.body}

        worklist = deque(p.body.keys())

        while worklist:

            label = worklist.pop()

            live, _ = self.live_block(p.body[label], live_before_block)

            if live != live_before_block[label]:

                live_before_block[label] = live

                worklist.extend(preds[label])

        self.live_info = []

        for label, instrs in p.body.items():

            _, info = self.live_block(instrs, live_before_block)

            self.live_info.extend(info)

        return p

    def build_interference_graph(self, p: X86Program) -> UndirectedAdjList:

        graph = UndirectedAdjList()

        for instrs in p.body.values():

            for instr in instrs:

                if isinstance(instr, Instr):

                    for a in instr.args:

                        if isinstance(a, Variable):

                            graph.add_vertex(a)

        for instr, W, live in self.live_info:

            if isinstance(instr, Instr) and instr.instr == 'idivq' and isinstance(instr.args[1], Variable):
            
                graph.add_edge(instr.args[1], Reg('rax'))
                graph.add_edge(instr.args[1], Reg('rdx'))

            for d in W:

                graph.add_vertex(d)

                for v in live:

                    if isinstance(instr, Instr) and instr.instr == 'movq' and v == instr.args[0]:

                        continue

                    if d != v:

                        graph.add_edge(d, v)
            
        return graph

    def color_graph(self, graph: UndirectedAdjList) -> dict[Variable, int]:

        regs = {'rcx': 0, 'rdx': 1, 'rsi': 2, 'rdi': 3, 'r8': 4, 'r9': 5, 'r10': 6, 'rbx': 7, 'r12': 8,
                 'r13': 9, 'r14': 10, 'rax': -1, 'rsp': -2, 'rbp': -3, 'r11': -4, 'r15': -5}

        color = {}

        for v in graph.vertices():

            if isinstance(v, Reg):

                color[v] = regs[v.id]

        p_vars = []

        for v in graph.vertices():

            if isinstance(v, Variable):

                p_vars.append(v)

        while p_vars:

            size = 0

            saved = set()

            index = 0

            for i in range(len(p_vars)):

                used_colors = set()

                for e in graph.adjacent(p_vars[i]):

                    if e in color:

                        used_colors.add(color[e])

                if len(used_colors) > size:

                    size = len(used_colors)
                    saved = used_colors
                    index = i

            c = 0

            while c in saved:

                c += 1

            v = p_vars.pop(index)

            color[v] = c

        return color

    def allocate_registers(self, p: X86Program, flag: int) -> X86Program:
    
        variables = {}

        var_colors = set()

        graph = self.build_interference_graph(p)

        colors = self.color_graph(graph)

        home = {}

        regs = {'rcx': 0, 'rdx': 1, 'rsi': 2, 'rdi': 3, 'r8': 4, 'r9': 5, 'r10': 6, 'rbx': 7, 'r12': 8,
                            'r13': 9, 'r14': 10, 'rax': -1, 'rsp': -2, 'rbp': -3, 'r11': -4, 'r15': -5}

        inverted = {}

        size = 11

        if flag >= 0:

            size = flag

        for r, i in regs.items():

            inverted[i] = r

        all_instrs = []

        for instrs in p.body.values():

            all_instrs.extend(instrs)

        contagem = {}

        for instr in all_instrs:

            if isinstance(instr, Instr):

                for arg in instr.args:

                    if isinstance(arg, Variable) and colors[arg] <= 10:

                        c = colors[arg]
                        contagem[c] = contagem.get(c, 0) + 1

        ordenadas = sorted(contagem, key=lambda c: contagem[c], reverse=True)

        kept = set(ordenadas[:size]) 

        self.used_callee = []

        for v, c in colors.items():

            if isinstance(v, Variable) and 7 <= c <= 10 and c in kept:

                if inverted[c] not in self.used_callee:

                    self.used_callee.append(inverted[c])


        self.used_callee.sort()

        C = len(self.used_callee)
                
        offset = -8 * (C + 1)

        for instr in all_instrs:

            if isinstance(instr, Instr):

                for arg in instr.args:

                    if isinstance(arg, Variable):

                        if arg not in home and colors[arg] in kept:

                            home[arg] = Reg(inverted[colors[arg]])

                        if arg not in home and colors[arg] not in kept:

                            if colors[arg] not in var_colors:

                                var_colors.add(colors[arg])
                                variables[colors[arg]] = Deref('rbp', offset)
                                home[arg] = Deref('rbp', offset)
                                offset -= 8

                            else:

                                home[arg] = variables[colors[arg]]
                                
        blocks = {}

        for label, instrs in p.body.items():

            new_body = []

            for i in instrs:

                new_body.append(self.assign_homes_instr(i, home))

            blocks[label] = new_body

        return X86Program(blocks)
           
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

                if i.args[0] == i.args[1]:

                    return []
                
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

            if i.instr == 'cmpq':

                if isinstance(i.args[1], Immediate):

                    instrs.append(Instr('movq', [i.args[1], Reg('rax')]))
                    instrs.append(Instr('cmpq', [i.args[0], Reg('rax')]))

                    return instrs

                if isinstance(i.args[0], Deref) and isinstance(i.args[1], Deref):

                    instrs.append(Instr('movq', [i.args[0], Reg('rax')]))
                    instrs.append(Instr('cmpq', [Reg('rax'), i.args[1]]))

                    return instrs

                return [i]

            if i.instr == 'movzbq':

                if not isinstance(i.args[1], Reg):

                    instrs.append(Instr('movzbq', [i.args[0], Reg('rax')]))
                    instrs.append(Instr('movq', [Reg('rax'), i.args[1]]))

                    return instrs

                return [i]

            if i.instr == 'xorq':

                if isinstance(i.args[0], Deref) and isinstance(i.args[1], Deref):

                    instrs.append(Instr('movq', [i.args[0], Reg('rax')]))
                    instrs.append(Instr('xorq', [Reg('rax'), i.args[1]]))

                    return instrs

                return [i]
                
            return [i]
    


    def patch_instructions(self, p: X86Program) -> X86Program:

        blocks = {}

        for label, instrs in p.body.items():

            new_body = []

            for i in instrs:

                if isinstance(i, Instr):

                    new_body.extend(self.patch_instr(i))

                else:

                    new_body.append(i)

            blocks[label] = new_body

        return X86Program(blocks)

                    

                  

    ############################################################################
    # Prelude & Conclusion
    ############################################################################

    def prelude_and_conclusion(self, p: X86Program) -> X86Program:

        prelude = [

            Instr('pushq', [Reg('rbp')]),
            Instr('movq', [Reg('rsp'), Reg('rbp')]),

        ]

        offset = 0

        for instrs in p.body.values():

            for i in instrs:

                if isinstance(i, Instr):

                    for a in i.args:

                        if isinstance(a, Deref):

                            offset = max(offset, abs(a.offset))

        offset = max(offset, 8 * len(self.used_callee))

        while offset % 16 != 0:

            offset += 8

        offset = offset - 8 * len(self.used_callee)

        for r in self.used_callee:

            prelude.append(Instr('pushq', [Reg(r)]))

        prelude.append(Instr('subq', [Immediate(offset), Reg('rsp')]))

        prelude.append(Jump('start'))

        conclusion = []

        conclusion.append(Instr('addq', [Immediate(offset), Reg('rsp')]))

        for r in reversed(self.used_callee):

            conclusion.append(Instr('popq', [Reg(r)]))

        conclusion.append(Instr('popq', [Reg('rbp')]))
        conclusion.append(Instr('retq', []))

        blocks = {'main': prelude}

        blocks.update(p.body)

        blocks['main_conclusion'] = conclusion

        return X86Program(blocks)



if __name__ == '__main__':
    import sys
    with open(sys.argv[1]) as f:
        prog = ast.parse(f.read())

    flag = -1

    for i in range(len(sys.argv)):

        if sys.argv[i] == '--registers':

            flag = i 

    if len(sys.argv) < flag + 2:

        flag = -1

    try:

        flag = int(sys.argv[flag + 1])

    except (ValueError, IndexError):

        flag = -1

    if flag > 11:

        flag = -1
    
    c = Compiler()
    prog = c.shrink(prog)
    
    prog = c.remove_complex_operands(prog)

    prog = c.explicate_control(prog)

    x86 = c.select_instructions(prog)
    x86 = c.uncover_live(x86)
    x86 = c.allocate_registers(x86, flag)
    x86 = c.patch_instructions(x86)
    x86 = c.prelude_and_conclusion(x86)
    print(x86)
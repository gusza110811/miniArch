from __future__ import annotations
from typing import TYPE_CHECKING
from lark import Lark, Transformer as t
import lark
import os, sys
from context import Context
import parameter
import instruction
from dataclasses import dataclass

@dataclass
class ParseErr(Exception):
    msg:str
    line:int
    col:int
    colend:int
    hint:str=""

__dir__ = os.path.dirname(__file__)

class Transformer(t):
    def __init__(self, visit_tokens = True):
        super().__init__(visit_tokens)
    
    def get_const_or_label(self, name):
        if name in self.constants:
            return self.constants[name]
        elif name in self.labels:
            return self.labels[name]
        else:
            raise NameError(f"`{name}` is not defined")

    class Node:
        def __init__(self, value):pass
        
        def eval(self, context:Context=None):pass

        def __repr__(self):
            return f"<Invalid Node>"
        
        def get_first_token(self) -> lark.Token:
            return
        
        def get_last_token(self) -> lark.Token:
            return

    class Branch(Node):
        def __init__(self, value:list[Transformer.Node]):
            self.children = value
        
        def eval(self, context:Context):
            pass

        def get_first_token(self):
            tokens = [child.get_first_token() for child in self.children if child]
            tokens = list(filter(lambda c: isinstance(c,lark.Token), tokens))
            return tokens[0]
        
        def get_last_token(self):
            tokens = [child.get_last_token() for child in self.children if child]
            tokens = list(filter(lambda c: isinstance(c,lark.Token), tokens))
            return tokens[-1]
        
        def __repr__(self):
            return f"{self.__class__.__name__}({self.children})"
    
    class Leaf(Node):
        def __init__(self, token):
            self.value = token.value
            self.token = token
        
        def eval(self):
            return self.value
        
        def get_first_token(self):
            return self.token
        
        def get_last_token(self):
            return self.token
        
        def __repr__(self):
            return f"{self.__class__.__name__}({self.value})"

    class start(Branch):
        def __repr__(self):
            return " ".join([repr(value) for value in self.children])
        
        def eval(self, context):
            codegens = [child for child in self.children if isinstance(child,Transformer.codegen_block)]
            non_codegens = [child for child in self.children if child not in codegens]

            for child in non_codegens:
                child.eval(context)

            self.functions = [child for child in self.children if isinstance(child,Transformer.code_block)]
            self.data = [child for child in self.children if isinstance(child,Transformer.data_block)]

            for func in self.functions:
                func.eval(context)
            for part in self.data:
                part.eval(context)
        
        def collect(self, context:Context):
            for func in self.functions:
                func.collect(context)
            for part in self.data:
                part.collect(context)
        
        def emit(self):
            out = []

            for func in self.functions:
                out.append(func.emit())
            for part in self.data:
                out.append(part.emit())
            
            return b"".join(out)

    def transform(self, tree) -> start:
        return super().transform(tree)

    class codegen_block(Branch):
        def __init__(self, value):
            self.name = value[0]
            self.children = value[1:]

        def eval(self, context):
            if self.name:
                self.name = self.name.eval()
                context.add_label(self.name)
            self.codegens = [child for child in self.children if isinstance(child,Transformer.codegen)]
            self.non_codegens = [child for child in self.children if child not in self.codegens]

            for child in self.non_codegens:
                child.eval(context)
            
            for child in self.codegens:
                child.eval(context)
        
        def collect(self, context):
            for item in self.codegens:
                item.collect(context)
        
        def emit(self):
            out = b""
            for item in self.codegens:
                out += item.emit()
            return out
    class codegen(Branch):
        def __init__(self, value):
            super().__init__(value)
            self.value = self.children[0]

        def eval(self, context:Context):
            pass

        def collect(self, context:Context):
            pass
        
        def emit(self):
            return b""

    class code_block(codegen_block):
        def eval(self, context):
            super().eval(context)

        def __repr__(self):
            return "code " + repr(self.name) + "{" + "; ".join([repr(value) for value in self.children]) + "}"

    class data_block(codegen_block):

        def __repr__(self):
            return "data " + repr(self.name) + "{" + ", ".join([repr(value) for value in self.children]) + "}"

    class instruction(codegen):
        def __init__(self, value):
            super().__init__(value)
            self.command = self.children[0]
            self.args:list[Transformer.Parameter] = self.children[1:]

        def eval(self, context):
            comtok:lark.Token = self.command.token
            self.command = self.command.eval()
            tmp_args = []
            for child in self.args:
                tmp_args.append(child.dry_eval())
            try:
                dryinst = instruction.Instruction.from_str(self.command,tmp_args).get(0)
            except SyntaxError:
                raise ParseErr(f"unknown instruction '{self.command}'",comtok.line-1,comtok.column-1,comtok.end_column-1)
            self.position = context.get_pc()
            if not isinstance(dryinst,instruction.Err):
                context.inc_pc(len(dryinst))
            else:
                err_begin = self.args[dryinst.pos].get_first_token()
                err_end = self.args[dryinst.pos].get_last_token()
                raise ParseErr(dryinst.msg, err_begin.line-1, err_begin.column-1,err_end.end_column-1,dryinst.hint)

        def collect(self, context):
            processed_args = []

            for child in self.args:
                processed_args.append(child.eval(context))
            self.out = instruction.Instruction.from_str(self.command, processed_args).get(self.position)
            if isinstance(self.out, instruction.Err):
                err_begin = self.args[self.out.pos].get_first_token()
                err_end = self.args[self.out.pos].get_last_token()
                raise ParseErr(self.out.msg, err_begin.line-1, err_begin.column-1,err_end.end_column-1,self.out.hint)

        def emit(self):
            return self.out

        def __repr__(self):
            return f"{self.command}({", ".join([repr(value) for value in self.args])})"

    class text(codegen):
        value:Transformer.STRING
        def __repr__(self):
            return f".ascii {self.children[0]}"
        def eval(self, context):
            self.text = self.value.eval()
            context.inc_pc(len(self.text))
        def collect(self, context):
            pass
        def emit(self):
            return self.text.encode('utf-8')
    
    class text_nulterm(text):
        def __repr__(self):
            return f".asciiz {self.children[0]}"
        def eval(self, context):
            super().eval(context)
            self.text = self.text + "\0"
            context.inc_pc(1)
        def emit(self):
            return self.text.encode('utf-8')
    
    class byte(codegen):
        value:Transformer.Leaf
        def __repr__(self):
            return f".byte {self.value}"
        def eval(self, context):
            context.inc_pc(1)
        def collect(self, context):
            self.out = self.value.eval(context).to_bytes(1)
        def emit(self):
            return self.out
    class word(codegen):
        def __repr__(self):
            return f".word {self.value}"
        def eval(self, context):
            context.inc_pc(2)
        def collect(self, context):
            self.out = self.value.eval(context).to_bytes(2, byteorder='little')
        def emit(self):
            return self.out
    class double(codegen):
        def __repr__(self):
            return f".double {self.value}"
        def eval(self, context):
            context.inc_pc(4)
        def collect(self, context):
            self.out = self.value.eval(context).to_bytes(4, byteorder='little')
        def emit(self):
            return self.out
    class quad(codegen):
        def __repr__(self):
            return f".quad {self.value}"
        def eval(self, context):
            context.inc_pc(8)
        def collect(self, context):
            self.out = self.value.eval(context).to_bytes(8, byteorder='little')
        def emit(self):
            return self.out

    class zero(codegen):
        def eval(self, context):
            context.inc_pc(self.children[0].eval(context))
        def collect(self, context):
            self.out = b"\0" * self.children[0].eval(context)
        def emit(self):
            return self.out

    class org(codegen):
        def eval(self, context):
            context.inc_pc(self.children[0].eval(context) - context.get_pc())

    class Parameter(Branch):pass

    class register(Parameter):
        def __init__(self, value):
            super().__init__(value)
        def __repr__(self):
            return f"register {self.children[0]}"
        
        def dry_eval(self):
            return parameter.Register(0)

        def eval(self, context):
            return parameter.Register(self.children[0].eval())
    class immediate(Parameter):
        def __repr__(self):
            return f"immediate {self.children[0]}"
        def dry_eval(self):
            return parameter.Immediate(0)
        def eval(self, context):
            return parameter.Immediate(self.children[0].eval(context))
    class direct_addr(Parameter):
        def __init__(self, value):
            super().__init__(value)
            self.size:Transformer.ADDR_SIZE = value[0]
            self.base:Transformer.BASES = value[1]
            self.sign = value[2]
            self.addr:Transformer.expr = value[3]
            if self.size:
                self.size = self.size.eval()
            else:
                self.size = None
        def __repr__(self):
            return f"deref {self.base} {self.sign} {self.addr}"
        def dry_eval(self):
            return parameter.Dereference(0,self.size,1)
        def eval(self, context):
            addr = self.addr.eval(context)
            if self.base:
                base = self.base.eval()
            else:
                base = 1
            return parameter.Dereference(addr,self.size,base)
        def get_first_token(self):
            if self.children[0]:
                return self.children[0].get_first_token()
            else:
                return self.children[1].get_first_token()
    class indirect_addr(Parameter):
        def __init__(self, value):
            super().__init__(value)
            self.size:Transformer.ADDR_SIZE|None = value[0]
            self.base:Transformer.REGISTER = value[1]
        def __repr__(self):
            return f"deref {self.base} + BX"
        def dry_eval(self):
            return parameter.IndirectDereference(0,0)
        def eval(self, context):
            if self.size:
                size = self.size.eval()
            else:
                size = None
            if self.base:
                base = self.base.eval()
            else:
                base = 1
            return parameter.IndirectDereference(base,size)

    class constantdef(Branch):
        def __init__(self, value):
            super().__init__(value)
            self.name:Transformer.IDENTIFIER = self.children[0]
            self.val:Transformer.expr = self.children[1]
        def __repr__(self):
            return f"{self.name} = {self.val}"
        
        def eval(self, context):
            name = self.name.eval()
            if context.get_local(name):
                raise SyntaxError(f"{name} already defined in this scope")

            context.set(name,self.val.eval(context))
        
    class labeldef(codegen):
        def __repr__(self):
            return f"label {self.children[0]}"
        
        def eval(self, context):
            context.add_label(self.children[0].eval())

    class expr(Branch):
        def __init__(self, value):
            if len(value) == 2:
                self.lhs = value[0]
                self.rhs = value[1]
            else:
                self.rhs = value[0]

    class or_op(expr):
        def __repr__(self):
            return f"({self.lhs} | {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) | self.rhs.eval(context)
    class xor_op(expr):
        def __repr__(self):
            return f"({self.lhs} ^ {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) ^ self.rhs.eval(context)
    class and_op(expr):
        def __repr__(self):
            return f"({self.lhs} & {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) & self.rhs.eval(context)
    class not_op(expr):
        def __repr__(self):
            return f"(~ {self.rhs})"
        def eval(self, context):
            return ~self.rhs.eval(context)
    
    class shiftr(expr):
        def __repr__(self):
            return f"({self.lhs} >> {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) >> self.rhs.eval(context)
    class shiftl(expr):
        def __repr__(self):
            return f"({self.lhs} << {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) << self.rhs.eval(context)
    
    class add(expr):
        def __repr__(self):
            return f"({self.lhs} + {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) + self.rhs.eval(context)
    class sub(expr):
        def __repr__(self):
            return f"({self.lhs} - {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) - self.rhs.eval(context)
    
    class mul(expr):
        def __repr__(self):
            return f"({self.lhs} * {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) * self.rhs.eval(context)
    class div(expr):
        def __repr__(self):
            return f"({self.lhs} / {self.rhs})"
        def eval(self, context):
            return self.lhs.eval(context) // self.rhs.eval(context)
    
    class unary_sub(expr):
        def __repr__(self):
            return f"(- {self.rhs})"
        def eval(self, context):
            return - self.rhs.eval(context)

    class literal(Branch):
        def __init__(self, value:Transformer.Leaf):
            super().__init__(value)
            self.val = self.children[0]
        def __repr__(self):
            return f"lit {self.val}"
        def eval(self, context):
            return self.val.eval()
    
    class symbol(Branch):
        def __repr__(self):
            return f"symbol {self.children[0]}"
        def eval(self, context):
            name = self.children[0].eval()
            return context.get(name)

    class IDENTIFIER(Leaf):
        def __repr__(self):
            return f"identifer {self.value}"

    class REGISTER(Leaf):
        def eval(self):
            return ['ax','bx','cx','dx'
                    'cs','ds','ss','es'
                    'ip','sp','bp'].index(self.value.lower())
    
    class SIGN(Leaf):
        def eval(self):
            return 1 if self.value == "+" else -1
    
    class BASES(Leaf):
        def eval(self):
            return ['cs','ds','ss','es',
                    'ip','sp','bp'].index(self.value.lower())

    class STRING(Leaf):
        def __init__(self,value:str):
            super().__init__(value)
            self.value = value[1:-1]
        def eval(self):
            self.value = self.value.replace(r"\n","\n").replace(r"\t","\t").replace(r"\\","\\").replace(r"\"","\"")
            return self.value
    class CHAR(STRING):
        def eval(self):
            super().eval()
            if len(self.value) != 1:
                raise ValueError("CHAR must be a single character")
            self.value = ord(self.value)
            return self.value

    class Number(Leaf):
        def __init__(self, token:lark.Token):
            token.value = token.value.replace("_","")
            super().__init__(token)

    class DECIMAL(Leaf):
        def eval(self):
            return int(self.value)
    class BINARY(Leaf):
        def eval(self):
            return int(self.value,base=2)
    class OCTAL(Leaf):
        def eval(self):
            return int(self.value,base=8)
    class HEX(Leaf):
        def eval(self):
            return int(self.value,base=16)
    
    class ADDR_SIZE(DECIMAL):
        def eval(self):
            return ["b","w","d","q"].index(self.value.lower())


class Parser:
    def __init__(self):
        self.grammar = open(os.path.join(__dir__,"grammar.lark")).read()
        self.parser = Lark(
            self.grammar,
        )
        self.transformer = Transformer()
    def parse(self, code:str, filename="<main>"):
        transformer = self.transformer
        parser = self.parser

        parsedTree = parser.parse(code)

        tree = transformer.transform(parsedTree)

        return tree

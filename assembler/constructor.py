from __future__ import annotations
from typing import TYPE_CHECKING
from context import Context
from parser import Transformer

class Constructor:
    def __init__(self):
        self.globals = Context()

    def main(self,ast:Transformer.start,filename="<main>") -> bytes:

        ast.eval(self.globals)

        ast.collect(self.globals)

        return ast.emit()

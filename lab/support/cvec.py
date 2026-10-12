"""The forms `expose_allocation` introduces.

A tuple literal does not survive to the back end: `expose_allocation` splits it
into reserving space and then filling it in.  `Allocate` is the reserving half;
the filling in is ordinary assignment to a `Subscript`, which `ast` already
gives us.

`Begin` and `Goto` still come from cif.py, and the definitions from cfun.py --
this module only adds what tuples need.
"""
from ast import expr
from dataclasses import dataclass


@dataclass
class Allocate(expr):
    """Reserve room for a tuple of `length` elements, uninitialised.

    Never collects and never fails: it assumes the space is already there.
    Whoever emits it is responsible for having made sure of that.
    """
    length: int
    __match_args__ = ("length",)

    def __str__(self):
        return f"allocate({self.length})"

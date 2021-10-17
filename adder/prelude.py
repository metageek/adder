from adder.env import Env
from adder.symbol import Symbol, intern

def total(*args):
    return sum(args)

def prod(*args):
    res=1
    for a in args:
        res *= a
    return res

def minus(*args):
    if not args:
        return 0
    if len(args) == 1:
        return -args[0]
    
    res=args[0]
    for a in args[1:]:
        res -= a
    return res

def divide(*args):
    if not args:
        raise ZeroDivisionError()
    if len(args) == 1:
        return 1/args[0]
    
    res=args[0]
    for a in args[1:]:
        res /= a
    return res

def make():
    return {'+': total,
            '*': prod,
            '-': minus,
            '/': divide,
            'print': print}

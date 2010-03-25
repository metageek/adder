# Standard env for Gomer.  Subset of the Adder stdenv, with no macros.

from adder.common import Symbol as S
from adder.gomer import *
import adder.common

def plus(*args):
    return sum(args)

def minus(first,*rest):
    if rest:
        return first-sum(rest)
    else:
        return -first

def times(*args):
    res=1
    for a in args:
        res*=a
    return res

def fdiv(first,*rest):
    if rest:
        return first/times(*rest)
    else:
        return 1/first

def idiv(first,*rest):
    if rest:
        return first//times(*rest)
    else:
        return 1//first

def mod(a,b):
    return a%b

def inF(a,b):
    return a in b

def raiseF(e):
    raise e

def getitem(l,i):
    return l[i]

def slice(l,a,b=None):
    if b is None:
        return l[a:]
    else:
        return l[a:b]

def cmpN(cmp2):
    def f(*args):
        if not args:
            return True
        prev=args[0]
        for a in args[1:]:
            if not cmp2(prev,a):
                return False
            prev=a
        return True
    return f

lt=cmpN(lambda a,b: a<b)
gt=cmpN(lambda a,b: a>b)
le=cmpN(lambda a,b: a<=b)
ge=cmpN(lambda a,b: a>=b)

eq=cmpN(lambda a,b: a==b)

def ne(*args):
    return not eq(*args)


def mkStdEnv():
    scope=Scope(None)
    env=Env(scope,None)

    functions=[
        ('==',eq,True),
        ('!=',ne,True),
        ('<',lt,True),
        ('>',gt,True),
        ('<=',le,True),
        ('>=',ge,True),
        ('+',plus,True),
        ('-',minus,True),
        ('*',times,True),
        ('/',fdiv,True),
        ('//',idiv,True),
        ('%',mod,True),
        ('in',inF,True),
        ('raise',raiseF,False),
        ('print',print,False),
        ('gensym',adder.common.gensym,False),
        ('[]',getitem,False), # impure for arb objects
        ('slice',slice,False), # probably impure for arb objects
        ]
    specials=[]

    for (name,f,pure) in functions:
        scope.addDef(S(name),Constant(scope,NativeFunction(f,pure)))

    for (name,f) in []:
        scope.addDef(S(name),Constant(scope,NativeFunction(f,False,
                                                           special=True)))

    return (scope,env)

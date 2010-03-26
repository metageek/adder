# Standard env for Gomer.  Subset of the Adder stdenv, with no macros.

from adder.common import Symbol as S
from adder.gomer import *
import adder.common

def cmpNF(cmp2):
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

ltF=cmpNF(lambda a,b: a<b)
gtF=cmpNF(lambda a,b: a>b)
leF=cmpNF(lambda a,b: a<=b)
geF=cmpNF(lambda a,b: a>=b)

eqF=cmpNF(lambda a,b: a==b)

def neF(*args):
    return not eqF(*args)

def plusF(*args):
    return sum(args)

def minusF(first,*rest):
    if rest:
        return first-sum(rest)
    else:
        return -first

def timesF(*args):
    res=1
    for a in args:
        res*=a
    return res

def fdivF(first,*rest):
    if rest:
        return first/timesF(*rest)
    else:
        return 1/first

def idivF(first,*rest):
    if rest:
        return first//timesF(*rest)
    else:
        return 1//first

def modF(a,b):
    return a%b

def inF(a,b):
    return a in b

def raiseF(e):
    raise e

def getitemF(l,i):
    return l[i]

def sliceF(l,a,b=None):
    if b is None:
        return l[a:]
    else:
        return l[a:b]

def reverseF(l):
    l2=list(l)
    l2.reverse()
    return l2

def mkStdEnv():
    scope=Scope(None)
    env=Env(scope,None)

    functions=[
        ('==',eqF,True),
        ('!=',neF,True),
        ('<',ltF,True),
        ('>',gtF,True),
        ('<=',leF,True),
        ('>=',geF,True),
        ('+',plusF,True),
        ('-',minusF,True),
        ('*',timesF,True),
        ('/',fdivF,True),
        ('//',idivF,True),
        ('%',modF,True),
        ('in',inF,True),
        ('raise',raiseF,False),
        ('print',print,False),
        ('gensym',adder.common.gensym,False),
        ('[]',getitemF,False), # impure for arb objects
        ('slice',sliceF,False), # probably impure for arb objects
        ('list',list,True),
        ('tuple',tuple,True),
        ('set',set,True),
        ('isinstance',isinstance,True),
        ('mk-list',lambda *a: list(a),True),
        ('mk-tuple',lambda *a: a,True),
        ('mk-set',lambda *a: set(a),True),
        ('mk-dict',lambda *a: dict(a),True),
        ('reverse',reverseF,True),
        ('reverse!',lambda l: l.reverse(),False),
        ]
    specials=[]

    for (name,f,pure) in functions:
        scope.addDef(S(name),Constant(scope,NativeFunction(f,pure)))

    for (name,f) in []:
        scope.addDef(S(name),Constant(scope,NativeFunction(f,False,
                                                           special=True)))

    return (scope,env)

# Standard env for Gomer.  Subset of the Adder stdenv, with no macros.

import sys

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

def getitemF(l,i):
    return l[i]

def sliceF(l,a,b=None):
    if b is None:
        return l[a:]
    else:
        return l[a:b]

def evalGomerF(expr,env):
    return build(env.scope,expr).evaluate(env)

def ifSF(env,cond,thenClause,elseClause=None):
    if cond.evaluate(env):
        return thenClause.evaluate(env)
    else:
        if elseClause:
            return elseClause.evaluate(env)
        else:
            return None

def mkStdEnv():
    scope=Scope(None)
    env=Env(scope,None)

    functions=[
        ('in',inF,True),
        ('print',print,False),
        ('gensym',adder.common.gensym,False),
        ('[]',getitemF,False), # impure for arb objects
        ('getattr',getattr,False), # ditto
        ('slice',sliceF,False), # probably ditto
        ('list',list,True),
        ('tuple',tuple,True),
        ('set',set,True),
        ('isinstance',isinstance,True),
        ('mk-list',lambda *a: list(a),True),
        ('mk-tuple',lambda *a: a,True),
        ('mk-set',lambda *a: set(a),True),
        ('mk-dict',lambda *a: dict(a),True),
        ('eval-gomer',evalGomerF,False),
        ('apply',lambda f,args: f(*args),False),
        ]

    for (name,f,pure) in functions:
        scope.addDef(S(name),Constant(scope,NativeFunction(f,pure)))

    for (name,value) in [
        ('stdin',sys.stdin),
        ('stdout',sys.stdout),
        ('stderr',sys.stderr),
        ('true',True),
        ('false',False),
        ('list-type',list),
        ('tuple-type',tuple),
        ('set-type',set),
        ('dict-type',dict),
        ]:
        scope.addDef(S(name),Constant(scope,value))

    return (scope,env)

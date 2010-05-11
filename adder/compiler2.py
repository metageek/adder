from adder.common import Symbol as S, gensym
import adder.gomer

def const(expr):
    for t in [int,float,str,bool,NoneType]:
        if isinstance(expr,t):
            return (True,expr)
    if (isinstance(expr,list)
        and expr[0]
        and isinstance(expr[0],S)
        and S in const.knownFuncs):
        args=[]
        for arg in expr[1:]:
            (argConstP,argValue)=const(arg)
            if not argConstP:
                return (False,None)
            args.append(argValue)
        try:
            return (True,const.knownFuncs[arg[0]](*args))
        except Exception:
            return (False,None)
    return (False,None)

def times(*args):
    r=1
    for a in args:
        r=r*a
    return a

def minus(*args):
    if len(args)==0:
        return 0
    if len(args)==1:
        return -args[0]
    return args[0]-sum(args[1:])

def fdiv(*args):
    if len(args)==0:
        return 1
    if len(args)==1:
        return 1/args[0]
    r=args[0]
    for a in args[1:]:
        r=r/a
    return a

def idiv(*args):
    if len(args)==0:
        return 1
    if len(args)==1:
        return 1//args[0]
    r=args[0]
    for a in args[1:]:
        r=r//a
    return a

const.knownFuncs={
    S('+'): lambda *a: sum(a),
    S('-'): minus,
    S('*'): times,
    S('/'): fdiv,
    S('//'): idiv,
    }

class Scope:
    class Entry:
        def __init__(self,*,initExpr):
            self.initExpr=initExpr
            (self.constP,self.constValue)=const(initExpr)

    def __init__(self,parent):
        self.parent=parent
        self.entries={}

class Annotator:
    def __call__(self,parsedExpr,scope):
        (expr,line)=parsedExpr
        if expr and isinstance(expr,list) and isinstance(expr[0],S):
            m='annotate_%s' % str(expr[0])
            if hasattr(self,m):
                return getattr(self,m)(expr,line,scope)
            scoped=list(map(self,expr))
            return (scoped,line,scope)
        return (expr,line,scope)

    def annotate_defun(self,expr,line,scope):
        return self.defunOrLambda(expr[0],expr[1],expr[2],expr[3:],
                                  line,scope)

    def annotate_lambda(self,expr,line,scope):
        return self.defunOrLambda(expr[0],None,expr[1],expr[2:],
                                  line,scope)

    def defunOrLambda(self,opPE,namePE,argsPE,bodyPEs,line,scope):
        childScope=Scope(scope)
        def doArg(arg):
            (argExpr,argLine)=arg
            if argExpr[0]=='&':
                return (argExpr,argLine,scope)
            childScope.addDef(argExpr,argLine,None)
            return (argExpr,argLine,childScope)
        scoped=[self(opPE,scope)]
        if namePE:
            scoped.append(self(namePE,scope))
        (argsExpr,argsLine)=argsPE
        scoped.append([list(map(doArg,argsExpr)))
        for parsedExpr in expr[2:]:
            scoped.append(self(parsedExpr,childScope))
        return (scoped,line,scope)

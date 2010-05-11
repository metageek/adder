import pdb
from adder.common import Symbol as S, gensym
import adder.gomer

def const(expr):
    if isinstance(expr,tuple):
        expr=expr[0]
    if expr is None:
        return (True,expr)
    for t in [int,float,str,bool]:
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

class Undefined(Exception):
    def __init__(self,sym):
        Exception.__init__(self,sym)

    def __str__(self):
        return 'Undefined variable: %s' % self.args

class Redefined(Exception):
    def __init__(self,var,initExpr,oldEntry):
        Exception.__init__(self,var,initExpr,oldEntry)

    def __str__(self):
        return 'Variable redefined: %s defined as %s after being defined at %s' % self.args

class Scope:
    class Entry:
        def __init__(self,*,initExpr,line):
            self.initExpr=initExpr
            (self.constP,self.constValue)=const(initExpr)
            self.line=line

    nextId=1

    def __init__(self,parent,*,isRoot=False):
        self.entries={}
        id=None

        if parent is None:
            if isRoot:
                self.parent=None
                id=0
            else:
                self.parent=Scope.root
        else:
            self.parent=parent

        if id is None:
            self.id=Scope.nextId
            Scope.nextId+=1
        else:
            self.id=id

    root=None

    def addDef(self,name,initExpr,line):
        if name in self.entries:
            raise Redefined(name,initExpr,self.entries[name])
        self.entries[name]=Scope.Entry(initExpr=initExpr,
                                       line=line)

    def __iter__(self):
        cur=self
        already=set()
        while cur is not None:
            for key in self.entries:
                if key not in already:
                    already.add(key)
                    yield key
            cur=cur.parent

    def __len__(self):
        cur=self
        already=set()
        res=0
        while cur is not None:
            for key in self.entries:
                if key not in already:
                    already.add(key)
                    res+=1
            cur=cur.parent
        return res

    def __getitem__(self,key):
        cur=self
        while cur is not None:
            if key in cur.entries:
                return cur.entries[key]
            cur=cur.parent
        raise Undefined(key)

    def requiredScope(self,sym):
        if sym in self.entries:
            return self
        if self.parent is not None:
            return self.parent.requiredScope(sym)
        raise Undefined(sym)

Scope.root=Scope(None,isRoot=True)
for name in ['+','-','*','/','//','%',
             'defun','lambda','defvar','scope'
             ]:
    Scope.root.addDef(S(name),None,0)

class Annotator:
    def __call__(self,parsedExpr,scope):
        try:
            (expr,line)=parsedExpr
        except ValueError as ve:
            print(ve,parsedExpr)
            raise
        if expr and isinstance(expr,list) and isinstance(expr[0][0],S):
            m='annotate_%s' % str(expr[0][0])
            if hasattr(self,m):
                return getattr(self,m)(expr,line,scope)
            scoped=list(map(lambda e: self(e,scope),expr))
            return (scoped,line,scope)
        if isinstance(expr,S):
            return (expr,line,scope.requiredScope(expr))
        return (expr,line,scope)

    def annotate_scope(self,expr,line,scope):
        scopedScope=self(expr[0],scope)
        childScope=Scope(scope)
        scopedChildren=list(map(lambda e: self(e,childScope),expr[1:]))
        return ([scopedScope]+scopedChildren,line,scope)

    def annotate_defvar(self,expr,line,scope):
        scopedDefvar=self(expr[0],scope)
        scopedInitExpr=self(expr[2],scope)
        scope.addDef(expr[1][0],scopedInitExpr,expr[1][1])
        scopedVar=self(expr[1],scope)
        return ([scopedDefvar,scopedVar,scopedInitExpr],line,scope)

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
            scope.addDef(namePE[0],namePE[1],None)
            scoped.append(self(namePE,scope))
        (argsExpr,argsLine)=argsPE
        scoped.append((list(map(doArg,argsExpr)),argsLine,scope))
        for parsedExpr in bodyPEs:
            scoped.append(self(parsedExpr,childScope))
        return (scoped,line,scope)

    def annotate_scope(self,expr,line,scope):
        childScope=Scope(scope)
        return (([self(expr[0],scope)]
                 +list(map(lambda e: self(e,childScope),
                           expr[1:]))
                 ),
                line,scope)

annotate=Annotator()

def stripAnnotations(annotated):
    (expr,line,scope)=annotated
    if isinstance(expr,S) and scope.id>0:
        return S('%s-%d' % (str(expr),scope.id))
    if not isinstance(expr,list):
        return expr
    return list(map(stripAnnotations,expr))

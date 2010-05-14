import pdb
from adder.common import Symbol as S, gensym, q
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
        ):
        if S in const.knownFuncs:
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
        if S==S('quote'):
            assert len(expr)==2
            return (True,expr[1])
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

class AssignedToConst(Exception):
    def __init__(self,var):
        Exception.__init__(self,var)

    def __str__(self):
        return 'Assigning to constant: %s' % self.args

class Scope:
    class Entry:
        def __init__(self,*,initExpr,line,asConst=False,ignoreScopeId=False):
            self.initExpr=initExpr
            if initExpr is None:
                (self.constValueValid,self.constValue)=(False,None)
            else:
                (self.constValueValid,self.constValue)=const(initExpr)
            self.line=line
            self.asConst=asConst
            self.ignoreScopeId=ignoreScopeId

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
        self.readOnly=False

        self.addConst(S('current-scope'),self,0,ignoreScopeId=True)

    root=None

    def addDef(self,name,initExpr,line,*,asConst=False,ignoreScopeId=False):
        assert not self.readOnly
        if name in self.entries:
            raise Redefined(name,initExpr,self.entries[name])
        self.entries[name]=Scope.Entry(initExpr=initExpr,
                                       line=line,
                                       asConst=asConst,
                                       ignoreScopeId=ignoreScopeId)

    def addConst(self,name,value,line,*,ignoreScopeId=False):
        self.addDef(name,q(value),line,
                    asConst=True,
                    ignoreScopeId=ignoreScopeId)

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
for name in ['defun','lambda','defvar','scope',
             'quote','import',
             'if','while','break','continue','begin',
             'yield', 'return','raise',
             'and','or',':=','.',
             'defconst',
             '==','!=','<=','<','>=','>',
             '+','-','*','/','//','%','in',
             'print','gensym','[]','getattr','slice','isinstance',
             'list','tuple','set','dict',
             'mk-list','mk-tuple','mk-set','mk-dict','mk-symbol',
             'reverse','stdenv','apply','eval','exec-py','load',
             'getScopeById','globals','locals',
             # All before this point are annotated.
             'defmacro','python',
             ]:
    Scope.root.addDef(S(name),None,0)

Scope.root.addConst(S('true'),True,0)
Scope.root.addConst(S('false'),False,0)
Scope.root.addConst(S('none'),None,0)
Scope.root.readOnly=True

class Annotator:
    pynamesForSymbols={'.': 'dot', ':=': 'assign'}
    def methodFor(self,f):
        s=str(f)
        if s in Annotator.pynamesForSymbols:
            s=Annotator.pynamesForSymbols[s]
        return 'annotate_%s' % s.replace('-','_')

    def __call__(self,parsedExpr,scope):
        try:
            (expr,line)=parsedExpr
        except ValueError as ve:
            print(ve,parsedExpr)
            raise
        if expr and isinstance(expr,list):
            if isinstance(expr[0][0],S):
                f=expr[0][0]
                if scope.requiredScope(f) is Scope.root:
                    m=self.methodFor(f)
                    if hasattr(self,m):
                        return getattr(self,m)(expr,line,scope)
            scoped=list(map(lambda e: self(e,scope),expr))
            return (scoped,line,scope)
        if isinstance(expr,S):
            if expr.isKeyword():
                return (expr,line,Scope.root)
            else:
                if str(expr)=='current-scope':
                    adder.runtime.getScopeById.scopes[scope.id]=scope
                    return self(([(S('getScopeById'),line),
                                  (scope.id,line)],line),scope)
                required=scope.requiredScope(expr)
                entry=required[expr]
                if (entry.asConst
                    and entry.constValueValid
                    and (isinstance(entry.constValue,int)
                         or isinstance(entry.constValue,float)
                         or isinstance(entry.constValue,str)
                         or isinstance(entry.constValue,bool)
                         )
                    ):
                    expr=entry.constValue
                return (expr,line,required)
        return (expr,line,scope)

    def annotate_assign(self,expr,line,scope):
        assert len(expr)==3
        (lhs,lhsLine)=expr[1]
        if isinstance(lhs,S):
            entry=scope[lhs]
            if entry.asConst:
                raise AssignedToConst(lhs)
        return (list(map(lambda e: self(e,scope),expr)),line,scope)
    
    def annotate_eval(self,expr,line,scope):
        assert len(expr)>=2 and len(expr)<=4
        adderArg=self(expr[1],scope)
        scopeArg=self((S('current-scope'),line),scope)
        if len(expr)>=3:
            globalArg=self(expr[2],scope)
        else:
            globalArg=self(([(S('globals'),line)],line),scope)
        if len(expr)>=4:
            localArg=self(expr[3],scope)
        else:
            localArg=self(([(S('locals'),line)],line),scope)
        return ([self(expr[0],scope),
                 adderArg,scopeArg,globalArg,localArg],line,scope)

    def annotate_exec_py(self,expr,line,scope):
        assert len(expr)>=2 and len(expr)<=4
        pyArg=self(expr[1],scope)
        if len(expr)>=3:
            globalArg=self(expr[2],scope)
        else:
            globalArg=self(([(S('globals'),line)],line),scope)
        if len(expr)>=4:
            localArg=self(expr[3],scope)
        else:
            localArg=self(([(S('locals'),line)],line),scope)
        return ([self(([(S('.'),line),
                        (S('python'),line),
                        (S('exec'),line)],
                       line),scope),
                 pyArg,globalArg,localArg],line,scope)

    def annotate_scope(self,expr,line,scope):
        scopedScope=self(expr[0],scope)
        childScope=Scope(scope)
        scopedChildren=list(map(lambda e: self(e,childScope),expr[1:]))
        return ([scopedScope]+scopedChildren,line,scope)

    def annotate_quote(self,expr,line,scope):
        return self.quoteOrImport(expr,line,scope,True)

    def annotate_import(self,expr,line,scope):
        res=self.quoteOrImport(expr,line,scope,False)
        for (pkg,pkgLine) in expr[1:]:
            scope.addDef(S(str(pkg).split('.')[0]),None,pkgLine,
                         ignoreScopeId=True)
        return res

    def quoteOrImport(self,expr,line,scope,justOneArg):
        def annotateDumbly(parsedExpr):
            try:
                (expr,line)=parsedExpr
            except ValueError as ve:
                print(ve,parsedExpr)
                raise
            if isinstance(expr,list):
                return [list(map(annotateDumbly,expr)),line,scope]
            else:
                return (expr,line,scope)

        if justOneArg:
            assert len(expr)==2
            args=[expr[1]]
        else:
            args=expr[1:]
            
        return (([self(expr[0],scope)]
                 +list(map(annotateDumbly,args))
                 ),
                line,scope)

    def annotate_dot(self,expr,line,scope):
        def annotateDumbly(parsedExpr):
            (expr,line)=parsedExpr
            assert isinstance(expr,S)
            return (expr,line,scope)

        return (([self(expr[0],scope),
                  self(expr[1],scope)
                  ]
                 +list(map(annotateDumbly,expr[2:]))
                 ),
                line,scope)

    def annotate_defvar(self,expr,line,scope):
        return self.defvarOrDefconst(expr,line,scope,False)

    def annotate_defconst(self,expr,line,scope):
        return self.defvarOrDefconst(expr,line,scope,True)

    def defvarOrDefconst(self,expr,line,scope,asConst):
        scopedDef=self((S(':='),expr[0][1]),scope)
        scopedInitExpr=self(expr[2],scope)
        scope.addDef(expr[1][0],scopedInitExpr,expr[1][1],asConst=asConst)
        scopedVar=(expr[1][0],expr[1][1],scope)
        return ([scopedDef,
                 scopedVar,scopedInitExpr],line,scope)

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
        return (([(S('begin'),expr[0][1],Scope.root)]
                 +list(map(lambda e: self(e,childScope),
                           expr[1:]))
                 ),
                line,scope)

annotate=Annotator()

def stripAnnotations(annotated,*,quoted=False):
    try:
        (expr,line,scope)=annotated
    except ValueError as ve:
        print(ve,annotated)
        raise
    if (not quoted
        and isinstance(expr,S)
        and scope.id>0
        and not scope[expr].ignoreScopeId):
        return S('%s-%d' % (str(expr),scope.id))
    if not (expr and isinstance(expr,list)):
        return expr
    if not quoted and expr[0][0] in [S('quote'),S('import')]:
        return ([expr[0][0]]
                +list(map(lambda e: stripAnnotations(e,quoted=True),expr[1:]))
                )
    if not quoted and expr[0][0]==S('.'):
        return ([expr[0][0],
                 stripAnnotations(expr[1])]
                 +list(map(lambda e: stripAnnotations(e,quoted=True),
                           expr[2:]))
                )
    return list(map(lambda e: stripAnnotations(e,quoted=quoted),expr))

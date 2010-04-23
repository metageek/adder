# A structured internal representation; basically an annotated form of
#  Adder itself, with macros expanded.  Gets converted to Pyle.
#  Includes a basic interpreter, for use in macro expansion.

import itertools,functools,re,pdb,adder.pyle,sys
from adder.common import Symbol as S, gensym

def q(x):
    return [S('quote'),x]

def qpy(x):
    return [S('quote'),[x]]

class NoCommonAncestor(Exception):
    def __str__(self):
        return 'The two scopes have no common ancestor.'

class NotConstant(Exception):
    def __init__(self,expr):
        Exception.__init__(self,expr)
        self.expr=expr

    def __str__(self):
        return '%s is not a constant.' % self.args

class NotInitialized(Exception):
    def __init__(self,varName):
        Exception.__init__(self,varName)
        self.varName=varName

    def __str__(self):
        return "%s is not initialized; probably it's a function arg." % self.args

class Undefined(Exception):
    def __init__(self,varRef):
        Exception.__init__(self,varRef)
        self.varRef=varRef

    def __str__(self):
        return 'Undefined variable: %s' % self.args

class KeywordsHaveNoValue(Exception):
    def __init__(self,varRef):
        Exception.__init__(self,varRef)
        self.varRef=varRef

    def __str__(self):
        return 'Cannot use a keyword as a value: %s' % str(self.varRef.name)

class TwoConsecutiveKeywords(Exception):
    def __init__(self,varRef1,varRef2):
        Exception.__init__(self,varRef1,varRef2)
        self.varRef1=varRef1
        self.varRef2=varRef2

    def __str__(self):
        return 'Two consecutive keywords: %s, %s' % self.args

class KeywordWithNoArg(Exception):
    def __init__(self,varRef):
        Exception.__init__(self,varRef)
        self.varRef=varRef

    def __str__(self):
        return 'Keyword at end of arglist: %s' % self.args

class DefinedAfterUse(Exception):
    def __init__(self,var,initExpr,accesses):
        Exception.__init__(self,var,initExpr,accesses)

    def __str__(self):
        return 'Variable defined after use: %s defined as %s after used at %s' % self.args

class Redefined(Exception):
    def __init__(self,var,initExpr,oldVarEntry):
        Exception.__init__(self,var,initExpr,oldVarEntry)

    def __str__(self):
        return 'Variable redefined: %s defined as %s after being defined at %s' % self.args

class AssigningToConstant(Exception):
    def __init__(self,var):
        Exception.__init__(self,var)

    def __str__(self):
        return 'Assigning to constant %s' % self.args

# Information known about a variable
class VarEntry:
    def __init__(self,name,initExpr,*,dontDisambiguate=False,const=False):
        self.name=name
        self.initExpr=initExpr
        self.neverModified=True
        self.dontDisambiguate=dontDisambiguate
        self.const=const

    def markModified(self):
        assert not self.const
        self.neverModified=False

    def constValue(self):
        if not self.neverModified:
            raise NotConstant(None)
        if self.initExpr is None:
            raise NotInitialized(self.name)
        return self.initExpr.constValue()

# Table of vars  known in a lexical scope
class Scope:
    nextId=1
    def __init__(self,parent,*,isFunc=False):
        self.id=Scope.nextId
        Scope.nextId+=1

        if parent:
            assert parent.id<self.id

        self.parent=parent
        self.isFunc=isFunc

        self.funcYields=False

        self.localDefs={}
        self.varAccesses={}

        self.transglobal=set()

        if not parent:
            for (name,f) in [('defun',Defun()),
                             ('lambda',Lambda()),
                             ('defvar',Defvar()),
                             ('defconst',Defconst()),
                             (':=',Assignment()),
                             ('begin',Begin()),
                             ('block',Block()),
                             ('return',Return()),
                             ('yield',Yield()),
                             ('return-from',ReturnFrom()),
                             ('yield-from',YieldFrom()),
                             ('raise',Raise()),
                             ('reraise',Reraise()),
                             ('-gomer-try',Try()),
                             ('reverse',Reverse()),
                             ('stdenv',Stdenv()),
                             ('eval-py',EvalPy()),
                             ('exec-py',ExecPy()),
                             ('import',Import()),
                             ('if',If()),
                             ('while',While()),
                             ('.',Dot()),
                             ('+',Plus()),
                             ('-',Minus()),
                             ('*',Times()),
                             ('/',Div()),
                             ('//',IDiv()),
                             ]:
                self.addDef(S(name),Constant(self,f))
                self.transglobal.add(S(name))
            for name in ['%',
                         '<','>','<=','>=','==','!=',
                         'in','not',
                         'tuple','list','set','dict',
                         'mk-tuple','mk-list','mk-set','mk-dict',
                         'mk-symbol',
                         '[]','slice','getattr','isinstance',
                         'print','apply',
                         ]:
                self.addDef(S(name),Constant(self,
                                             PyleExpr(self,name)))
                self.transglobal.add(S(name))

            for name in ['break','continue',
                         ]:
                self.addDef(S(name),Constant(self,
                                             PyleStmt(self,name)))
                self.transglobal.add(S(name))

            for (name,value) in [('true',True),
                                 ('false',False),
                                 ('None',None),
                                 ]:
                self.addDef(S(name),Constant(self,value),const=True)
                self.transglobal.add(S(name))

    def nearestFuncAncestor(self):
        cur=self
        while cur and not (cur.isFunc):
            cur=cur.parent
        return cur

    def isPyGlobal(self):
        cur=self
        while cur.parent:
            if cur.isFunc:
                return False
            cur=cur.parent
        return True

    Local=1
    Nonlocal=2
    Global=3

    # Which access is needed in this scope to get at the given var scope?
    #  Returns None if impossible.
    def accessMode(self,varScope):
        cur=self
        crossedFunctionBoundary=False
        while cur and cur is not varScope:
            if cur.isFunc:
                crossedFunctionBoundary=True
            cur=cur.parent
        if not cur:
            return None
        if not crossedFunctionBoundary:
            return Scope.Local
        if varScope.isPyGlobal():
            return Scope.Global
        return Scope.Nonlocal

    def isDescendant(self,other):
        if not other:
            return False
        cur=self
        while cur:
            if cur==other:
                return True
            cur=cur.parent
        return False

    def commonAncestor(self,other,*,errorp=False):
        if self.isDescendant(other):
            return other
        if other.isDescendant(self):
            return self
        if not self.parent:
            if errorp:
                raise NoCommonAncestor()
            else:
                return None
        return self.parent.commonAncestor(other,errorp=errorp)

    def __contains__(self,var):
        if not isinstance(var,S):
            return False

        cur=self
        depth=0
        while cur:
            assert cur.parent is not cur
            if cur.parent:
                assert cur.parent.id<cur.id

            if cur.isLocal(var):
                return True

            cur=cur.parent

        return False

    def dontDisambiguate(self,name):
        return self.isLocal(name) and self.localDefs[name].dontDisambiguate

    def isLocal(self,var):
        return var in self.localDefs

    def __getitem__(self,varRef):
        cur=self
        while cur:
            if varRef.name in cur.localDefs:
                return cur.localDefs[varRef.name]
            cur=cur.parent
        raise Undefined(varRef)

    def addDef(self,var,initExpr,*,dontDisambiguate=False,const=False):
        var=S(var)
        if var in self.varAccesses:
            raise DefinedAfterUse(var,initExpr,self.varAccesses[var])
        if var in self.localDefs:
            raise Redefined(var,initExpr,self.localDefs[var])
        self.localDefs[var]=VarEntry(var,initExpr,
                                     dontDisambiguate=dontDisambiguate,
                                     const=const)

    def addFuncArg(self,var):
        self.addDef(var,None)

    def _addAccess(self,varRef):
        if varRef.name not in self.varAccesses:
            self.varAccesses[varRef.name]=set()
        accesses=self.varAccesses[varRef.name]
        accesses.add(varRef)

    def addRead(self,varRef):
        self._addAccess(varRef)

    def addWrite(self,varRef):
        self._addAccess(varRef)
        cur=self
        while cur:
            if varRef.name in cur.localDefs:
                cur.localDefs[varRef.name].markModified()
                break
            cur=cur.parent

    def undefinedVars(self):
        for v in self.varAccesses:
            if v not in self:
                yield (v,self.varAccesses[v])

class Env:
    def __init__(self,scope,parent):
        self.parent=parent
        self.scope=scope
        self.values={}

    def __getitem__(self,varRef):
        if self.scope.isLocal(varRef.name):
            if varRef.name in self.values:
                return self.values[varRef.name]
            else:
                try:
                    return varRef.constValue()
                except NotConstant:
                    raise NotInitialized(varRef.name)
        else:
            if self.parent:
                return self.parent[varRef]
            else:
                raise Undefined(varRef)

    def __setitem__(self,varRef,value):
        if self.scope.isLocal(varRef.name):
            self.values[varRef.name]=value
        else:
            if self.parent:
                self.parent[varRef]=value
            else:
                raise Undefined(varRef)

class Expr:
    def __init__(self,scope,isStmt):
        self.scope=scope
        if isStmt is None:
            self.isStmt=self.mustBeStmt()
        else:
            self.isStmt=isStmt
            assert isStmt or (not self.mustBeStmt())

    def mustBeStmt(self):
        return False

    def contents(self):
        return []

    def setScope(self,scope):
        for x in self.contents():
            x.setScope(scope)
        self.scope=scope

    def constValue(self):
        raise NotConstant(self)

    # Return the scope, ancestral to self.scope, which contains
    #  all var definitions upon which this expr depends.  For
    #  a constant, this is None.
    def scopeRequired(self):
        pass

    def varRefs(self):
        return []

    def isPureIn(self,containingScope):
        return False

    # Compile into Pyle.
    def compyle(self,stmtCollector):
        pass

    def isLvalue(self):
        return False

def varRefs(expr):
    if isinstance(expr,list):
        iters=list(map(varRefs,expr))
        return itertools.chain(*iters)
    if isinstance(expr,Expr):
        return expr.varRefs()
    return []

class Constant(Expr):
    def __init__(self,scope,value):
        Expr.__init__(self,scope,False)
        self.value=value

    def evaluate(self,env):
        return self.value

    def constValue(self):
        return self.value

    def scopeRequired(self):
        return None

    def isPureIn(self,containingScope):
        return True

    def compyle(self,stmtCollector):
        if self.isStmt:
            return None
        if isinstance(self.value,S):
            return [S('adder.common.Symbol'),[str(self.value)]]
        if self.value is None:
            return self.value
        for t in [str,int,float,bool,tuple,type(Constant)]:
            if isinstance(self.value,t):
                return self.value
        if isinstance(self.value,UserFunction):
            return self.value.compyle(stmtCollector)
        assert isinstance(self.value,list)
        return [S('mk-list'),
                list(map(lambda x: Constant(self.scope,
                                            x).compyle(stmtCollector),
                         self.value))
                ]

class VarRef(Expr):
    def __init__(self,scope,name,*,asDef=False):
        assert(name)
        Expr.__init__(self,scope,False)
        self.name=name
        self.asDef=asDef

    def isKeyword(self):
        return self.name.isKeyword()

    def evaluate(self,env):
        if self.isKeyword():
            raise KeywordsHaveNoValue(self)
        return env[self]

    def constValue(self):
        if self.isKeyword():
            raise KeywordsHaveNoValue(self)

        try:
            return self.scope[self].constValue()
        except NotConstant: # the one from VarEntry will have None for its expr
            raise NotConstant(self)

    def isLvalue(self):
        if self.asDef:
            return False

        scope=self.scopeRequired()
        if self.name in scope:
            varEntry=scope[self]
            return not varEntry.const

        return False

    def scopeRequired(self):
        if self.isKeyword() or self.asDef:
            return None

        cur=self.scope
        while cur:
            if cur.isLocal(self.name):
                return cur
            cur=cur.parent
        raise Undefined(self)

    def varRefs(self):
        if self.isKeyword():
            return []
        else:
            return [self]

    def isPureIn(self,containingScope):
        if self.isKeyword():
            return True

        try:
            required=self.scopeRequired()
        except Undefined:
            return False

        if required.isDescendant(containingScope):
            return True

        try:
            self.constValue()
        except NotConstant:
            return False
        except Undefined:
            return False
        return True

    def __str__(self):
        return self.name

    def compyle(self,stmtCollector):
        if self.isKeyword():
            raise KeywordsHaveNoValue(self)

        if self.isStmt:
            return

        if self.name.isGensym() or self.name.startswith('&'):
            return S(self.name)

        if self.asDef:
            scope=self.scope
        else:
            scope=self.scopeRequired()

        if self.name in scope:
            varEntry=scope[self]
            if varEntry.const and not self.asDef:
                try:
                    return varEntry.constValue()
                except NotConstant:
                    pass
                except NotInitialized:
                    pass
                except Undefined:
                    pass

            if varEntry.dontDisambiguate:
                return S(self.name)

        if scope.parent==None:
            return S(self.name)

        return S("%s_%d" % (self.name,scope.id))

class Call(Expr):
    def __init__(self,scope,isStmt,f,args):
        self.f=f
        Expr.__init__(self,scope,isStmt)
        self.allArgs=args
        self.posArgs=[]
        self.kwArgs=[]
        curKeyword=None
        for arg in args:
            isKeyword=isinstance(arg,VarRef) and arg.isKeyword()

            if curKeyword:
                if isKeyword:
                    raise TwoConsecutiveKeywords(curKeyword,arg)
                self.kwArgs.append([curKeyword.name[1:],arg])
                curKeyword=None
            else:
                if isKeyword:
                    assert len(arg.name)>1
                    curKeyword=arg
                else:
                    self.posArgs.append(arg)

        if args and isKeyword:
            raise KeywordWithNoArg(curKeyword)

    def mustBeStmt(self):
        fv=self.getFV()
        if fv:
            return fv.mustBeStmt()

    def contents(self):
        return [self.f]+self.allArgs

    def evaluate(self,env):
        fv=self.f.evaluate(env)
        if fv.special:
            return fv(env,*self.posArgs,**dict(self.kwArgs))
        else:
            posArgs=list(map(lambda a: a.evaluate(env),self.posArgs))
            kwArgs={}
            for (key,expr) in self.kwArgs:
                kwArgs[key]=expr.evaluate(env)
            return fv(*posArgs,**kwArgs)

    def constValue(self):
        fv=self.f.constValue()
        if not fv.isPure():
            raise NotConstant(self)
        argVs=list(map(lambda a: a.constValue(),self.posArgs))
        kwArgs={}
        for (key,expr) in self.kwArgs:
            kwArgs[key]=expr.constValue()
        return fv(*argVs,**kwArgs)

    def allArgExprs(self):
        return itertools.chain(self.posArgs,
                               map(lambda kx: kx[1],self.kwArgs)
                               )

    def scopeRequired(self):
        required=self.f.scopeRequired()
        for arg in self.allArgExprs():
            scope=arg.scopeRequired()
            if scope:
                required=required.commonAncestor(scope)
        return required

    def varRefs(self):
        for var in varRefs(self.f):
            yield var

        for arg in self.allArgExprs():
            for var in varRefs(arg):
                yield var

    def isPureIn(self,containingScope):
        fv=self.f.constValue()
        if not fv.isPure():
            return False
        for arg in self.allArgExprs():
            if not arg.isPureIn(containingScope):
                return False
        return True

    def getFV(self):
        try:
            return self.f.constValue()
        except NotConstant:
            pass
        except NotInitialized:
            pass
        except Undefined:
            pass

    def compyle(self,stmtCollector):
        fv=self.getFV()
        if fv:
            if isinstance(fv,str):
                print('f:',self.f,fv)
            return fv.compyleCall(self.f,self.posArgs,self.kwArgs,
                                  stmtCollector,self.isStmt)
        else:
            f=self.f.compyle(stmtCollector)
            posArgs=list(map(lambda x: x.compyle(stmtCollector),
                             self.posArgs))
            kwArgs=list(map(lambda kx: [kx[0],
                                        kx[1].compyle(stmtCollector)
                                        ],
                            self.kwArgs))
            if kwArgs:
                return [f,posArgs,kwArgs]
            else:
                return [f,posArgs]

class ExnHandler(Expr):
    def __init__(self,scope,exnVar,exnBody):
        Expr.__init__(self,scope,False)
        self.exnVar=exnVar
        self.exnBody=exnBody

    def compyle(self,stmtCollector):
        assert False

class Function:
    def __init__(self):
        self.special=False

    def mustBeStmt(self):
        return False

    def isPure(self):
        return False

    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        f=self.f.compyle(stmtCollector)
        posArgs=list(map(lambda x: x.compyle(stmtCollector),
                         args))
        kwArgs=list(map(lambda kx: [kx[0],kx[1].compyle(stmtCollector)],
                        kwArgs))
        if kwArgs:
            return [f,posArgs,kwArgs]
        else:
            return [f,posArgs]

class PyleExpr(Function):
    def __init__(self,scope,f):
        self.f=VarRef(scope,S(f))

class PyleStmt(PyleExpr):
    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        stmtCollector(PyleExpr.compyleCall(self,f,
                                           args,kwArgs,
                                           stmtCollector,isStmt))

class Defun(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        uf=UserFunction(f.scope,
                        args[1:],kwArgs,
                        None,
                        name=args[0])
        expr=uf.compyle(stmtCollector)
        if not isStmt:
            return expr

class Lambda(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        if isStmt:
            return
        return UserFunction(f.scope,
                            args,kwArgs,
                            None).compyle(stmtCollector)

class Defvar(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        assert args
        assert len(args) in [1,2]
        assert not kwArgs

        var=args[0].compyle(stmtCollector)
        if len(args)==2:
            valueExpr=args[1]
            valuePyle=valueExpr.compyle(stmtCollector)
            if isStmt:
                stmtCollector([S(':='),[var,valuePyle]])
            else:
                stmtCollector([S(':='),[var,None]])
                assigner=gensym('assign-%s' % args[0].name)
                assignerArg=S('y') if args[0].name==S('x') else S('x')
                d=build(f.scope,
                        [S('defun'),
                         assigner,[assignerArg],
                         [S(':='),args[0].name,assignerArg],
                         [S('return'),args[0].name]
                         ],
                        True)
                d.compyle(stmtCollector)
                return [assigner,[valuePyle]]
        else:
            stmtCollector([S(':='),[var,None]])
            if not isStmt:
                return var

class Defconst(Defvar):
    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        assert isStmt
        Defvar.compyleCall(self,f,args,kwArgs,stmtCollector,isStmt)

class Assignment(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        assert args
        assert len(args)==2
        assert not kwArgs
        if not args[0].isLvalue():
            raise AssigningToConstant(args[0].name)

        valueExpr=args[1]
        valuePyle=valueExpr.compyle(stmtCollector)
        var=args[0].compyle(stmtCollector)
        if isStmt:
            stmtCollector([S(':='),[var,valuePyle]])
        else:
            assigner=gensym('assign-%s' % args[0].name)
            assignerArg=S('y') if args[0].name==S('x') else S('x')
            d=build(f.scope,
                    [S('defun'),
                     assigner,[assignerArg],
                     [S(':='),args[0].name,assignerArg],
                     args[0].name
                     ],
                    True)
            d.compyle(stmtCollector)
            return [assigner,[valuePyle]]

class Raise(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        assert not kwArgs
        exnPyle=args[0].compyle(stmtCollector)
        if isStmt:
            pyle=[S('raise'),[exnPyle]]
            stmtCollector(pyle)
        else:
            raiser=gensym('raise')
            d=build(f.scope,
                    [S('defun'),
                     raiser,[S('e')],
                     [S('raise'),S('e')],
                     None
                     ],
                    True)
            d.compyle(stmtCollector)
            return [raiser,[exnPyle]]

    def __call__(self,e):
        raise e

class Reraise(Function):
    def mustBeStmt(self):
        return True

    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        assert not args
        assert not kwArgs
        assert isStmt

        stmtCollector([S('raise'),[]])

class Return(Function):
    def mustBeStmt(self):
        return True

    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        assert not kwArgs
        assert isStmt
        pyle=[S('return'),[args[0].compyle(stmtCollector)]]
        stmtCollector(pyle)
        return None

class Yield(Function):
    def mustBeStmt(self):
        return True

    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        assert not kwArgs
        assert isStmt

        scope=f.scope.nearestFuncAncestor()
        assert scope
        scope.funcYields=True

        pyle=[S('yield'),[args[0].compyle(stmtCollector)]]
        stmtCollector(pyle)
        return None

class ReturnOrYieldFrom(Function):
    def __init__(self,yielding):
        self.yielding=yielding
        self.klass='adder.runtime.%sValue' % ('Yield' if yielding
                                              else 'Return')

    def mustBeStmt(self):
        return True

    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        assert not kwArgs
        assert isStmt
        assert len(args)==2

        blockExpr=args[0]
        assert isinstance(blockExpr,VarRef)
        block=blockExpr.name

        if self.yielding:
            scope=f.scope.nearestFuncAncestor(block)
            assert scope
            scope.funcYields=True

        pyle=[S('raise'),[[S(self.klass),
                           [qpy(block),
                            args[1].compyle(stmtCollector)
                            ]
                           ]]
              ]
        stmtCollector(pyle)
        return None

class ReturnFrom(ReturnOrYieldFrom):
    def __init__(self):
        ReturnOrYieldFrom.__init__(self,False)

class YieldFrom(ReturnOrYieldFrom):
    def __init__(self):
        ReturnOrYieldFrom.__init__(self,True)

class Reverse(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        # (reverse) is pure, so just eval the arg
        if isStmt:
            return args[0].compyle(stmtCollector)

        assert not kwArgs
        assert len(args)==1
        return [S('adder.runtime.reverse'),
                [args[0].compyle(stmtCollector)]]

    def __call__(self,l):
        l2=list(l)
        l2.reverse()
        return l2

class Stdenv(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        if isStmt:
            return None
        assert not kwArgs
        assert len(args)==0
        return [S('adder.runtime.stdenv'),[]]

class EvalPy(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        assert not kwArgs
        assert len(args)==1
        return [S('evalPy'),[args[0].compyle(stmtCollector)]]

class ExecPy(Function):
    def mustBeStmt(self):
        return True

    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        assert not kwArgs
        assert len(args)==1
        assert isStmt

        stmtCollector([S('exec'),[args[0].compyle(stmtCollector)]])

class Begin(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        assert not kwArgs
        if not args:
            # (begin) with empty body is a no-op
            return

        body=[]
        def innerCollector(stmt):
            body.append(stmt)

        if (isStmt
            or (args and args[-1].mustBeStmt())
            ):
            stmts=args
            last=None
        else:
            stmts=args[:-1]
            last=args[-1] if args else None

        for a in stmts:
            exprPyle=a.compyle(innerCollector)
            if exprPyle:
                innerCollector(exprPyle)

        if last:
            scratchVar=gensym('scratch')
            innerCollector([S(':='),
                            [scratchVar,
                             last.compyle(innerCollector)]
                            ])
        else:
            scratchVar=None

        stmtCollector([S('begin'),body])
        return scratchVar

class Block(Function):
    def transform(self,srcExpr):
        assert len(srcExpr)==3
        (name,body)=srcExpr[1:]
        assert isinstance(name,S) and name.isKeyword()
        name=S(name[1:])
        scratch=gensym(name)
        rv=gensym('rv')
        return [S('begin'),
                [S('defvar'),scratch],
                [S('-gomer-try'),
                 [S(':='),scratch,body],
                 S(':adder.runtime.ReturnValue'),
                 [rv,
                  [S('if'),
                   [S('=='),
                    [S('.'),rv,S('block')],
                    q(name)],
                   [S(':='),scratch,[S('.'),rv,S('value')]],
                   [S('reraise')]
                   ]
                  ]
                 ],
                scratch
                ]

class Try(Function):
    def mustBeStmt(self):
        return True

    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        if not args:
            # try: with empty body is a no-op, no matter what
            #  its except: and finally: clauses may be.
            return

        assert isStmt

        bodyPyle=[]
        innerCollector=bodyPyle.append

        Begin().compyleCall(VarRef(f.scope,S('begin')),
                            args,None,innerCollector,
                            True)

        exnPyles=[]

        for (klass,exnHandler) in kwArgs:
            assert isinstance(exnHandler,ExnHandler)
            exnStmts=[]
            clausePyle=exnHandler.exnBody.compyle(exnStmts.append)
            if clausePyle:
                exnStmts.append(clausePyle)

            if exnHandler.exnVar:
                var=exnHandler.exnVar.compyle(innerCollector)
            else:
                var=None
                
            exnPyles.append([klass,var,[S('begin'),exnStmts]])

        stmtCollector([S('try'),bodyPyle,exnPyles])

class While(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        assert args
        assert not kwArgs

        scratch=gensym('scratch')
        innerStmts=[]
        condPyle=args[0].compyle(stmtCollector)
        for arg in args[1:]:
            expr=arg.compyle(innerStmts.append)
            if expr:
                innerStmts.append(expr)

        stmtCollector([S('while'),[condPyle]+innerStmts])

class If(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        def wrapStmts(stmts,noneOK):
            if noneOK and not stmts:
                return None
            if len(stmts)==1:
                return stmts[0]
            return [S('begin'),stmts]

        assert args
        assert len(args) in [2,3]
        assert not kwArgs

        condExpr=args[0]
        thenExpr=args[1]
        elseExpr=args[2] if len(args)==3 else None

        thenStmts=[]
        elseStmts=[]

        condPyle=args[0].compyle(stmtCollector)

        thenPyle=thenExpr.compyle(thenStmts.append)
        elsePyle=None
        if isStmt:
            if thenPyle:
                thenStmts.append(thenPyle)
            if elseExpr:
                elsePyle=elseExpr.compyle(elseStmts.append)
                if elsePyle:
                    elseStmts.append(elsePyle)
            thenClause=wrapStmts(thenStmts,False)
            elseClause=wrapStmts(elseStmts,True)
            stmtCollector([S('if-stmt'),
                           [condPyle,thenClause,elseClause]])
        else:
            if elseExpr:
                elsePyle=elseExpr.compyle(elseStmts.append)
            if thenStmts or elseStmts:
                helperName=gensym('if')
                if thenPyle:
                    thenStmts.append([S('return'),[thenPyle]])
                if elsePyle:
                    elseStmts.append([S('return'),[elsePyle]])
                thenStmts=wrapStmts(thenStmts,False)
                elseStmts=wrapStmts(elseStmts,True)
                ifStmt=[S('if-stmt'),[condPyle,thenStmts,elseStmts]]
                stmtCollector([S('def'),[helperName,[],ifStmt]])
                return [helperName,[]]
            return [S('if-expr'),[condPyle,thenPyle,elsePyle]]

class Dot(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        assert not kwArgs
        obj=args[0].compyle(stmtCollector)
        return [S('.'),
                ([obj]
                 +list(map(lambda x: x.name,args[1:]))
                 )
                ]

class NAryAdditive(Function):
    def __init__(self,op,zero):
        self.op=op
        self.zero=zero

    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        assert not kwArgs
        if not args:
            return self.zero
        operands=list(map(lambda a: a.compyle(stmtCollector),args))
        return functools.reduce(lambda x,y: [S(self.op),[x,y]],operands)

class NArySubtractive(NAryAdditive):
    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        assert not kwArgs
        if len(args)==1:
            x=args[0].compyle(stmtCollector)
            if self.zero is 0:
                return [S(self.op),[x]]
            else:
                return [S(self.op),[self.zero,x]]
        return NAryAdditive.compyleCall(self,f,args,kwArgs,
                                        stmtCollector,isStmt)

class Plus(NAryAdditive):
    def __init__(self):
        NAryAdditive.__init__(self,'+',0)

class Times(NAryAdditive):
    def __init__(self):
        NAryAdditive.__init__(self,'*',1)

class Minus(NArySubtractive):
    def __init__(self):
        NArySubtractive.__init__(self,'-',0)

class Div(NArySubtractive):
    def __init__(self):
        NArySubtractive.__init__(self,'/',1)

class IDiv(NArySubtractive):
    def __init__(self):
        NArySubtractive.__init__(self,'//',1)

class Import(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,isStmt):
        assert len(args)==1
        assert isinstance(args[0],VarRef)
        stmtCollector([S('import'),[args[0].name]])

class NativeFunction(Function):
    def __init__(self,f,pure,*,special=False):
        self.pure=pure
        self.f=f
        self.special=special

    def __call__(self,*args,**kwArgs):
        return self.f(*args,**kwArgs)

    def isPure(self):
        return self.pure

class UserFunction(Function):
    # The fExpr should be the (defun) or (lambda) that created this function.
    def __init__(self,scope,defArgs,kwArgs,outerEnv,*,name=None):
        Function.__init__(self)
        self.special=False
        assert defArgs
        assert not kwArgs
        self.name=name or VarRef(scope,gensym('lambda'),asDef=True)
        
        assert isinstance(defArgs[0],list)
        for arg in defArgs[0]:
            assert isinstance(arg,VarRef)
        self.argList=defArgs[0]
        self.bodyExprs=defArgs[(1):]
        if self.bodyExprs:
            self.innerScope=self.bodyExprs[0].scope
            self.outerEnv=outerEnv

        if name:
            self.name.asDef=True
        for arg in self.argList:
            arg.asDef=True

    def __call__(self,*args):
        if not self.bodyExprs:
            return None
        assert len(args)==len(self.argList)
        innerEnv=Env(self.innerScope,self.outerEnv)
        for (arg,value) in zip(self.argList,args):
            innerEnv[arg]=value

        last=None
        for x in self.bodyExprs:
            last=x.evaluate(innerEnv)
        return last

    def isPure(self):
        if not self.bodyExprs:
            return True
        for expr in self.bodyExprs:
            if not expr.isPureIn(self.innerScope):
                return False
        return True

    def compyle(self,stmtCollector):
        globalRefs=set()
        nonlocalRefs=set()
        for expr in self.bodyExprs:
            for varRef in varRefs(expr):
                required=varRef.scopeRequired()
                if not required:
                    continue
                if required.isDescendant(self.innerScope):
                    continue
                accessMode=self.innerScope.accessMode(required)
                assert accessMode
                if accessMode==Scope.Nonlocal:
                    nonlocalRefs.add(varRef.compyle(stmtCollector))
                else:
                    if accessMode==Scope.Global:
                        if varRef.name not in required.transglobal:
                            globalRefs.add(varRef.compyle(stmtCollector))

        argListPyle=list(map(lambda sym: sym.compyle(stmtCollector),
                             self.argList))
        if globalRefs:
            argListPyle.append(S('&global'))
            argListPyle+=list(globalRefs)

        if nonlocalRefs:
            argListPyle.append(S('&nonlocal'))
            argListPyle+=list(nonlocalRefs)

        defStmt=[S('def'),
                 [self.name.compyle(stmtCollector),
                  argListPyle]
                 ]

        def innerCollector(stmt):
            defStmt[1].append(stmt)

        scratchVar=gensym('scratch')

        for expr in self.bodyExprs[:-1]:
            pyleExpr=expr.compyle(innerCollector)
            if pyleExpr:
                innerCollector(pyleExpr)

        if self.bodyExprs:
            lastExpr=self.bodyExprs[-1]
            pyleExpr=lastExpr.compyle(innerCollector)
            if pyleExpr:
                if self.innerScope.funcYields:
                    innerCollector(pyleExpr)
                else:
                    innerCollector([S('return'),[pyleExpr]])

        stmtCollector(defStmt)
        return self.name.compyle(stmtCollector)

def gatherArgs(args):
    posArgs=[]
    kwArgs=[]
    prevKeyword=False
    for a in args:
        isKeyword=(isinstance(a,S) and a.isKeyword())
        if prevKeyword:
            if isKeyword:
                raise TwoConsecutiveKeywords(prevKeyword,a)
            kwArgs.append([prevKeyword,a])
            prevKeyword=None
        else:
            if isKeyword:
                prevKeyword=a
            else:
                posArgs.append(a)
    if prevKeyword:
        raise KeywordWithNoArg(prevKeyword)
    return (posArgs,kwArgs)

def build(scope,gomer,isStmt):
    if isinstance(gomer,S):
        return VarRef(scope,gomer)
    if not isinstance(gomer,list):
        return Constant(scope,gomer)
    assert gomer
    assert gomer[0]

    if gomer[0] in scope:
        f=None
        try:
            f=scope[VarRef(scope,gomer[0])].constValue()
        except NotConstant:
            pass
        except NotInitialized:
            pass
        if f and hasattr(f,'transform'):
            return build(scope,f.transform(gomer),isStmt)

    if gomer[0]==S('scope'):
        innerScope=Scope(scope)
        return build(innerScope,[S('begin')]+gomer[1:],isStmt)

    if gomer[0]==S('defun'):
        innerScope=Scope(scope,isFunc=True)
        name=gomer[1]
        argList=gomer[2]
        body=gomer[3:]
        scope.addDef(name,None)
        nameVar=build(scope,name,False)
        nameVar.asDef=True
        for arg in argList:
            innerScope.addDef(arg,None,dontDisambiguate=True)
        bodyArgs=list(map(lambda g: build(innerScope,g,True),
                          body[:-1]))
        if body:
            bodyArgs.append(build(innerScope,body[-1],None))
        return Call(scope,isStmt,
                    build(scope,gomer[0],False),
                    ([nameVar]
                     +[list(map(lambda a: build(innerScope,a,False),
                                argList))]
                     +bodyArgs
                     )
                    )
    if gomer[0]==S('lambda'):
        innerScope=Scope(scope,isFunc=True)
        argList=gomer[1]
        body=gomer[2:]
        for arg in argList:
            innerScope.addDef(arg,None,dontDisambiguate=True)
        bodyArgs=list(map(lambda g: build(innerScope,g,True),
                          body[:-1]))
        if body:
            bodyArgs.append(build(innerScope,body[-1],None))
        return Call(scope,
                    isStmt,
                    build(scope,gomer[0],isStmt),
                    ([list(map(lambda a: build(innerScope,a,isStmt),
                               argList))]
                     +bodyArgs
                     )
                    )
    if gomer[0]==S('quote'):
        assert len(gomer)==2
        if isinstance(gomer[1],list):
            return Constant(scope,gomer[1])
        else:
            return Constant(scope,gomer[1])

    if gomer[0]==S('-gomer-try'):
        lastWasKeyword=False
        (posArgs,kwArgs)=gatherArgs(gomer[1:])
        args=list(map(lambda a: build(scope,a,True),
                      posArgs))
        clauses=[]
        for (klass,handler) in kwArgs:
            innerScope=Scope(scope)
            if klass==S(':finally'):
                (exnVar,exnBody)=(None,handler)
            else:
                (exnVar,*exnBody)=handler
                innerScope.addDef(exnVar,None)
                exnVar=VarRef(innerScope,exnVar)
                exnVar.asDef=True
            exnBody=list(exnBody)
            if len(exnBody)>1:
                exnBody=[S('begin')]+exnBody
            else:
                exnBody=exnBody[0]

            clause=ExnHandler(scope,
                              exnVar,build(innerScope,
                                           exnBody,
                                           True))
            args.append(build(scope,klass,False))
            args.append(clause)

        return Call(scope,
                    isStmt,
                    build(scope,gomer[0],False),
                    args)

    if gomer[0]==S('begin'):
        args=list(map(lambda g: build(scope,g,True),
                  gomer[1:-1]))
        if len(gomer)>1:
            args.append(build(scope,gomer[-1],isStmt))
    else:
        if gomer[0]==S('while'):
            args=([build(scope,gomer[1],False)]
                  +list(map(lambda g: build(scope,g,True),
                            gomer[2:-1])))
            if len(gomer)>2:
                args.append(build(scope,gomer[-1],isStmt))
        else:
            if gomer[0]==S('if'):
                assert len(gomer) in [3,4]
                args=[build(scope,gomer[1],False),
                      build(scope,gomer[2],isStmt)]
                if len(gomer)==4:
                    args.append(build(scope,gomer[3],isStmt))
            else:
                args=list(map(lambda g: build(scope,g,False),
                              gomer[1:]))

    res=Call(scope,
             isStmt,
             build(scope,gomer[0],False),
             args)

    if gomer[0] in [S('defvar'),S('defconst')]:
        res.posArgs[0].asDef=True
        res.scope.addDef(res.posArgs[0].name,None,
                         const=(gomer[0]==S('defconst'))
                         )

    if gomer[0]==S('.'):
        for arg in res.posArgs[1:]:
            arg.asDef=True

    return res

def maybeBegin(body):
    if len(body)==1:
        return body[0]
    else:
        return [S('begin')]+body

class Reducer:
    def reduce(self,gomer,isStmt,stmtCollector):
        pass

class ReduceDefault(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        def reduceArg(i):
            return reduce(gomer[i],
                          False,
                          stmtCollector)
        return list(map(reduceArg,range(len(gomer))))

class ReduceIf(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        assert len(gomer) in [3,4]
        condExpr=reduce(gomer[1],False,stmtCollector)
        thenBody=[]
        thenExpr=reduce(gomer[2],isStmt,thenBody.append)
        if isStmt:
            scratch=None
        else:
            scratch=gensym('if')
            thenBody.append([S(':='),scratch,thenExpr])
        if len(gomer)==4:
            elseBody=[]
            elseExpr=reduce(gomer[3],isStmt,elseBody.append)
            if not isStmt:
                elseBody.append([S(':='),scratch,elseExpr])
            stmtCollector([S('if'),condExpr,
                           maybeBegin(thenBody),
                           maybeBegin(elseBody)])
        else:
            stmtCollector([S('if'),condExpr,
                           maybeBegin(thenBody)])
        return scratch

class ReduceWhile(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        assert len(gomer)>=2
        if isStmt:
            scratch=None
        else:
            scratch=gensym('while')
            stmtCollector([S(':='),scratch,None])
        condBody=[]
        condExpr=reduce(gomer[1],False,condBody.append)
        for cb in condBody:
            stmtCollector(cb)
        body=[]
        bodyExpr=None
        for (i,b) in enumerate(gomer[2:]):
            bodyExpr=reduce(b,
                            isStmt or ((i+2)<(len(gomer)-1)),
                            body.append)
        if body and not isStmt:
            body.append([S(':='),scratch,bodyExpr])
        for cb in condBody:
            body.append(cb)
        stmtCollector([S('while'),condExpr,maybeBegin(body)])
        return scratch

class ReduceDefun(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        name=gomer[1]
        argList=gomer[2]
        body=[]
        bodyGs=gomer[3:]
        if bodyGs:
            for g in bodyGs[:-1]:
                reduce(g,True,body.append)
            resExpr=reduce(bodyGs[-1],False,body.append)
            reduce([S('return'),resExpr],True,body.append)
        if body:
            body=maybeBegin(body)
        else:
            body=[S('pass')]
        stmtCollector([S('def'),name,gomer[2],body])
        if not isStmt:
            return name

class ReduceLambda(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        if isStmt:
            return None
        name=gensym('lambda')
        reduce([S('defun'),name]+gomer[1:],True,stmtCollector)
        return name

class ReduceAssign(Reducer):
    def isSimple(self,rhs):
        if not isinstance(rhs,list):
            return True
        assert rhs
        if rhs[0] in reductionRules:
            return False
        for arg in rhs[1:]:
            if isinstance(arg,list):
                return False
        return True

    def reduce(self,gomer,isStmt,stmtCollector):
        lhs=gomer[1]
        rhs=gomer[2]
        assert isinstance(lhs,S) # Have to deal with members later
        if self.isSimple(rhs):
            stmtCollector(gomer)
        else:
            rhsExpr=reduce(rhs,False,stmtCollector,inAssignment=True)
            stmtCollector([S(':='),lhs,rhsExpr])
        if not isStmt:
            return lhs

class ReduceBegin(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        parts=gomer[1:]
        if not parts:
            return None

        for p in parts[:-1]:
            reduce(p,True,stmtCollector)
        lastExpr=reduce(parts[-1],isStmt,stmtCollector)
        if not isStmt:
            return lastExpr

class ReduceImport(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        last=None
        for module in gomer[1:]:
            assert isinstance(module,S)
            stmtCollector([S('import'),module])
            last=module
        if not isStmt:
            return last

class ReduceAtom(Reducer):
    def __init__(self,name):
        self.name=S(name)

    def reduce(self,gomer,isStmt,stmtCollector):
        assert isStmt
        assert len(gomer)==1
        stmtCollector([self.name])

class ReduceQuote(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        if isStmt:
            return
        assert len(gomer)==2
        if gomer[1] is None:
            return gomer[1]
        for t in [bool,int,float,str]:
            if isinstance(gomer[1],t):
                return gomer[1]
        return gomer

class ReduceReturn(Reducer):
    # Always make (return) a statment.  If you use it as an expr,
    #  it'll get put into the statement stream in the correct
    #  order.  Of course, it *can't* have a value, since it skips
    #  past the value, so it doesn't matter what we return as the
    #  expr code.  So we don't, and let the caller get None.
    def reduce(self,gomer,isStmt,stmtCollector):
        assert len(gomer)==2
        stmtCollector([S('return'),reduce(gomer[1],False,stmtCollector)])

class ReduceYield(Reducer):
    # Python yield has to be a statement; Adder (yield) does not.  If
    #  you use it as an expr, it'll get put into the statement stream
    #  in the correct order, and the value yielded will be used as
    #  the value of the expr.
    def reduce(self,gomer,isStmt,stmtCollector):
        assert len(gomer)==2
        expr=reduce(gomer[1],False,stmtCollector)
        stmtCollector([S('yield'),expr])
        if not isStmt:
            return expr

class ReduceAnd(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        if len(gomer)==1:
            if isStmt:
                return
            else:
                return True
        if len(gomer)==2:
            return reduce(gomer[1],isStmt,stmtCollector)
        cond=reduce(gomer[1],False,stmtCollector)
        return reduce([S('if'),
                       cond,
                       [S('and')]+gomer[2:],
                       cond
                       ],
                      isStmt,stmtCollector)

class ReduceOr(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        if len(gomer)==1:
            if isStmt:
                return
            else:
                return False
        if len(gomer)==2:
            return reduce(gomer[1],isStmt,stmtCollector)
        cond=reduce(gomer[1],False,stmtCollector)
        return reduce([S('if'),
                       cond,
                       cond,
                       [S('or')]+gomer[2:]
                       ],
                      isStmt,stmtCollector)

class ReduceDot(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        assert len(gomer)>1
        if len(gomer)==2:
            return reduce(gomer[1],isStmt,stmtCollector)
        obj=reduce(gomer[1],False,stmtCollector)
        if isStmt:
            # x.y as a statement is a nop,
            # But f().y as a statement is equiv to f().
            return

        res=[S('.'),obj]
        for name in gomer[2:]:
            assert isinstance(name,S)
            res.append(name)
        return res

class ReduceRaise(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        assert len(gomer) in [1,2]
        if len(gomer)==1:
            stmtCollector([S('reraise')])
        else:
            stmtCollector([S('raise'),reduce(gomer[1],False,stmtCollector)])

class ReducePrint(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        expr=None
        stmt=[S('print')]
        for arg in gomer[1:]:
            expr=reduce(arg,False,stmtCollector)
            stmt.append(expr)
        stmtCollector(stmt)
        if not isStmt:
            return expr

class ReduceAdditiveBinop(Reducer):
    def __init__(self,op,identity):
        self.op=op
        self.identity=identity

    def reduce(self,gomer,isStmt,stmtCollector):
        def expr():
            if len(gomer)==1:
                return self.identity
            op1=reduce(gomer[1],False,stmtCollector)
            if len(gomer)==2:
                return op1
            return [S('binop'),self.op,op1,
                    reduce([self.op]+gomer[2:],False,stmtCollector)
                    ]
        e=expr()
        if not isStmt:
            return e

reductionRules={S('if') : ReduceIf(),
                S('while') : ReduceWhile(),
                S('defun') : ReduceDefun(),
                S('lambda') : ReduceLambda(),
                S(':=') : ReduceAssign(),
                S('begin') : ReduceBegin(),
                S('import') : ReduceImport(),
                S('break') : ReduceAtom('break'),
                S('continue') : ReduceAtom('continue'),
                S('quote') : ReduceQuote(),
                S('return') : ReduceReturn(),
                S('yield') : ReduceYield(),
                S('and') : ReduceAnd(),
                S('or') : ReduceOr(),
                S('.') : ReduceDot(),
                S('raise') : ReduceRaise(),
                S('print') : ReducePrint(),
                S('+') : ReduceAdditiveBinop(S('+'),0),
                }
reduceDefault=ReduceDefault()

def getReducer(f):
    if f in reductionRules:
        return reductionRules[f]
    else:
        return reduceDefault

def reduce(gomer,isStmt,stmtCollector,*,inAssignment=False):
    if isinstance(gomer,list):
        assert gomer
        reducer=getReducer(gomer[0])
        gomer=reducer.reduce(gomer,isStmt,stmtCollector)
    if isStmt:
        if isinstance(gomer,list):
            stmtCollector(gomer)
    else:
        if ((not inAssignment)
            and isinstance(gomer,list)
            and gomer[0]!=S(':=')
            ):
            scratch=gensym('scratch')
            stmtCollector([S(':='),scratch,gomer])
            gomer=scratch
        return gomer

def evalTopLevel(expr,scope,globals,isStmt,*,verbose=False):
    pyleStmts=[]
    pythonFlat=''
    exprPyleList=build(scope,expr,isStmt).compyle(pyleStmts.append)
    if exprPyleList is not None:
        exprPyleAST=adder.pyle.buildExpr(exprPyleList)
        exprPython=exprPyleAST.toPython(False)
    else:
        exprPython=None
    for pyleList in pyleStmts:
        pyleAST=adder.pyle.buildStmt(pyleList)
        pythonTree=pyleAST.toPythonTree()
        pythonFlat+=adder.pyle.flatten(pythonTree)
    if verbose:
        print('exprPyleList: ',exprPyleList)
        print('pyleStmts: ',pyleStmts)
        print('pythonFlat: ',pythonFlat)
    if pythonFlat:
        exec(pythonFlat,globals)
    if exprPython is not None:
        return eval(exprPython,globals)

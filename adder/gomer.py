# A structured internal representation; basically an annotated form of
#  Adder itself, with macros expanded.  Gets converted to Pyle.
#  Includes a basic interpreter, for use in macro expansion.

import itertools,re,pdb,adder.pyle,sys
from adder.common import Symbol as S, gensym

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
        return 'Cannot use a keyword as a value: %s' % self.args

class TwoConsecutiveKeywords(Exception):
    def __init__(self,varRef):
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
                             ('return',Return()),
                             ('yield',Yield()),
                             ('raise',Raise()),
                             ('-gomer-try',Try()),
                             ('reverse',Reverse()),
                             ('stdenv',Stdenv()),
                             ('eval-py',EvalPy()),
                             ('exec-py',ExecPy()),
                             ('import',Import()),
                             ('while',While()),
                             ('.',Dot()),
                             ]:
                self.addDef(S(name),Constant(self,f))
                self.transglobal.add(S(name))
            for name in ['if',
                         '+','-','*','/','//','%',
                         '<','>','<=','>=','==','!=',
                         'in','not',
                         'tuple','list','set','dict',
                         'mk-tuple','mk-list','mk-set','mk-dict',
                         'mk-symbol',
                         '[]','slice','getattr','isinstance',
                         'print','gensym','apply',
                         ]:
                self.addDef(S(name),Constant(self,PyleExpr(self,name)))
                self.transglobal.add(S(name))

            for name in ['break','continue',
                         ]:
                self.addDef(S(name),Constant(self,PyleStmt(self,name)))
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
    def __init__(self,scope):
        self.scope=scope

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
    def compyle(self,stmtCollector,*,asStmt=False):
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
        Expr.__init__(self,scope)
        self.value=value

    def evaluate(self,env):
        return self.value

    def constValue(self):
        return self.value

    def scopeRequired(self):
        return None

    def isPureIn(self,containingScope):
        return True

    def compyle(self,stmtCollector,*,asStmt=False):
        if isinstance(self.value,S):
            return [S('adder.common.Symbol'),[str(self.value)]]
        if self.value is None:
            return self.value
        for t in [str,int,float,bool,tuple,type(Constant)]:
            if isinstance(self.value,t):
                return self.value
        if isinstance(self.value,UserFunction):
            return self.value.compyle(stmtCollector,asStmt=asStmt)
        assert isinstance(self.value,list)
        return [S('mk-list'),
                list(map(lambda x: Constant(self.scope,
                                            x).compyle(stmtCollector,
                                                       asStmt=False),
                         self.value))
                ]

class VarRef(Expr):
    def __init__(self,scope,name,*,asDef=False):
        assert(name)
        Expr.__init__(self,scope)
        self.name=name
        self.asDef=asDef

    def isKeyword(self):
        return (self.name[0]==':') and (self.name!=':=')

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

    def compyle(self,stmtCollector,*,asStmt=False):
        if self.isKeyword():
            raise KeywordsHaveNoValue(self)

        if asStmt:
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
    def __init__(self,scope,f,args):
        Expr.__init__(self,scope)
        self.f=f
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

    def compyle(self,stmtCollector,*,asStmt=False):
        fv=self.getFV()
        if fv:
            if isinstance(fv,str):
                print('f:',self.f,fv)
            return fv.compyleCall(self.f,self.posArgs,self.kwArgs,
                                  stmtCollector,asStmt=asStmt)
        else:
            f=self.f.compyle(stmtCollector,asStmt=False)
            posArgs=list(map(lambda x: x.compyle(stmtCollector,
                                                 asStmt=False),
                             self.posArgs))
            kwArgs=list(map(lambda kx: [kx[0],
                                        kx[1].compyle(stmtCollector,
                                                      asStmt=False)
                                        ],
                            self.kwArgs))
            if kwArgs:
                return [f,posArgs,kwArgs]
            else:
                return [f,posArgs]

class Function:
    def __init__(self):
        self.special=False

    def mustBeStmt(self):
        return False

    def isPure(self):
        return False

    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        f=self.f.compyle(stmtCollector,asStmt=False)
        posArgs=list(map(lambda x: x.compyle(stmtCollector,
                                             asStmt=False),
                         args))
        kwArgs=list(map(lambda kx: [kx[0],kx[1].compyle(stmtCollector,
                                                        asStmt=False)],
                        kwArgs))
        if kwArgs:
            return [f,posArgs,kwArgs]
        else:
            return [f,posArgs]

class PyleExpr(Function):
    def __init__(self,scope,f):
        self.f=VarRef(scope,S(f))

class PyleStmt(PyleExpr):
    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        stmtCollector(PyleExpr.compyleCall(self,f,
                                           args,kwArgs,
                                           stmtCollector,
                                           asStmt=True))

class Defun(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        uf=UserFunction(f.scope,
                        args[1:],kwArgs,
                        None,
                        name=args[0])
        return uf.compyle(stmtCollector,
                          asStmt=asStmt)

class Lambda(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        if asStmt:
            return
        return UserFunction(f.scope,
                            args,kwArgs,
                            None).compyle(stmtCollector,
                                          asStmt=asStmt)

class Defvar(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        assert args
        assert len(args) in [1,2]
        assert not kwArgs

        if len(args)==2:
            valueExpr=args[1]
            valuePyle=valueExpr.compyle(stmtCollector,asStmt=False)
            var=args[0].compyle(stmtCollector,asStmt=False)
            if asStmt:
                stmtCollector([S(':='),[var,valuePyle]])
            else:
                stmtCollector([S(':='),[var,None]])
                assigner=gensym('assign-%s' % args[0].name)
                assignerArg=S('y') if args[0].name==S('x') else S('x')
                d=build(f.scope,
                        [S('defun'),
                         assigner,[assignerArg],
                         [S(':='),args[0].name,assignerArg]
                         ])
                d.compyle(stmtCollector,asStmt=True)
                return [assigner,[valuePyle]]
        else:
            stmtCollector([S(':='),[var,None]])
            if not asStmt:
                return var

class Defconst(Defvar):
    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        assert asStmt
        Defvar.compyleCall(self,f,args,kwArgs,stmtCollector,asStmt=asStmt)

class Assignment(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        assert args
        assert len(args)==2
        assert not kwArgs
        if not args[0].isLvalue():
            raise AssigningToConstant(args[0].name)

        valueExpr=args[1]
        valuePyle=valueExpr.compyle(stmtCollector,asStmt=False)
        var=args[0].compyle(stmtCollector,asStmt=False)
        if asStmt:
            stmtCollector([S(':='),[var,valuePyle]])
        else:
            assigner=gensym('assign-%s' % args[0].name)
            assignerArg=S('y') if args[0].name==S('x') else S('x')
            d=build(f.scope,
                    [S('defun'),
                     assigner,[assignerArg],
                     [S(':='),args[0].name,assignerArg],
                     args[0].name
                     ])
            d.compyle(stmtCollector,asStmt=False)
            return [assigner,[valuePyle]]

class Raise(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        assert not kwArgs
        exnPyle=args[0].compyle(stmtCollector,asStmt=False)
        if asStmt:
            pyle=[S('raise'),[exnPyle]]
            stmtCollector(pyle)
        else:
            raiser=gensym('raise')
            d=build(f.scope,
                    [S('defun'),
                     raiser,[S('e')],
                     [S('raise'),S('e')],
                     None
                     ])
            d.compyle(stmtCollector,asStmt=True)
            return [raiser,[exnPyle]]

    def __call__(self,e):
        raise e

class Return(Function):
    def mustBeStmt(self):
        return True

    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        assert not kwArgs
        assert asStmt
        pyle=[S('return'),[args[0].compyle(stmtCollector,asStmt=False)]]
        stmtCollector(pyle)
        return None

class Yield(Function):
    def mustBeStmt(self):
        return True

    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        assert not kwArgs
        assert asStmt

        scope=f.scope.nearestFuncAncestor()
        if scope:
            scope.funcYields=True

        pyle=[S('yield'),[args[0].compyle(stmtCollector,asStmt=False)]]
        stmtCollector(pyle)
        return None

class Reverse(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        # (reverse) is pure, so just eval the arg
        if asStmt:
            return args[0].compyle(stmtCollector,asStmt=True)

        assert not kwArgs
        assert len(args)==1
        return [S('adder.runtime.reverse'),
                [args[0].compyle(stmtCollector,asStmt=False)]]

    def __call__(self,l):
        l2=list(l)
        l2.reverse()
        return l2

class Stdenv(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        if asStmt:
            return None
        assert not kwArgs
        assert len(args)==0
        return [S('adder.runtime.stdenv'),[]]

class EvalPy(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        assert not kwArgs
        assert len(args)==1
        return [S('eval'),[args[0].compyle(stmtCollector,
                                           asStmt=False)]]

class ExecPy(Function):
    def mustBeStmt(self):
        return True

    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        assert not kwArgs
        assert len(args)==1
        assert asStmt

        stmtCollector([S('exec'),
                       [args[0].compyle(stmtCollector,
                                        asStmt=False)]])

class Begin(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        assert not kwArgs
        if not args:
            # (begin) with empty body is a no-op
            return

        body=[]
        def innerCollector(stmt):
            body.append(stmt)

        if (asStmt
            or (args and args[-1].mustBeStmt())
            ):
            stmts=args
            last=None
        else:
            stmts=args[:-1]
            last=args[-1] if args else None

        for a in stmts:
            exprPyle=a.compyle(innerCollector,asStmt=True)
            if exprPyle:
                innerCollector(exprPyle)

        if last:
            scratchVar=gensym('scratch')
            innerCollector([S(':='),
                            [scratchVar,
                             last.compyle(innerCollector,asStmt=False)]
                            ])
        else:
            scratchVar=None

        stmtCollector([S('begin'),body])
        return scratchVar

class Try(Function):
    def mustBeStmt(self):
        return True

    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        if not args:
            # try: with empty body is a no-op, no matter what
            #  its except: and finally: clauses may be.
            return

        assert asStmt

        bodyPyle=[]
        innerCollector=bodyPyle.append

        scratchVar=gensym('scratch')
        stmtCollector([S(':='),[scratchVar,None]])

        innerCollector([S(':='),
                        [scratchVar,
                         Begin().compyleCall(VarRef(f.scope,S('begin')),
                                             args,None,innerCollector,
                                             asStmt=False)]
                        ])

        exnPyles=[]

        for (klass,clause) in kwArgs:
            exnStmts=[]
            if klass=='finally':
                var=None
                assert len(clause.posArgs)==0
                clausePyle=clause.f.compyle(exnStmts.append,
                                            asStmt=False)
                if clausePyle:
                    exnStmts.append(clausePyle)
            else:
                var=clause.f.compyle(innerCollector,
                                     asStmt=False)
                assert len(clause.posArgs)==1
                clausePyle=clause.posArgs[0].compyle(exnStmts.append,
                                                     asStmt=True)
                if clausePyle:
                    exnStmts.append(clausePyle)
                
            exnPyles.append([klass,var,[S('begin'),exnStmts]])

        stmtCollector([S('try'),bodyPyle,exnPyles])
        return scratchVar

class While(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        assert args
        assert not kwArgs

        scratch=gensym('scratch')
        innerStmts=[]
        condPyle=args[0].compyle(stmtCollector,asStmt=False)
        for arg in args[1:]:
            expr=arg.compyle(innerStmts.append,asStmt=True)
            if expr:
                innerStmts.append(expr)

        stmtCollector([S('while'),[condPyle]+innerStmts])

class Dot(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        assert not kwArgs
        obj=args[0].compyle(stmtCollector,asStmt=False)
        return [S('.'),
                ([obj]
                 +list(map(lambda x: x.name,args[1:]))
                 )
                ]

class Import(Function):
    def mustBeStmt(self):
        return True

    def compyleCall(self,f,args,kwArgs,stmtCollector,*,asStmt=False):
        assert asStmt
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

    def compyle(self,stmtCollector,*,asStmt=False):
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
                    nonlocalRefs.add(varRef.compyle(stmtCollector,
                                                    asStmt=False))
                else:
                    if accessMode==Scope.Global:
                        if varRef.name not in required.transglobal:
                            globalRefs.add(varRef.compyle(stmtCollector,
                                                          asStmt=False))

        argListPyle=list(map(lambda sym: sym.compyle(stmtCollector,
                                                     asStmt=False),
                             self.argList))
        if globalRefs:
            argListPyle.append(S('&global'))
            argListPyle+=list(globalRefs)

        if nonlocalRefs:
            argListPyle.append(S('&nonlocal'))
            argListPyle+=list(nonlocalRefs)

        defStmt=[S('def'),
                 [self.name.compyle(stmtCollector,
                                    asStmt=False),
                  argListPyle]
                 ]

        def innerCollector(stmt):
            defStmt[1].append(stmt)

        scratchVar=gensym('scratch')

        for expr in self.bodyExprs[:-1]:
            pyleExpr=expr.compyle(innerCollector,asStmt=True)
            if pyleExpr:
                innerCollector(pyleExpr)

        if self.bodyExprs:
            lastExpr=self.bodyExprs[-1]
            pyleExpr=lastExpr.compyle(innerCollector,
                                      asStmt=lastExpr.mustBeStmt())
            if pyleExpr:
                if self.innerScope.funcYields:
                    innerCollector(pyleExpr)
                else:
                    innerCollector([S('return'),[pyleExpr]])

        stmtCollector(defStmt)
        return self.name.compyle(stmtCollector,asStmt=False)

def build(scope,gomer):
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
            return build(scope,f.transform(gomer))

    if gomer[0]==S('scope'):
        innerScope=Scope(scope)
        return build(innerScope,[S('begin')]+gomer[1:])

    if gomer[0]==S('defun'):
        innerScope=Scope(scope,isFunc=True)
        name=gomer[1]
        argList=gomer[2]
        body=gomer[3:]
        scope.addDef(name,None)
        nameVar=build(scope,name)
        nameVar.asDef=True
        for arg in argList:
            innerScope.addDef(arg,None,dontDisambiguate=True)
        return Call(scope,
                    build(scope,gomer[0]),
                    ([nameVar]
                     +[list(map(lambda a: build(innerScope,a),argList))]
                     +list(map(lambda g: build(innerScope,g),body))
                     )
                    )
    if gomer[0]==S('lambda'):
        innerScope=Scope(scope,isFunc=True)
        argList=gomer[1]
        body=gomer[2:]
        for arg in argList:
            innerScope.addDef(arg,None,dontDisambiguate=True)
        return Call(scope,
                    build(scope,gomer[0]),
                    ([list(map(lambda a: build(innerScope,a),argList))]
                     +list(map(lambda g: build(innerScope,g),body))
                     )
                    )
    if gomer[0]==S('quote'):
        assert len(gomer)==2
        if isinstance(gomer[1],list):
            return Constant(scope,gomer[1])
        else:
            return Constant(scope,gomer[1])

    res=Call(scope,
             build(scope,gomer[0]),
             list(map(lambda g: build(scope,g),
                      gomer[1:])))

    if gomer[0]==S('-gomer-try'):
        for (klass,clause) in res.kwArgs:
            innerScope=Scope(scope)
            if klass!='finally':
                innerScope.addDef(clause.f.name,None)
            clause.setScope(innerScope)
            clause.f.asDef=True

    if gomer[0] in [S('defvar'),S('defconst')]:
        res.posArgs[0].asDef=True
        res.scope.addDef(res.posArgs[0].name,None,
                         const=(gomer[0]==S('defconst'))
                         )

    if gomer[0]==S('.'):
        for arg in res.posArgs[1:]:
            arg.asDef=True

    return res

def evalTopLevel(expr,scope,globals,*,verbose=False,asStmt=False):
    pyleStmts=[]
    pythonFlat=''
    exprPyleList=build(scope,expr).compyle(pyleStmts.append,
                                           asStmt=asStmt)
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

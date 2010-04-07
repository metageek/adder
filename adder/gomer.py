# A structured internal representation; basically an annotated form of
#  Adder itself, with macros expanded.  Gets converted to Pyle.
#  Includes a basic interpreter, for use in macro expansion.

import itertools,re,pdb,adder.pyle
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

# Information known about a variable
class VarEntry:
    def __init__(self,name,initExpr,*,dontDisambiguate=False):
        self.name=name
        self.initExpr=initExpr
        self.neverModified=True
        self.dontDisambiguate=dontDisambiguate

    def markModified(self):
        self.neverModified=False

    def constValue(self):
        if not self.neverModified:
            raise NotConstant(None)
        if not self.initExpr:
            raise NotInitialized(self.name)
        return self.initExpr.constValue()

# Table of vars  known in a lexical scope
class Scope:
    nextId=1
    def __init__(self,parent,*,isFunc=False):
        self.id=Scope.nextId
        Scope.nextId+=1

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
                             (':=',Assignment()),
                             ('begin',Begin()),
                             ('return',Return()),
                             ('yield',Yield()),
                             ('raise',Raise()),
                             ('-gomer-try',Try()),
                             ('reverse',Reverse()),
                             ('reverse!',ReverseBang()),
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
                         'in',
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
                                 ]:
                self.addDef(S(name),Constant(self,value))
                self.transglobal.add(S(name))

    def nearestFuncAncestor(self):
        cur=self
        while cur and not (cur.isFunc):
            cur=cur.parent
        return cur

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
        return (isinstance(var,S)
                and (self.isLocal(var)
                     or (self.parent and var in self.parent)
                     )
                )

    def dontDisambiguate(self,name):
        return self.isLocal(name) and self.localDefs[name].dontDisambiguate

    def isLocal(self,var):
        return var in self.localDefs

    def __getitem__(self,varRef):
        if varRef.name in self.localDefs:
            return self.localDefs[varRef.name]
        if self.parent:
            return self.parent[varRef]
        raise Undefined(varRef)

    def addDef(self,var,initExpr,*,dontDisambiguate=False):
        if var in self.varAccesses:
            raise DefinedAfterUse(var,initExpr,self.varAccesses[var])
        if var in self.localDefs:
            raise Redefined(var,initExpr,self.localDefs[var])
        self.localDefs[var]=VarEntry(var,initExpr,
                                     dontDisambiguate=dontDisambiguate)

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

    def compyle(self,stmtCollector):
        if isinstance(self.value,S):
            return [S('adder.common.Symbol'),[str(self.value)]]
        if self.value is None:
            return self.value
        for t in [str,int,float,bool,tuple]:
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

        if self.name.isGensym() or self.name.startswith('&'):
            return S(self.name)

        if self.asDef:
            scope=self.scope
        else:
            scope=self.scopeRequired()
        if scope.parent==None:
            return S(self.name)

        if scope.dontDisambiguate(self.name):
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
        for var in self.f.varRefs():
            yield var

        for arg in self.allArgExprs():
            for var in arg.varRefs():
                yield var

    def isPureIn(self,containingScope):
        fv=self.f.constValue()
        if not fv.isPure():
            return False
        for arg in self.allArgExprs():
            if not arg.isPureIn(containingScope):
                return False
        return True

    def compyle(self,stmtCollector):
        fv=None
        try:
            fv=self.f.constValue()
        except NotConstant:
            pass
        except NotInitialized:
            pass
        except Undefined:
            pass

        if fv:
            if isinstance(fv,str):
                print('f:',self.f,fv)
            return fv.compyleCall(self.f,self.posArgs,self.kwArgs,stmtCollector)
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

class Function:
    def __init__(self):
        self.special=False

    def isPure(self):
        return False

    def compyleCall(self,f,args,kwArgs,stmtCollector):
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
    def compyleCall(self,f,args,kwArgs,stmtCollector):
        stmtCollector(PyleExpr.compyleCall(self,f,
                                           args,kwArgs,
                                           stmtCollector))

class Defun(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector):
        return UserFunction(f.scope,
                            args[1:],kwArgs,
                            None,
                            name=args[0]).compyle(stmtCollector)

class Lambda(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector):
        return UserFunction(f.scope,
                            args,kwArgs,
                            None).compyle(stmtCollector)

class Defvar(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector):
        assert args
        assert len(args) in [1,2]
        assert not kwArgs
        if len(args)==2:
            valueExpr=args[1]
            valuePyle=valueExpr.compyle(stmtCollector)
        else:
            valueExpr=valuePyle=None
        var=args[0].compyle(stmtCollector)
        stmtCollector([S(':='),[var,valuePyle]])
        return var

class Assignment(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector):
        assert args
        assert len(args)==2
        assert not kwArgs
        valueExpr=args[1]
        valuePyle=valueExpr.compyle(stmtCollector)
        var=args[0].compyle(stmtCollector)
        stmtCollector([S(':='),[var,valuePyle]])
        return var

class Raise(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector):
        assert not kwArgs
        pyle=[S('raise'),[args[0].compyle(stmtCollector)]]
        stmtCollector(pyle)
        return None

    def __call__(self,e):
        raise e

class Return(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector):
        assert not kwArgs
        pyle=[S('return'),[args[0].compyle(stmtCollector)]]
        stmtCollector(pyle)
        return None

class Yield(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector):
        assert not kwArgs

        scope=f.scope.nearestFuncAncestor()
        if scope:
            scope.funcYields=True

        pyle=[S('yield'),[args[0].compyle(stmtCollector)]]
        stmtCollector(pyle)
        return None

class Reverse(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector):
        assert not kwArgs
        assert len(args)==1
        return [S('adder.runtime.reverse'),[args[0].compyle(stmtCollector)]]

    def __call__(self,l):
        l2=list(l)
        l2.reverse()
        return l2

class ReverseBang(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector):
        assert not kwArgs
        assert len(args)==1
        scratchVar=gensym('scratch')
        stmtCollector([S(':='),
                       [scratchVar,args[0].compyle(stmtCollector)]
                       ])
        stmtCollector([[S('.'),
                        [scratchVar,S('reverse')]
                        ],
                       []])
        return scratchVar

    def __call__(self,l):
        l.reverse()

class Stdenv(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector):
        assert not kwArgs
        assert len(args)==0
        return [S('adder.runtime.stdenv'),[]]

class EvalPy(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector):
        assert not kwArgs
        assert len(args)==1
        return [S('eval'),[args[0].compyle(stmtCollector)]]

class ExecPy(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector):
        assert not kwArgs
        assert len(args)==1
        stmtCollector([S('exec'),[args[0].compyle(stmtCollector)]])

class Begin(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector):
        assert not kwArgs
        if not args:
            # (begin) with empty body is a no-op
            return

        body=[]
        def innerCollector(stmt):
            body.append(stmt)

        for a in args[:-1]:
            pyleExpr=a.compyle(innerCollector)
            if pyleExpr and not isinstance(pyleExpr,S):
                innerCollector(pyleExpr)

        scratchVar=gensym('scratch')
        innerCollector([S(':='),
                        [scratchVar,args[-1].compyle(innerCollector)]
                        ])

        stmtCollector([S('begin'),body])
        return scratchVar

class Try(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector):
        if not args:
            # try: with empty body is a no-op, no matter what
            #  its except: and finally: clauses may be.
            return

        bodyPyle=[]
        innerCollector=bodyPyle.append

        scratchVar=gensym('scratch')
        stmtCollector([S(':='),[scratchVar,None]])

        innerCollector([S(':='),
                        [scratchVar,
                         Begin().compyleCall(VarRef(f.scope,S('begin')),
                                             args,None,innerCollector)]
                        ])

        exnPyles=[]

        for (klass,clause) in kwArgs:
            exnStmts=[]
            if klass=='finally':
                var=None
                assert len(clause.posArgs)==0
                clausePyle=clause.f.compyle(exnStmts.append)
                if clausePyle:
                    exnStmts.append(clausePyle)
            else:
                var=clause.f.compyle(innerCollector)
                assert len(clause.posArgs)==1
                clausePyle=clause.posArgs[0].compyle(exnStmts.append)
                if clausePyle:
                    exnStmts.append(clausePyle)
                
            exnPyles.append([klass,var,[S('begin'),exnStmts]])

        stmtCollector([S('try'),bodyPyle,exnPyles])
        return scratchVar

class While(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector):
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

class Dot(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector):
        assert not kwArgs
        obj=args[0].compyle(stmtCollector)
        return [S('.'),
                ([obj]
                 +list(map(lambda x: x.name,args[1:]))
                 )
                ]

class Import(Function):
    def compyleCall(self,f,args,kwArgs,stmtCollector):
        assert len(args)==1
        assert isinstance(args[0],VarRef)
        stmtCollector([S('import'),[args[0].name]])
        return args[0].name

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
            for varRef in expr.varRefs():
                required=varRef.scopeRequired()
                if not required:
                    continue
                if required==self.innerScope:
                    continue
                if required.parent:
                    nonlocalRefs.add(varRef.compyle(stmtCollector))
                else:
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

        lastPyleExpr=None
        for expr in self.bodyExprs:
            pyleExpr=expr.compyle(innerCollector)
            innerCollector([S(':='),
                            [scratchVar,pyleExpr]])

        if self.bodyExprs:
            if not self.innerScope.funcYields:
                innerCollector([S('return'),[scratchVar]])

        stmtCollector(defStmt)
        return self.name.compyle(stmtCollector)

def build(scope,gomer):
    if isinstance(gomer,S):
        if gomer in scope:
            val=scope[VarRef(scope,gomer)]
            if (isinstance(val.initExpr,Constant)
                and type(val.initExpr.value) in [int,str,bool,float]
                ):
                return val.initExpr
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

    if gomer[0]==S('defvar'):
        res.posArgs[0].asDef=True
        res.scope.addDef(res.posArgs[0].name,None)

    if gomer[0]==S('.'):
        for arg in res.posArgs[1:]:
            arg.asDef=True

    return res

def evalTopLevel(expr,scope,globals):
    pyleStmts=[]
    pythonFlat=''
    exprPyleList=build(scope,expr).compyle(pyleStmts.append)
    if exprPyleList:
        exprPyleAST=adder.pyle.buildExpr(exprPyleList)
        exprPython=exprPyleAST.toPython(False)
    else:
        exprPython=None
    for pyleList in pyleStmts:
        pyleAST=adder.pyle.buildStmt(pyleList)
        pythonTree=pyleAST.toPythonTree()
        pythonFlat+=adder.pyle.flatten(pythonTree)
    if pythonFlat:
        exec(pythonFlat,globals)
    if exprPython is not None:
        return eval(exprPython,globals)

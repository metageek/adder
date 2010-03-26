# A structured internal representation; basically an annotated form of
#  Adder itself, with macros expanded.  Gets converted to Pyle.
#  Includes a basic interpreter, for use in macro expansion.

import itertools,re,pdb
from adder.common import Symbol as S

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
    def __init__(self,name,initExpr):
        self.name=name
        self.initExpr=initExpr
        self.neverModified=True

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
    def __init__(self,parent):
        self.parent=parent
        self.localDefs={}
        self.varAccesses={}

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
        return (self.isLocal(var)
                or (self.parent and var in self.parent)
                )

    def isLocal(self,var):
        return var in self.localDefs

    def __getitem__(self,varRef):
        if varRef.name in self.localDefs:
            return self.localDefs[varRef.name]
        if self.parent:
            return self.parent[varRef]
        raise Undefined(varRef)

    def addDef(self,var,initExpr):
        if var in self.varAccesses:
            raise DefinedAfterUse(var,initExpr,self.varAccesses[var])
        if var in self.localDefs:
            raise Redefined(var,initExpr,self.localDefs[var])
        self.localDefs[var]=VarEntry(var,initExpr)

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

class VarRef(Expr):
    def __init__(self,scope,name):
        Expr.__init__(self,scope)
        self.name=name

    def evaluate(self,env):
        return env[self]

    def constValue(self):
        try:
            return self.scope[self].constValue()
        except NotConstant: # the one from VarEntry will have None for its expr
            raise NotConstant(self)

    def scopeRequired(self):
        cur=self.scope
        while cur:
            if cur.isLocal(self.name):
                return cur
            cur=cur.parent
        raise Undefined(self)

    def varRefs(self):
        return [self]

    def isPureIn(self,containingScope):
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

class Call(Expr):
    def __init__(self,scope,f,args):
        Expr.__init__(self,scope)
        self.f=f
        self.args=list(args)

    def evaluate(self,env):
        fv=self.f.evaluate(env)
        if fv.special:
            args=self.args
        else:
            args=list(map(lambda a: a.evaluate(env),self.args))
        return fv(*args)

    def constValue(self):
        fv=self.f.constValue()
        if not fv.isPure():
            raise NotConstant(self)
        argVs=list(map(lambda a: a.constValue(),self.args))
        return fv(*argVs)

    def scopeRequired(self):
        required=self.f.scopeRequired()
        for arg in self.args:
            required=required.commonAncestor(arg.scopeRequired())
        return required

    def varRefs(self):
        for var in self.f.varRefs():
            yield var

        for arg in self.args:
            for var in arg.varRefs():
                yield var

    def isPureIn(self,containingScope):
        fv=self.f.constValue()
        if not fv.isPure():
            return False
        for arg in self.args:
            if not arg.isPureIn(containingScope):
                return False
        return True

class Function:
    def isPure(self):
        return False

class NativeFunction(Function):
    def __init__(self,f,pure,*,special=False):
        self.pure=pure
        self.f=f
        self.special=special

    def __call__(self,*args):
        return self.f(*args)

    def isPure(self):
        return self.pure

class UserFunction(Function):
    # The fExpr should be the (define) or (lambda) that created this function.
    def __init__(self,fExpr,outerEnv):
        self.special=False
        self.fExpr=fExpr
        assert isinstance(fExpr,Call)
        assert isinstance(fExpr.f,VarRef)
        assert fExpr.f.name in {'defun','lambda'}
        assert fExpr.args
        offset=(1 if fExpr.f.name=='defun' else 0)
        assert isinstance(fExpr.args[offset+0],list)
        for arg in fExpr.args[offset+0]:
            assert isinstance(arg,VarRef)
        self.argList=fExpr.args[offset+0]
        self.bodyExprs=fExpr.args[(offset+1):]
        if self.bodyExprs:
            self.innerScope=self.bodyExprs[0].scope
            self.outerEnv=outerEnv

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
        localScope=self.bodyExprs[0].scope
        for expr in self.bodyExprs:
            if not expr.isPureIn(localScope):
                return False
        return True

def build(scope,gomer):
    if isinstance(gomer,S):
        return VarRef(scope,gomer)
    if not isinstance(gomer,list):
        return Constant(scope,gomer)
    assert gomer
    assert gomer[0]
    if gomer[0]==S('defun') or gomer[0]==S('lambda'):
        innerScope=Scope(scope)
    else:
        innerScope=scope
    return Call(scope,
                build(scope,gomer[0]),
                list(map(lambda g: build(innerScope,g),
                         gomer[1:])))

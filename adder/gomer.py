# A structured internal representation; basically an annotated form of
#  Adder itself, with macros expanded.  Gets converted to Pyle.

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
            raise NotConstant()
        return self.initExpr.constValue()

# Table of vars  known in a lexical scope
class Scope:
    def __init__(self,parent):
        self.parent=parent
        self.localDefs={}
        self.varAccesses={}

    def __contains__(self,var):
        return (self.isLocal(var)
                or (self.parent and var in self.parent)
                )

    def isLocal(self,var):
        return var in self.localDefs

    def undefinedVars(self):
        for v in self.varsAccessed:
            if v not in self:
                yield (v,self.varsAccessed[v])

    def __getitem__(self,varRef):
        if varRef.name in self.localDefs:
            return self.localDefs[varRef.name]
        if self.parent:
            return self.parent[varRef]
        raise Undefined(varRef.name,varRef)

    def addDef(self,var,initExpr):
        if var in self.varsAccessed:
            raise DefinedAfterUse(var,initExpr,self.varsAccessed[var])
        if var in self.localDefs:
            raise Redefined(var,initExpr,self.localDefs[var])
        self.localDefs[var]=VarEntry(var,initExpr)

    def _addAccess(self,var,expr):
        accesses=self.varsAccessed.get(var,{})
        accesses.add(expr)

    def addRead(self,var,expr):
        self._addAccess(expr)

    def addWrite(self,var,expr):
        self._addAccess(expr)
        cur=self
        while cur:
            if var in cur.localDefs:
                cur.localDefs[var].markModified()
                break
            cur=cur.parent

class Expr:
    def __init__(self,scope):
        self.scope=scope

    def constValue(self):
        raise NotConstant()

class Constant(Expr):
    def __init__(self,scope,value):
        Expr.__init__(self,scope)
        self.value=value

    def constValue(self):
        return self.value

class Call(Expr):
    def __init__(self,scope,f,args):
        Expr.__init__(self,scope)
        self.f=f
        self.args=list(args)

    def constValue(self):
        fv=self.f.constValue()
        if not fv.isPure():
            raise NotConstant()
        argVs=map(lambda a: a.constValue(),self.args)
        return fv(*argVs)

class VarRef(Expr):
    def __init__(self,scope,name):
        Expr.__init__(self,scope)
        self.name=name

    def constValue(self):
        return self.scope[self].constValue()

class Function:
    def isPure(self):
        return False

class NativeFunction(Function):
    def __init__(self,f,pure):
        self.pure=pure
        self.__call__=f

    def isPure(self):
        return self.pure


class UserFunction(Function):
    def __init__(self,fExpr):
        self.fExpr=fExpr

    def isPure(self):
        

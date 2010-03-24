# Python Lisp-Like Encoding.  IL which maps directly to Python.

def withParens(s,inParens):
    if inParens:
        return '(%s)' % s
    else:
        return s

class Expr:
    pass

class SimpleExpr(Expr):
    def __init__(self,py):
        self.py=py

    def toPython(self,inParens):
        return self.py

class Constant(SimpleExpr):
    def __init__(self,c):
        SimpleExpr.__init__(self,repr(c))

class VarExpr(SimpleExpr):
    def __init__(self,v):
        SimpleExpr.__init__(self,v)

class BinaryOperator(Expr):
    def __init__(self,operator,left,right):
        self.operator=operator
        self.left=left
        self.right=right

    def toPython(self,inParens):
        return withParens('%s %s %s' % (self.left.toPython(True),
                                        self.operator,
                                        self.right.toPython(True)),
                          inParens)

class UnaryOperator(Expr):
    def __init__(self,operator,operand):
        self.operator=operator
        self.operand=operand

    def toPython(self,inParens):
        return withParens('%s %s' % (self.operator,
                                     self.operand.toPython(True)),
                          inParens)

class CallExpr(Expr):
    def __init__(self,f,posArgs,kwArgs):
        self.f=f
        self.posArgs=posArgs
        self.kwArgs=kwArgs

    def toPython(self,inParens):
        res=(self.f.toPython(True)
             +'('
             +', '.join(map(lambda expr: expr.toPython(False),
                           self.posArgs)))
        for (argName,argExpr) in kwArgs.iteritems():
            res+=', %s=%s' % (argName,argExpr.toPython(False))
        res+=')'
        return res

class IfOperator(Expr):
    def __init__(self,condExpr,thenExpr,elseExpr):
        self.condExpr=condExpr
        self.thenExpr=thenExpr
        self.elseExpr=elseExpr

    def toPython(self,inParens):
        return withParens(('if %s then %s else %s'
                           % (self.condExpr.toPython(True),
                              self.thenExpr.toPython(True),
                              self.elseExpr.toPython(True))),
                          inParens)

class Stmt:
    pass

class Block(Stmt):
    def __init__(self,stmts):
        self.stmts=stmts

    def genPython(self,indent):
        for s in self.stmts:
            for line in s.genPython(indent):
                yield line

class IfStmt(Stmt):
    def __init__(self,condExpr,thenStmt,elseStmt):
        self.condExpr=condExpr
        self.thenStmt=thenStmt
        self.elseStmt=elseStmt

    def genPython(self,indent):
        yield prefix(indent)+'if %s:'
        for line in self.thenStmt.genPython(indent+2):
            yield line
        yield prefix(indent)+'if %s:'
        for line in self.elseStmt.genPython(indent+2):
            yield line

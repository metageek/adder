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
    indentStep=4

    def flatten(self,tree,depth=0):
        if isinstance(tree,str):
            return (' '*(depth*Stmt.indentStep))+tree+'\n'
        return ''.join(map(lambda t: flatten(t,depth+1)))

    def toPythonFlat(self):
        return self.flatten(self.toPythonTree())

class Block(Stmt):
    def __init__(self,stmts):
        self.stmts=stmts

    def toPythonTree(self):
        return list(map(lambda s: s.toPythonTree(),self.stmts))

class IfStmt(Stmt):
    def __init__(self,condExpr,thenStmt,elseStmt):
        self.condExpr=condExpr
        self.thenStmt=thenStmt
        self.elseStmt=elseStmt

    def toPythonTree(self):
        return ['if %s:' % self.condExpr.toPython(False),
                self.thenStmt.toPythonTree(),
                'else:',
                self.elseStmt.toPythonTree()]

class WhileStmt(Stmt):
    def __init__(self,condExpr,body):
        self.condExpr=condExpr
        self.body=body

    def toPythonTree(self):
        return ['while %s:' % self.condExpr.toPython(False),
                self.body.toPythonTree()]

class DefStmt(Stmt):
    def __init__(self,fname,fixedArgs,optionalArgs,kwArgs,body):
        self.fname=fname
        self.fixedArgs=fixedArgs
        self.optionalArgs=optionalArgs
        self.kwArgs=kwArgs
        self.body=body

    def toPythonTree(self):
        def optArgToPy(optionalArg):
            (name,defExpr)=optionalArg
            return '%s=%s' % (name,defExpr.toPython(False))

        def kwArgToPy(kwArg):
            if isinstance(kwArg,str):
                return kwArg
            else:
                (name,defExpr)=kwArg
                return '%s=%s' % (name,defExpr.toPython(False))

        fixedArgsPy=self.fixedArgs
        optionalArgsPy=map(optArgToPy,self.optionalArgs)
        nonKwArgsPy=list(fixedArgsPy)+list(optionalArgsPy)
        kwArgsPy=map(kwArgToPy,self.kwArgs)

        return ['def %s(%s%s%s):' % (self.fname,
                                     ','.join(nonKwArgsPy),
                                     '*' if kwArgs else '',
                                     ','.join(kwArgsPy)
                                     ),
                self.body.toPythonTree()]

class ReturnStmt(Stmt):
    def __init__(self,returnExpr):
        self.returnExpr=returnExpr

    def toPythonTree(self):
        return 'return %s' % self.returnExpr.toPython(False)

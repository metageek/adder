# Python Lisp-Like Encoding.  IL which maps directly to Python.  Does not encode all
#  of Python, only the bits which Adder will need to generate.

import itertools,re

def withParens(s,inParens):
    if inParens:
        return '(%s)' % s
    else:
        return s

class Expr:
    def isLvalue(self):
        return False

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

    def isLvalue(self):
        return True

noPaddingRe=re.compile('^[^a-zA-Z]+$')

class BinaryOperator(Expr):
    def __init__(self,operator,left,right):
        self.operator=operator
        self.padding='' if noPaddingRe.match(operator) else ' '
        self.left=left
        self.right=right

    def toPython(self,inParens):
        return withParens('%s%s%s%s%s' % (self.left.toPython(True),
                                          self.padding,
                                          self.operator,
                                          self.padding,
                                          self.right.toPython(True)),
                          inParens)

class IndexOperator(Expr):
    def __init__(self,left,right):
        self.left=left
        self.right=right

    def isLvalue(self):
        return True

    def toPython(self,inParens):
        return '%s[%s]' % (self.left.toPython(True),
                           self.right.toPython(False)
                           )


class UnaryOperator(Expr):
    def __init__(self,operator,operand):
        self.operator=operator
        self.operand=operand
        self.padding='' if noPaddingRe.match(operator) else ' '

    def toPython(self,inParens):
        return withParens('%s%s%s' % (self.operator,
                                      self.padding,
                                      self.operand.toPython(True)),
                          inParens)

class CallExpr(Expr):
    def __init__(self,f,posArgs,kwArgs=None):
        self.f=f
        self.posArgs=posArgs
        self.kwArgs=kwArgs or {}

    def toPython(self,inParens):
        res=self.f.toPython(True)+'('

        posArgsStrs=map(lambda expr: expr.toPython(False),
                        self.posArgs)
        kwArgsStrs=map(lambda a: '%s=%s' % (a[0],a[1].toPython(False)),
                       self.kwArgs.items())

        res+=', '.join(itertools.chain(posArgsStrs,kwArgsStrs))

        res+=')'
        return res

class IfOperator(Expr):
    def __init__(self,condExpr,thenExpr,elseExpr):
        self.condExpr=condExpr
        self.thenExpr=thenExpr
        self.elseExpr=elseExpr

    def toPython(self,inParens):
        return withParens(('%s if %s else %s'
                           % (self.thenExpr.toPython(True),
                              self.condExpr.toPython(True),
                              self.elseExpr.toPython(True))),
                          inParens)

class DotExpr(Expr):
    def __init__(self,base,path):
        self.base=base
        self.path=path

    def isLvalue(self):
        return True

    def toPython(self,inParens):
        return '.'.join([self.base.toPython(True)]+self.path)

class ListConstructor(Expr):
    def __init__(self,elementExprs):
        self.elementExprs=elementExprs

    def toPython(self,inParens):
        return ('[%s]'
                % ', '.join(map(lambda e: e.toPython(False),self.elementExprs))
                )

class TupleConstructor(Expr):
    def __init__(self,elementExprs):
        self.elementExprs=elementExprs

    def toPython(self,inParens):
        if len(self.elementExprs)==1:
            return '(%s,)' % self.elementExprs[0].toPython(False)
        else:
            return ('(%s)'
                    % ', '.join(map(lambda e: e.toPython(False),self.elementExprs))
                    )

class DictConstructor(Expr):
    def __init__(self,pairExprs):
        self.pairExprs=pairExprs

    def toPython(self,inParens):
        return ('{%s}'
                % ', '.join(map(lambda p: '%s: %s' % (p[0].toPython(False),
                                                      p[1].toPython(False)),
                                self.pairExprs))
                )

class SetConstructor(Expr):
    def __init__(self,elementExprs):
        self.elementExprs=elementExprs

    def toPython(self,inParens):
        if self.elementExprs:
            return ('{%s}'
                    % ', '.join(map(lambda e: e.toPython(False),self.elementExprs))
                    )
        else:
            return 'set()'

class Stmt:
    indentStep=4

    def flatten(self,tree,depth=0):
        if isinstance(tree,str):
            return (' '*(depth*Stmt.indentStep))+tree+'\n'

        if isinstance(tree,list):
            indent=1
        else:
            indent=0

        return ''.join(map(lambda t: self.flatten(t,depth+indent),tree))

    def toPythonFlat(self):
        return self.flatten(self.toPythonTree())

class Assignment(Stmt):
    def __init__(self,lvalue,rvalue):
        assert lvalue.isLvalue()
        self.lvalue=lvalue
        self.rvalue=rvalue

    def toPythonTree(self):
        return '%s=%s' % (self.lvalue.toPython(False),
                          self.rvalue.toPython(False))

class Block(Stmt):
    def __init__(self,stmts):
        self.stmts=stmts

    def toPythonTree(self):
        return tuple(map(lambda s: s.toPythonTree(),self.stmts))

class IfStmt(Stmt):
    def __init__(self,condExpr,thenStmt,elseStmt):
        self.condExpr=condExpr
        self.thenStmt=thenStmt
        self.elseStmt=elseStmt

    def toPythonTree(self):
        return ('if %s:' % self.condExpr.toPython(False),
                [self.thenStmt.toPythonTree()],
                'else:',
                [self.elseStmt.toPythonTree()])

class WhileStmt(Stmt):
    def __init__(self,condExpr,body):
        self.condExpr=condExpr
        self.body=body

    def toPythonTree(self):
        return ('while %s:' % self.condExpr.toPython(False),
                self.body.toPythonTree())

class ReturnStmt(Stmt):
    def __init__(self,returnExpr):
        self.returnExpr=returnExpr

    def toPythonTree(self):
        return 'return %s' % self.returnExpr.toPython(False)

class DefStmt(Stmt):
    def __init__(self,fname,fixedArgs,optionalArgs,kwArgs,body,globals=None,nonlocals=None):
        self.fname=fname
        self.fixedArgs=fixedArgs
        self.optionalArgs=optionalArgs
        self.kwArgs=kwArgs
        self.body=body
        self.globals=globals or []
        self.nonlocals=nonlocals or []

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

        return ('def %s(%s%s%s%s):' % (self.fname,
                                     ','.join(nonKwArgsPy),
                                     ',' if self.kwArgs and nonKwArgsPy else '',
                                     '*,' if self.kwArgs else '',
                                     ','.join(kwArgsPy)
                                     ),
                ( (['global '+','.join(self.globals)] if self.globals else [])
                 +(['nonlocal '+','.join(self.nonlocals)] if self.nonlocals else [])
                  +[self.body.toPythonTree() if self.body else 'pass']
                  )
                )

class ClassStmt(Stmt):
    def __init__(self,name,parents,body):
        self.name=name
        self.parents=parents
        self.body=body

    def toPythonTree(self):
        return ('class %s(%s):' % (self.name,
                                   ','.join(self.parents)),
                [self.body.toPythonTree() if self.body else 'pass']
                )

class ImportStmt(Stmt):
    def __init__(self,modules):
        assert modules
        self.modules=modules

    def toPythonTree(self):
        return 'import %s' % (', '.join(self.modules))

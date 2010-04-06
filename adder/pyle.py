# Python Lisp-Like Encoding.  IL which maps directly to Python; does
#  not include semantics which can't be translated directly.  Does not
#  encode all of Python, only the bits which Adder will need to
#  generate.  Just easier for Adder to generate than Python text.
#  (Also, I hold out hope that it can target py3 or py2,
#  transparently.  For that to be useful, though, the compiler itself
#  would also have to work in both.)

from adder.common import Symbol as S

import itertools,re,pdb

def withParens(s,inParens):
    if inParens:
        return '(%s)' % s
    else:
        return s

def treemap(f,x):
    if isinstance(x,list):
        return list(map(lambda elt: treemap(f,elt),x))
    return f(x)

def buildExpr(pyle):
    if isinstance(pyle,S):
        return VarExpr(pyle)
    if pyle is None:
        return Constant(pyle)
    for t in [str,int,float,bool,tuple]:
        if isinstance(pyle,t):
            return Constant(pyle)

    assert isinstance(pyle,list)
    assert pyle
    for t in [int,float,bool]:
        assert not isinstance(pyle[0],t)
    assert not (isinstance(pyle[0],str) and not isinstance(pyle[0],S))

    if isinstance(pyle[0],S):
        if pyle[0]==S('quote'):
            assert len(pyle[1])==1
            return Constant(pyle[1][0])

        if pyle[0]==S('[]'):
            assert len(pyle[1])==2
            return IndexOperator(buildExpr(pyle[1][0]),
                                 buildExpr(pyle[1][1]))

        if pyle[0]==S('slice'):
            assert len(pyle[1]) in [2,3]
            if len(pyle[1])==2:
                return SliceOperator(buildExpr(pyle[1][0]),
                                     buildExpr(pyle[1][1]))
            else:
                return SliceOperator(buildExpr(pyle[1][0]),
                                     buildExpr(pyle[1][1]),
                                     buildExpr(pyle[1][2]))

        if pyle[0]==S('if'):
            assert len(pyle[1])==3
            return IfOperator(buildExpr(pyle[1][0]),
                              buildExpr(pyle[1][1]),
                              buildExpr(pyle[1][2]))

        if pyle[0]==S('.'):
            assert len(pyle)>=2
            if len(pyle[1])==1:
                return buildExpr(pyle[1][0])
            return DotExpr(buildExpr(pyle[1][0]),pyle[1][1:])

        if pyle[0]==S('mk-list'):
            return ListConstructor(list(map(buildExpr,pyle[1])))

        if pyle[0]==S('mk-tuple'):
            return TupleConstructor(list(map(buildExpr,pyle[1])))

        if pyle[0]==S('mk-set'):
            return SetConstructor(list(map(buildExpr,pyle[1])))

        if pyle[0]==S('mk-dict'):
            assert len(pyle)==3
            return DictConstructor(list(map(lambda kx: (buildExpr(kx[0]),
                                                        buildExpr(kx[1])),
                                            pyle[2] or [])))

        if pyle[0]==S('apply'):
            f=buildExpr(pyle[1][0])
            posArgs=buildExpr(pyle[1][1])
            if len(pyle[1])==3:
                return Apply(f,posArgs,buildExpr(pyle[1][2]))
            else:
                return Apply(f,posArgs,None)

        if pyle[0]==S('-'):
            assert len(pyle[1]) in [1,2]
            if len(pyle[1])==2:
                return BinaryOperator(pyle[0],
                                      buildExpr(pyle[1][0]),
                                      buildExpr(pyle[1][1]))
            else:
                return UnaryOperator(pyle[0],
                                     buildExpr(pyle[1][0]))

        if pyle[0] in buildExpr.binaryOperators:
            assert len(pyle[1])==2
            return BinaryOperator(pyle[0],
                                  buildExpr(pyle[1][0]),
                                  buildExpr(pyle[1][1]))

        if pyle[0] in buildExpr.unaryOperators:
            assert len(pyle[1])==1
            return UnaryOperator(pyle[0],buildExpr(pyle[1][0]))

    if len(pyle)==2:
        kwArgs=[]
    else:
        kwArgs=pyle[2]

    f=pyle[0]
    if f==S('mk-symbol'):
        f=S('adder.common.Symbol')

    return CallExpr(buildExpr(f),
                    list(map(buildExpr,pyle[1])),
                    dict(map(lambda kx: (kx[0], buildExpr(kx[1])),
                             kwArgs)
                         )
                    )

buildExpr.binaryOperators=set(map(S,['==','!=','<','<=','>','>=',
                                     '+','*','/','//','%',
                                     'in']))
buildExpr.unaryOperators=set(map(S,['not','and','or']))

def buildStmt(pyle):
    if isinstance(pyle,S):
        return Nop()
    if not isinstance(pyle,list):
        pdb.set_trace()
    assert isinstance(pyle,list)
    if not pyle:
        pdb.set_trace()
    assert pyle

    if pyle[0]==S(':='):
        assert len(pyle[1])==2
        return Assignment(buildExpr(pyle[1][0]),
                          buildExpr(pyle[1][1]))

    if pyle[0]==S('begin'):
        if not pyle[1]:
            return Nop()
        return Block(list(map(buildStmt,pyle[1])))

    if pyle[0]==S('if'):
        assert len(pyle[1]) in [2,3]
        elseStmt=buildStmt(pyle[1][2]) if len(pyle[1])==3 else None
        return IfStmt(buildExpr(pyle[1][0]),
                      buildStmt(pyle[1][1]),
                      elseStmt)

    if pyle[0]==S('while'):
        assert len(pyle[1])>=1
        return WhileStmt(buildExpr(pyle[1][0]),
                         maybeBlock(list(map(buildStmt,pyle[1][1:]))))

    if pyle[0]==S('break'):
        assert len(pyle[1])==0
        return BreakStmt()

    if pyle[0]==S('continue'):
        assert len(pyle[1])==0
        return ContinueStmt()

    if pyle[0]==S('return'):
        assert len(pyle)==2
        assert len(pyle[1])==1
        return ReturnStmt(buildExpr(pyle[1][0]),)

    if pyle[0]==S('yield'):
        assert len(pyle)==2
        assert len(pyle[1])==1
        return YieldStmt(buildExpr(pyle[1][0]),)

    if pyle[0]==S('raise'):
        assert len(pyle)==2
        assert len(pyle[1])==1
        return RaiseStmt(buildExpr(pyle[1][0]),)

    if pyle[0]==S('exec'):
        assert len(pyle)==2
        assert len(pyle[1])==1
        return ExecStmt(buildExpr(pyle[1][0]),)

    if pyle[0]==S('def'):
        assert len(pyle[1])>=2
        assert isinstance(pyle[1][0],S)
        assert isinstance(pyle[1][1],list)
        fixedArgs=[]
        optionalArgs=[]
        kwArgs=[]
        globals=[]
        nonlocals=[]
        stateToCollector={'fixed': fixedArgs,
                          'optional': optionalArgs,
                          'key': kwArgs,
                          'global': globals,
                          'nonlocal': nonlocals}
        state='fixed'
        for arg in pyle[1][1]:
            if isinstance(arg,S) and arg[0]=='&':
                state=arg[1:]
                continue
            if (state=='optional' or state=='key'):
                assert isinstance(arg,tuple) or isinstance(arg,S)
                if state=='optional' and not isinstance(arg,tuple):
                    arg=(arg,None)
            else:
                if not isinstance(arg,S):
                    print('arg-not-S',arg)
                assert isinstance(arg,S)
            if isinstance(arg,tuple):
                assert len(arg)==2
                assert isinstance(arg[0],S)
                arg=(arg[0],buildExpr(arg[1]))
            stateToCollector[state].append(arg)
        return DefStmt(pyle[1][0],
                       fixedArgs,optionalArgs,kwArgs,
                       maybeBlock(list(map(buildStmt,pyle[1][2:]))),
                       globals,nonlocals)

    if pyle[0]==S('class'):
        assert pyle[1]
        assert isinstance(pyle[1][0],S)
        assert isinstance(pyle[1][1],list)
        for parent in pyle[1][1]:
            assert isinstance(parent,S)

        return ClassStmt(pyle[1][0],pyle[1][1],
                         maybeBlock(list(map(buildStmt,pyle[1][2:])),True))

    if pyle[0]==S('import'):
        for module in pyle[1]:
            assert isinstance(module,S)

        return ImportStmt(pyle[1])

    if pyle[0]==S('begin'):
        return maybeBlock(pyle[1])

    if pyle[0]==S('try'):
        def buildExn(kx):
            (klass,var,clause)=kx
            return (klass,var,buildStmt(clause))
        return TryStmt(list(map(buildStmt,pyle[1])),
                       list(map(buildExn,pyle[2])))

    return ExprStmt(buildExpr(pyle))

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

    def toPython(self,inParens):
        return '.'.join(map(lambda part: S(part).toPython(),
                            self.py.split('.')))

    def isLvalue(self):
        return True

class Quote(Expr):
    def __init__(self,arg):
        self.arg=arg

    def toPython(self,inParens):
        if isinstance(self.arg,Expr):
            return self.arg.toPython(inParens)
        else:
            return repr(self.arg)

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

class SliceOperator(Expr):
    def __init__(self,left,low,high=None):
        self.left=left
        self.low=low
        self.high=high

    def toPython(self,inParens):
        return '%s[%s:%s]' % (self.left.toPython(True),
                              self.low.toPython(False),
                              ('' if self.high is None
                               else self.high.toPython(False))
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
                                sorted(self.pairExprs,
                                       key=lambda p: p[0].py)))
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

class Apply(Expr):
    def __init__(self,f,posArgs,kwArgs):
        self.f=f
        self.posArgs=posArgs
        self.kwArgs=kwArgs

    def isLvalue(self):
        return False

    def toPython(self,inParens):
        if self.kwArgs:
            return '%s(*%s, **%s)' % (self.f.toPython(True),
                                      self.posArgs.toPython(True),
                                      self.kwArgs.toPython(True))
        else:
            return '%s(*%s)' % (self.f.toPython(True),
                                self.posArgs.toPython(True))

def flatten(tree,depth=0):
    if isinstance(tree,str):
        return (' '*(depth*Stmt.indentStep))+tree+'\n'

    if isinstance(tree,list):
        indent=1
    else:
        indent=0

    return ''.join(map(lambda t: flatten(t,depth+indent),tree))

class Stmt:
    indentStep=4

    def toPythonFlat(self):
        return flatten(self.toPythonTree())

class Assignment(Stmt):
    def __init__(self,lvalue,rvalue):
        assert lvalue.isLvalue()
        self.lvalue=lvalue
        self.rvalue=rvalue

    def toPythonTree(self):
        return '%s=%s' % (self.lvalue.toPython(False),
                          self.rvalue.toPython(False))

class Nop(Stmt):
    def __init__(self,passable=False):
        self.passable=passable

    def toPythonTree(self):
        return 'pass' if self.passable else 'assert True'

def maybeBlock(stmts,passable=False):
    if stmts:
        if len(stmts)>1:
            return Block(stmts)
        return stmts[0]
    return Nop(passable)

class Block(Stmt):
    def __init__(self,stmts):
        self.stmts=stmts

    def toPythonTree(self):
        stmts=[]
        for stmt in self.stmts:
            if isinstance(stmt,Nop):
                continue
            stmts.append(stmt.toPythonTree())
        if stmts:
            return tuple(stmts)
        else:
            return (Nop().toPythonTree(),)

class IfStmt(Stmt):
    def __init__(self,condExpr,thenStmt,elseStmt=None):
        self.condExpr=condExpr
        self.thenStmt=thenStmt
        self.elseStmt=elseStmt

    def toPythonTree(self):
        res=('if %s:' % self.condExpr.toPython(False),
             [self.thenStmt.toPythonTree()])
        if self.elseStmt:
            res=res+('else:',
                     [self.elseStmt.toPythonTree()])
        return res

class WhileStmt(Stmt):
    def __init__(self,condExpr,body):
        self.condExpr=condExpr
        self.body=body

    def toPythonTree(self):
        return ('while %s:' % self.condExpr.toPython(False),
                [self.body.toPythonTree() if self.body else 'pass'])

class BreakStmt(Stmt):
    def toPythonTree(self):
        return 'break'

class ContinueStmt(Stmt):
    def toPythonTree(self):
        return 'continue'

class ReturnStmt(Stmt):
    def __init__(self,returnExpr):
        self.returnExpr=returnExpr

    def toPythonTree(self):
        return 'return %s' % self.returnExpr.toPython(False)

class YieldStmt(Stmt):
    def __init__(self,yieldExpr):
        self.yieldExpr=yieldExpr

    def toPythonTree(self):
        return 'yield %s' % self.yieldExpr.toPython(False)

class RaiseStmt(Stmt):
    def __init__(self,raiseExpr):
        self.raiseExpr=raiseExpr

    def toPythonTree(self):
        return 'raise %s' % self.raiseExpr.toPython(False)

class ExecStmt(Stmt):
    def __init__(self,execExpr):
        self.execExpr=execExpr

    def toPythonTree(self):
        return 'exec(%s)' % self.execExpr.toPython(False)

class DefStmt(Stmt):
    def __init__(self,fname,fixedArgs,optionalArgs,kwArgs,body,globals=None,nonlocals=None):
        self.fname=S(fname)
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

        return ('def %s(%s%s%s%s):' % (self.fname.toPython(),
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

class ExprStmt(Stmt):
    def __init__(self,expr):
        self.expr=expr

    def toPythonTree(self):
        return self.expr.toPython(False)

class TryStmt(Stmt):
    def __init__(self,body,exns):
        self.body=body
        self.exns=exns

    def toPythonTree(self):
        res=['try:',
             list(map(lambda stmt: stmt.toPythonTree(),self.body))]
        sawFinally=False
        for (klass,var,clause) in self.exns:
            assert not sawFinally
            if klass=='finally':
                assert not var
                res.append('finally:')
                sawFinally=True
            else:
                assert var
                res.append('except %s as %s:' % (klass,var))
            res.append([clause.toPythonTree(),])
        return tuple(res)

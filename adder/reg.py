# And intermediate form for use in compiling Gomer to Pyle.  Inspired
#  by 3-address form.  The main characteristic is that there are no
#  function arguments which include function calls.  See
#  doc/compiler.html for the syntax.

from adder.common import Symbol as S

indentStep=2

def flatten(tree,depth=0):
    if isinstance(tree,str):
        return (' '*(depth*indentStep))+tree+'\n'

    if isinstance(tree,list):
        indent=1
    else:
        indent=0

    return ''.join(map(lambda t: flatten(t,depth+indent),tree))

class IL:
    def toPythonTree(self):
        return str(self)

    def toPythonFlat(self):
        return flatten(self.toPythonTree())

def toPythonTree(il):
    return il.toPythonTree()

def toPythonFlat(il):
    return il.toPythonFlat()

class Any(IL):
    pass

class Simple(Any):
    pass

class Var(Simple):
    def __init__(self,varSym):
        assert isinstance(varSym,S)
        self.varSym=varSym

    def __str__(self):
        return str(self.varSym)

class Literal(Simple):
    def __init__(self,value):
        assert (isinstance(value,int)
                or isinstance(value,str)
                or isinstance(value,float)
                or isinstance(value,bool)
                or isinstance(value,S)
                )
        self.value=value

    def __str__(self):
        return repr(self.value)

    def toPythonTree(self):
        return repr(self.value)

class List(Any):
    def __init__(self,value):
        assert isinstance(value,list)
        for v in value:
            assert isinstance(v,Any)
        self.value=value

    def __str__(self):
        return '(%s)' % (' '.join(map(str,self.value)))

    def toPythonTree(self):
        return '[%s]' % (', '.join(map(toPythonTree,self.value)))

class Stmt(IL):
    pass

class Call(Stmt):
    def __init__(self,f,posArgs,kwArgs):
        assert isinstance(f,Var)
        for arg in posArgs:
            assert isinstance(arg,Simple)
        for (key,value) in kwArgs:
            assert isinstance(key,Var)
            assert isinstance(value,Simple)

        self.f=f
        self.posArgs=list(posArgs)
        self.kwArgs=list(map(tuple,kwArgs))

    def __str__(self):
        def kwArgToStr(arg):
            (key,value)=arg
            return '%s=%s' % (str(key),value.toPythonTree())

        return '%s(%s)' % (str(self.f),
                           ','.join(list(map(str,self.posArgs))
                                    +list(map(kwArgToStr,self.kwArgs))
                                    )
                           )

class Assign(Stmt):
    def __init__(self,lhs,rhs):
        assert isinstance(lhs,Var)
        assert (isinstance(rhs,Simple)
                or isinstance(rhs,Call)
                or isinstance(rhs,Binop)
                or isinstance(rhs,Dot)
                or isinstance(rhs,Quote)
                )
        self.lhs=lhs
        self.rhs=rhs

    def __str__(self):
        return '%s=%s' % (str(self.lhs),str(self.rhs))

class Return(Stmt):
    def __init__(self,value):
        assert isinstance(value,Simple)
        self.value=value

    def __str__(self):
        return 'return %s' % str(self.value)

class Yield(Stmt):
    def __init__(self,value):
        assert isinstance(value,Simple)
        self.value=value

    def __str__(self):
        return 'yield %s' % str(self.value)

class Try(Stmt):
    def __init__(self,body,klassClauses,finallyBody):
        assert isinstance(body,Stmt)
        for (exnKlass,exnVar,exnBody) in klassClauses:
            assert isinstance(exnKlass,Var)
            assert isinstance(exnVar,Var)
            assert isinstance(exnBody,Stmt)
        if finallyBody:
            assert isinstance(finallyBody,Stmt)
        self.body=body
        self.klassClauses=list(map(tuple,klassClauses))
        self.finallyBody=finallyBody

    def __str__(self):
        res='{try %s' % str(self.body)
        for (exnKlass,exnVar,exnBody) in self.klassClauses:
            res+=' {except %s as %s: %s}' % (str(exnKlass),
                                             str(exnVar),
                                             str(exnBody))
        if self.finallyBody:
            res+=' {finally: %s}' % str(self.finallyBody)

        res+='}'
        return res

    def toPythonTree(self):
        res=['try:',
             list(map(toPythonTree,self.body))]
        sawFinally=False
        for (klass,var,clause) in self.exns:
            res.append('except %s as %s:' % (klass,var.toPython()))
            res.append([clause.toPythonTree(),])
        if self.finallyBody:
            res.append('finally:')
            res.append([finallyBody.toPythonTree(),])
        return tuple(res)

class Raise(Stmt):
    def __init__(self,value):
        assert isinstance(value,Var)
        self.value=value

    def __str__(self):
        return 'raise %s' % str(self.value)

class Reraise(Stmt):
    def __str__(self):
        return 'raise'

class Binop(IL):
    def __init__(self,op,left,right):
        assert isinstance(op,Var)
        assert isinstance(left,Simple)
        assert isinstance(right,Simple)

        self.op=op
        self.left=left
        self.right=right

    def __str__(self):
        return '%s%s%s' % (str(self.left),
                           str(self.op),
                           str(self.right))

class Quote(Stmt):
    def __init__(self,value):
        assert isinstance(value,Any)
        self.value=value

    def __str__(self):
        return str(self.value)

    def toPythonTree(self):
        return self.value.toPythonTree()

class If(Stmt):
    def __init__(self,cond,thenBody,elseBody):
        assert isinstance(cond,Simple)
        assert isinstance(thenBody,Stmt)
        assert (elseBody is None) or isinstance(elseBody,Stmt)
        self.cond=cond
        self.thenBody=thenBody
        self.elseBody=elseBody

    def __str__(self):
        res='{if %s then %s' % (str(self.cond),str(self.thenBody))
        if self.elseBody:
            res+=' else %s' % self.elseBody
        res+='}'
        return res

    def toPythonTree(self):
        res=['if %s:' % self.cond.toPythonTree(),
             maybeList(self.thenBody.toPythonTree())]
        if self.elseBody:
            res.append('else:')
            res.append(maybeList(self.thenBody.toPythonTree()))
        return res

class While(Stmt):
    def __init__(self,cond,body):
        assert isinstance(cond,Simple)
        assert isinstance(body,Stmt)
        self.cond=cond
        self.body=body

    def __str__(self):
        return '{while %s %s}' % (str(self.cond),str(self.body))

    def toPythonTree(self):
        return [S('while %s:' % self.cond.toPythonTree()),
                maybeList(self.body.toPythonTree())]

class Def(Stmt):
    def __init__(self,f,posArgs,kwArgs,globals,nonlocals,body):
        assert isinstance(f,Var)
        for varList in [posArgs,kwArgs,globals,nonlocals]:
            for arg in varList:
                assert isinstance(arg,Var)
        assert isinstance(body,Stmt)

        self.f=f
        self.body=body
        self.posArgs=list(posArgs)
        self.kwArgs=list(kwArgs)
        self.globals=list(globals)
        self.nonlocals=list(nonlocals)

    def __str__(self):
        if self.globals:
            globalDecl=' {globals %s}' % (','.join(map(str,self.globals)))
        else:
            globalDecl=''

        if self.nonlocals:
            nonlocalDecl=' {nonlocals %s}' % (','.join(map(str,self.nonlocals)))
        else:
            nonlocalDecl=''

        return '{def %s(%s)%s%s %s}' % (str(self.f),
                                        ','.join(map(str,
                                                     (self.posArgs
                                                      +(['*'] if self.kwArgs
                                                        else [])
                                                      +self.kwArgs
                                                      ))),
                                        globalDecl,nonlocalDecl,
                                        str(self.body))

    def toPythonTree(self):
        defLine='def %s(%s%s%s):' % (str(self.f),
                                     ','.join(map(str,self.posArgs)),
                                     (',*,' if (self.posArgs and self.kwArgs)
                                      else ''),
                                     ','.join(map(str,self.kwArgs))
                                     )
        return [defLine,
                maybeList(self.body.toPythonTree())
                ]

class Break(Stmt):
    def __str__(self):
        return 'break'

class Continue(Stmt):
    def __str__(self):
        return 'continue'

class Pass(Stmt):
    def __str__(self):
        return 'pass'

class Begin(Stmt):
    def __init__(self,stmts):
        for stmt in stmts:
            assert isinstance(stmt,Stmt)
        self.stmts=stmts

    def __str__(self):
        return '{%s}' % '; '.join(map(str,self.stmts))

    def toPythonTree(self):
        return tuple(map(toPythonTree,self.stmts))

class Import(Stmt):
    def __init__(self,module):
        assert isinstance(module,Var)
        self.module=module

    def __str__(self):
        return 'import %s' % str(self.module)

def build(reg):
    if isinstance(reg,S):
        return Var(reg)
    for t in [int,str,float,bool]:
        if isinstance(reg,t):
            return Literal(t)
    assert isinstance(reg,list)
    assert reg
    f=reg[0]
    if f==S(':='):
        assert len(reg)==3
        return Assign(build(reg[1]),build(reg[2]))
    if f==S('return'):
        assert len(reg)==2
        return Return(build(reg[1]))
    if f==S('yield'):
        assert len(reg)==2
        return Yield(build(reg[1]))
    if f==S('try'):
        klassClauses=[]
        finallyClause=None
        assert len(reg)>=2
        sawFinally=False
        for clause in reg[2:]:
            assert not sawFinally
            assert len(clause) in [2,3]
            if len(clause)==2:
                assert clause[0]==S(':finally')
                sawFinally=True
                finallyBody=build(clause[1])
            else:
                assert isinstance(clause[0],S)
                assert isinstance(clause[1],S)
                assert str(clause[0])[0]==':'
                klassClauses.push((Var(S(str(clause[0])[1:])),
                                   Var(clause[1]),
                                   build(clause[2])))
        return Try(build(reg[1]),klassClauses,finallyBody)
    if f==S('raise'):
        assert len(reg)==2
        return Raise(build(reg[1]))
    if f==S('reraise'):
        assert len(reg)==1
        return Reraise()
    if f==S('binop'):
        assert len(reg)==4
        return Binop(build(reg[1]),
                     build(reg[2]),
                     build(reg[3]))
    if f==S('quote'):
        assert len(reg)==2
        return Quote(build(reg[1]))
    if f==S('if'):
        assert len(reg) in [3,4]
        cond=build(reg[1])
        thenClause=build(reg[2])
        elseClause=build(reg[3]) if len(reg)==4 else None
        return If(cond,thenClause,elseClause)
    if f==S('while'):
        assert len(reg)==3
        cond=build(reg[1])
        body=build(reg[2])
        return While(cond,body)
    if f==S('def'):
        assert len(reg)==4
        name=build(reg[1])
        argList=list(map(build,reg[2]))
        body=build(reg[3])
        return Def(name,argList,body)
    if f==S('break'):
        assert len(reg)==1
        return Break()
    if f==S('continue'):
        assert len(reg)==1
        return Continue()
    if f==S('pass'):
        assert len(reg)==1
        return Pass()
    if f==S('begin'):
        return Begin(list(map(build,reg[1:])))
    if f==S('import'):
        assert len(reg)==2
        return Import(build(reg[1]))
    if f==S('import'):
        assert len(reg)==2
        return Import(build(reg[1]))
    if f==S('.'):
        assert len(reg)>2
        return Dot(build(reg[1]),
                   list(map(build,reg[2:])))
    
    def buildPair(varAndVal):
        (var,val)=varAndVal
        return (build(var),build(val))

    return Call(build(reg[0]),
                list(map(build,reg[1])),
                list(map(buildPair,reg[2]))
                )

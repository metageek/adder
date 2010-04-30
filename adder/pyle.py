# And intermediate form for use in compiling Gomer to Pyle.  Inspired
#  by 3-address form.  The main characteristic is that there are no
#  function arguments which include function calls.  See
#  doc/compiler.html for the syntax.

from adder.common import Symbol as S

indentStep=4

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
        return self.varSym.toPython()

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
                or isinstance(rhs,Subscript)
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
             [self.body.toPythonTree()]]
        sawFinally=False
        for (klass,var,clause) in self.klassClauses:
            res.append('except %s as %s:' % (klass,var.toPythonTree()))
            res.append([clause.toPythonTree()])
        if self.finallyBody:
            res.append('finally:')
            res.append([self.finallyBody.toPythonTree()])
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
                           str(self.op.varSym),
                           str(self.right))

class Dot(IL):
    def __init__(self,obj,members):
        assert isinstance(obj,Simple)
        assert isinstance(members,list)
        for m in members:
            assert isinstance(m,Var)

        self.obj=obj
        self.members=members

    def __str__(self):
        return '.'.join(map(str,[self.obj]+self.members))

class Subscript(IL):
    def __init__(self,obj,key):
        assert isinstance(obj,Simple)
        assert isinstance(key,Simple)

        self.obj=obj
        self.key=key

    def __str__(self):
        return '%s[%s]' % (str(self.obj),str(self.key))

class Slice(IL):
    def __init__(self,obj,left,right):
        assert isinstance(obj,Simple)
        assert left is None or isinstance(left,Simple)
        assert right is None or isinstance(right,Simple)

        self.obj=obj
        self.left=left
        self.right=right

    def __str__(self):
        return '%s[%s:%s]' % (str(self.obj),
                              str(self.left),
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
             [self.thenBody.toPythonTree()]
             ]
        if self.elseBody:
            res.append('else:')
            res.append([self.elseBody.toPythonTree()])
        return tuple(res)

class While(Stmt):
    def __init__(self,cond,body):
        assert isinstance(cond,Simple)
        assert isinstance(body,Stmt)
        self.cond=cond
        self.body=body

    def __str__(self):
        return '{while %s %s}' % (str(self.cond),str(self.body))

    def toPythonTree(self):
        return ('while %s:' % self.cond.toPythonTree(),
                [self.body.toPythonTree()])

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
        body=[]
        
        if self.globals:
            body.append('global %s' % (','.join(map(str,self.globals))))
        if self.nonlocals:
            body.append('nonlocal %s' % (','.join(map(str,self.nonlocals))))
        body.append(self.body.toPythonTree())
                        
        return ('def %s(%s%s%s):' % (str(self.f),
                                     ','.join(map(str,self.posArgs)),
                                     (',*,' if (self.posArgs and self.kwArgs)
                                      else ('*,' if self.kwArgs else '')
                                      ),
                                     ','.join(map(str,self.kwArgs))
                                     ),
                body)

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
        t=tuple(map(toPythonTree,self.stmts))
        if t:
            if len(t)>1:
                return t
            return t[0]
        else:
            return "pass"

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
            return Literal(reg)
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
        finallyBody=None
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
                klassClauses.append((Var(S(str(clause[0])[1:])),
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
        def q(r):
            if isinstance(r,list):
                return List(list(map(q,r)))
            else:
                return Literal(r)
        return Quote(q(reg[1]))
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
        body=build(reg[3])

        posArgs=[]
        kwArgs=[]
        globals=[]
        nonlocals=[]

        states={'&key': kwArgs,
                '&global': globals,
                '&nonlocal': nonlocals}
        cur=posArgs
        for arg in reg[2]:
            assert isinstance(arg,S)
            if arg[0]=='&':
                cur=states[str(arg)]
            else:
                cur.append(build(arg))

        return Def(name,posArgs,kwArgs,globals,nonlocals,body)
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
    if f==S('[]'):
        assert len(reg)==3
        return Subscript(build(reg[1]),build(reg[2]))

    if f==S('slice'):
        assert len(reg)==4
        return Slice(build(reg[1]),build(reg[2]),build(reg[3]))

    if f==S('call'):
        def buildPair(varAndVal):
            (var,val)=varAndVal
            return (build(var),build(val))

        assert len(reg)==4
        return Call(build(reg[1]),
                    list(map(build,reg[2])),
                    list(map(buildPair,reg[3]))
                    )
    assert False

# And intermediate form for use in compiling Gomer to Pyle.  Inspired
#  by 3-address form.  The main characteristic is that there are no
#  function arguments which include function calls.  See
#  doc/compiler.html for the syntax.

from adder.common import Symbol as S, literable
import re,pdb

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

class LValue:
    pass

class Var(Simple,LValue):
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
                or value is None
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
        if isinstance(posArgs,list):
            for arg in posArgs:
                assert isinstance(arg,Simple)
        else:
            assert isinstance(posArgs,Var)

        if isinstance(kwArgs,list):
            for (key,value) in kwArgs:
                assert isinstance(key,Var)
                assert isinstance(value,Simple)
        else:
            assert isinstance(kwArgs,Var)

        self.f=f
        self.posArgs=posArgs
        if isinstance(kwArgs,list):
            self.kwArgs=list(map(tuple,kwArgs))
        else:
            self.kwArgs=kwArgs

    def __str__(self):
        def kwArgToStr(arg):
            (key,value)=arg
            return '%s=%s' % (str(key),value.toPythonTree())

        res=str(self.f)+'('
        posArgsNonEmpty=False
        if isinstance(self.posArgs,list):
            res+=','.join(map(str,self.posArgs))
            posArgsNonEmpty=len(self.posArgs)>0
        else:
            res+='*'+str(self.posArgs)
            posArgsNonEmpty=True

        if self.kwArgs:
            if posArgsNonEmpty:
                res+=','
            if isinstance(self.kwArgs,list):
                res+=','.join(map(kwArgToStr,self.kwArgs))
            else:
                res+='**'+str(self.kwArgs)

        res+=')'
        return res

class Assign(Stmt):
    def __init__(self,lhs,rhs):
        assert isinstance(lhs,LValue)
        assert (rhs is None
                or isinstance(rhs,Simple)
                or isinstance(rhs,Call)
                or isinstance(rhs,Binop)
                or isinstance(rhs,Dot)
                or isinstance(rhs,Subscript)
                or isinstance(rhs,Slice)
                or isinstance(rhs,Quote)
                or isinstance(rhs,MkList)
                or isinstance(rhs,MkTuple)
                or isinstance(rhs,MkSet)
                or isinstance(rhs,MkDict)
                )
        self.lhs=lhs
        self.rhs=rhs

    def __str__(self):
        return '%s=%s' % (str(self.lhs),str(self.rhs))

    def toPythonTree(self):
        return '%s=%s' % (self.lhs.toPythonTree(),
                          'None' if (self.rhs is None) else self.rhs.toPythonTree() 
                          )

class Return(Stmt):
    def __init__(self,value):
        assert isinstance(value,Simple) or value is None
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
    allLetters=re.compile('^[a-z]+$',re.IGNORECASE)
    def __init__(self,op,left,right):
        assert isinstance(op,Var)
        assert isinstance(left,Simple)
        assert isinstance(right,Simple)

        self.op=op
        self.left=left
        self.right=right
        self.opStr=str(self.op.varSym)
        if Binop.allLetters.match(self.opStr):
            self.opStr=' %s ' % self.opStr

    def __str__(self):
        return '%s%s%s' % (str(self.left),
                           self.opStr,
                           str(self.right))

class Dot(IL,LValue):
    def __init__(self,obj,members):
        assert isinstance(obj,Simple)
        assert isinstance(members,list)
        for m in members:
            assert isinstance(m,Var)

        self.obj=obj
        self.members=members

    def __str__(self):
        return '.'.join(map(str,[self.obj]+self.members))

class Subscript(IL,LValue):
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
        if isinstance(left,Literal) and left.value is None:
            self.left=None
        else:
            self.left=left
        if isinstance(right,Literal) and right.value is None:
            self.right=None
        else:
            self.right=right

    def __str__(self):
        return '%s[%s:%s]' % (str(self.obj),
                              '' if (self.left is None) else str(self.left),
                              '' if (self.right is None) else str(self.right),
                              )

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
    def __init__(self,f,posArgs,kwArgs,restArgs,globals,nonlocals,body):
        assert isinstance(f,Var)
        assert len(restArgs)<=1
        for varList in [posArgs,kwArgs,restArgs,globals,nonlocals]:
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

class MkList(Stmt):
    def __init__(self,items):
        self.items=items

    def __str__(self):
        return '[%s]' % (', '.join(map(str,self.items)))

class MkTuple(Stmt):
    def __init__(self,items):
        self.items=items

    def __str__(self):
        return '(%s)' % (', '.join(map(str,self.items)))

class MkSet(Stmt):
    def __init__(self,items):
        self.items=items

    def __str__(self):
        if self.items:
            return '{%s}' % (', '.join(map(str,self.items)))
        else:
            return 'set()'

class MkDict(Stmt):
    def __init__(self,kvPairs):
        self.kvPairs=kvPairs

    def __str__(self):
        def strPair(p):
            (var,val)=p
            return '%s: %s' % (repr(str(var)),str(val))
        return '{%s}' % (', '.join(map(strPair,self.kvPairs)))

def build(pyle):
    def buildPair(varAndVal):
        (var,val)=varAndVal
        return (build(var),build(val))
    if isinstance(pyle,S):
        return Var(pyle)
    if literable(pyle):
        return Literal(pyle)
    assert isinstance(pyle,list)
    assert pyle
    f=pyle[0]
    if f==S(':='):
        assert len(pyle)==3
        return Assign(build(pyle[1]),build(pyle[2]))
    if f==S('return'):
        assert len(pyle)==2
        return Return(build(pyle[1]))
    if f==S('yield'):
        assert len(pyle)==2
        return Yield(build(pyle[1]))
    if f==S('mk-list'):
        return MkList(list(map(build,pyle[1:])))
    if f==S('mk-tuple'):
        return MkTuple(list(map(build,pyle[1:])))
    if f==S('mk-set'):
        return MkSet(list(map(build,pyle[1:])))
    if f==S('mk-dict'):
        return MkDict(list(map(buildPair,pyle[1:])))
    if f==S('try'):
        klassClauses=[]
        finallyClause=None
        assert len(pyle)>=2
        sawFinally=False
        finallyBody=None
        for clause in pyle[2:]:
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
        return Try(build(pyle[1]),klassClauses,finallyBody)
    if f==S('raise'):
        assert len(pyle)==2
        return Raise(build(pyle[1]))
    if f==S('reraise'):
        assert len(pyle)==1
        return Reraise()
    if f==S('binop'):
        assert len(pyle)==4
        return Binop(build(pyle[1]),
                     build(pyle[2]),
                     build(pyle[3]))
    if f==S('quote'):
        assert len(pyle)==2
        def q(r):
            if isinstance(r,list):
                return List(list(map(q,r)))
            else:
                return Literal(r)
        return Quote(q(pyle[1]))
    if f==S('if'):
        assert len(pyle) in [3,4]
        cond=build(pyle[1])
        thenClause=build(pyle[2])
        elseClause=build(pyle[3]) if len(pyle)==4 else None
        return If(cond,thenClause,elseClause)
    if f==S('while'):
        assert len(pyle)==3
        cond=build(pyle[1])
        body=build(pyle[2])
        return While(cond,body)
    if f==S('def'):
        assert len(pyle)==4
        name=build(pyle[1])
        body=build(pyle[3])

        posArgs=[]
        kwArgs=[]
        restArgs=[]
        globals=[]
        nonlocals=[]

        states={'&key': kwArgs,
                '&rest': restArgs,
                '&global': globals,
                '&nonlocal': nonlocals}
        cur=posArgs
        for arg in pyle[2]:
            assert isinstance(arg,S)
            if arg[0]=='&':
                cur=states[str(arg)]
            else:
                cur.append(build(arg))

        return Def(name,posArgs,kwArgs,restArgs,globals,nonlocals,body)
    if f==S('break'):
        assert len(pyle)==1
        return Break()
    if f==S('continue'):
        assert len(pyle)==1
        return Continue()
    if f==S('pass'):
        assert len(pyle)==1
        return Pass()
    if f==S('begin'):
        return Begin(list(map(build,pyle[1:])))
    if f==S('import'):
        assert len(pyle)==2
        return Import(build(pyle[1]))
    if f==S('import'):
        assert len(pyle)==2
        return Import(build(pyle[1]))
    if f==S('.'):
        assert len(pyle)>2
        return Dot(build(pyle[1]),
                   list(map(build,pyle[2:])))
    if f==S('[]'):
        assert len(pyle)==3
        return Subscript(build(pyle[1]),build(pyle[2]))

    if f==S('slice'):
        assert len(pyle)==4
        return Slice(build(pyle[1]),build(pyle[2]),build(pyle[3]))

    if f==S('call'):
        assert len(pyle)==4

        if isinstance(pyle[2],list):
            posArgs=list(map(build,pyle[2]))
        else:
            posArgs=build(pyle[2])

        if isinstance(pyle[3],list):
            kwArgs=list(map(buildPair,pyle[3]))
        else:
            kwArgs=build(pyle[3])

        return Call(build(pyle[1]),posArgs,kwArgs)

    print(pyle)
    assert False

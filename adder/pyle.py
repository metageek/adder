# Pyle (Python Lisplike Encoding) encodes a subset of Python into
# Lispy data structures.  As an IL, it's loosely based on
# register-based instruction sets.  The main characteristic is that
# there are no function arguments which include function calls, to
# avoid the problems that arose when I was less careful about
# statements which appeared inside expressions.  See doc/compiler.html
# for the syntax.

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
    pdb.set_trace()
    assert False

def findScratchVars(p):
    for (path,stmt) in descendantStmts(p):
        for var in childVars(stmt):
            if var.isScratch:
                yield (var,path)

def pathCompare(path1,path2):
    N1=len(path1)
    N2=len(path2)
    i=0
    while i<N1 and i<N2:
        if path1[0]<path2[0]:
            return -1
        if path1[0]>path2[0]:
            return 1
        i+=1
    if i==N1:
        if i==N2:
            return 0
        else:
            return -1
    else:
        return 1

def childStmts(pyleStmt):
    assert isinstance(pyleStmt,list) and pyleStmt
    if pyleStmt[0] is S('if'):
        yield ([2],pyleStmt[2])
        if len(pyleStmt)>3:
            yield ([3],pyleStmt[3])
        return

    if pyleStmt[0] is S('try'):
        yield ([1],pyleStmt[1])
        for (i,clause) in enumerate(pyleStmt[2:]):
            if clause[0] is S(':finally'):
                yield ([2+i,1],clause[1])
            else:
                yield ([2+i,2],clause[2])
        return

    if pyleStmt[0] is S('while'):
        yield ([2],pyleStmt[2])
        return

    if pyleStmt[0] is S('def'):
        yield ([3],pyleStmt[3])
        return

    if pyleStmt[0] is S('begin'):
        for (i,stmt) in enumerate(pyleStmt[1:]):
            yield ([1+i],stmt)
        return

def childVars(pyleStmt):
    if isinstance(pyleStmt,S):
        if pyleStmt.isKeyword():
            return []
        return [pyleStmt]

    if not (isinstance(pyleStmt,list) and pyleStmt):
        return []

    def extraCandidates():
        if pyleStmt[0] is S('try'):
            for clause in pyleStmt[2:]:
                yield clause[1]
                if clause[0] is not S(':finally'):
                    yield clause[2]
            return

        if pyleStmt[0] is S('def'):
            for arg in pyleStmt[2]:
                yield arg
            yield pyleStmt[3]
            return

        if pyleStmt[0] is S(':='):
            for xhs in pyleStmt[1:]:
                if isinstance(xhs,list):
                    for var in childVars(xhs):
                        yield var

        if pyleStmt[0] is S('mk-dict'):
            for pair in pyleStmt[1:]:
                assert isinstance(pair,list)
                for var in childVars(pair[1]):
                    yield var

        if pyleStmt[0] is S('call'):
            if isinstance(pyleStmt[2],list):
                for posArg in pyleStmt[2]:
                    for var in childVars(posArg):
                        yield var
            else:
                for var in childVars(pyleStmt[2]):
                    yield var
            if isinstance(pyleStmt[3],list):
                for pair in pyleStmt[3]:
                    if not (isinstance(pair,list) and len(pair)>0):
                        pdb.set_trace()
                    for var in childVars(pair[1]):
                        yield var
            else:
                for var in childVars(pyleStmt[3]):
                    yield var

    def candidates():
        if pyleStmt[0] is S('.'):
            yield pyleStmt[1]
            return

        if pyleStmt[0] is S('quote'):
            return

        for p in pyleStmt[1:]:
            yield p
        for p in extraCandidates():
            yield p

    return filter(lambda c: isinstance(c,S) and not c.isKeyword(),
                  candidates())

def descendantStmts(pyleStmt,*,path=None):
    assert isinstance(pyleStmt,list)
    if path is None:
        path=[]
    yield (path,pyleStmt)
    for (pathSteps,child) in childStmts(pyleStmt):
        for desc in descendantStmts(child,path=path+pathSteps):
            yield desc

def descendantVars(pyleStmt):
    for (path,desc) in descendantStmts(pyleStmt):
        for var in childVars(desc):
            yield var

BEFORE=-1
AFTER=1

def trimmer(scratch):
    return [S(':='),scratch,None]

def trimBeforeOrAfter(pyleStmt,scratch,before):
    assert pyleStmt and isinstance(pyleStmt,list)
    if pyleStmt[0] in trimBeforeOrAfter.scopeExiters:
        return pyleStmt

    if before:
        return [S('begin'),trimmer(scratch),pyleStmt]
    else:
        return [S('begin'),pyleStmt,trimmer(scratch)]

trimBeforeOrAfter.scopeExiters={S('return'),S('raise'),S('reraise')}

def trimBefore(pyleStmt,scratch):
    return trimBeforeOrAfter(pyleStmt,scratch,True)

def trimAfter(pyleStmt,scratch):
    return trimBeforeOrAfter(pyleStmt,scratch,False)

def trim1Scratch(pyleStmt,scratch):
    assert pyleStmt and isinstance(pyleStmt,list)

    if pyleStmt[0] is S('try'):
        mustTrimAfter=False
        allBefore=True
        allAfter=True
        bodyT=trim1Scratch(pyleStmt[1],scratch)
        if bodyT==BEFORE:
            allAfter=False
            newBody=pyleStmt[1]
        else:
            allBefore=False
            if bodyT==AFTER:
                newBody=pyleStmt[1]
                mustTrimAfter=True
            else:
                allAfter=False
                newBody=bodyT

        newClauses=[]
        for clause in pyleStmt[2:]:
            if clause[0] is S(':finally'):
                clauseBody=clause[1]
            else:
                clauseBody=clause[2]
            clauseT=trim1Scratch(clauseBody,scratch)
            if clauseT==BEFORE:
                allAfter=False
                newClause=clause
            else:
                allBefore=False
                if clauseT==AFTER:
                    mustTrimAfter=True
                    newClause=clause
                else:
                    allAfter=False
                    if clause[0] is S(':finally'):
                        newClause=[clause[0],clauseT]
                    else:
                        newClause=[clause[0],clause[1],clauseT]
            newClauses.append(newClause)
        if allBefore:
            return BEFORE
        if allAfter:
            return AFTER
        newTry=[S('try'),newBody]+newClauses
        if mustTrimAfter:
            return trimAfter(newTry,scratch)
        else:
            return newTry

    if pyleStmt[0] is S('if'):
        condMatch=(pyleStmt[1] is scratch)
        thenT=trim1Scratch(pyleStmt[2],scratch)
        elseT=trim1Scratch(pyleStmt[3],scratch) if len(pyleStmt)>3 else BEFORE
        if thenT==BEFORE:
            if elseT==BEFORE:
                if condMatch:
                    return AFTER
                else:
                    return BEFORE
            if elseT==AFTER:
                return [S('if'),
                        pyleStmt[1],
                        trimBefore(pyleStmt[2],scratch),
                        trimAfter(pyleStmt[3],scratch)]
            return [S('if'),
                    pyleStmt[1],
                    trimBefore(pyleStmt[2],scratch),
                    elseT]
        if thenT==AFTER:
            if elseT==BEFORE:
                if len(pyleStmt)>3:
                    return [S('if'),
                            pyleStmt[1],
                            trimAfter(pyleStmt[2],scratch),
                            trimBefore(pyleStmt[3],scratch)]
                else:
                    return [S('if'),
                            pyleStmt[1],
                            trimAfter(pyleStmt[2],scratch)]
            if elseT==AFTER:
                return AFTER
            return [S('if'),
                    pyleStmt[1],
                    trimAfter(pyleStmt[2],scratch),
                    elseT]
        if elseT==BEFORE:
            return [S('if'),
                    pyleStmt[1],
                    thenT,
                    trimBefore(pyleStmt[3],scratch)]
        if elseT==AFTER:
            return [S('if'),
                    pyleStmt[1],
                    thenT,
                    trimAfter(pyleStmt[3],scratch)]
        return [S('if'),
                pyleStmt[1],
                thenT,elseT]

    if pyleStmt[0] is S('while'):
        if pyleStmt[1] is scratch:
            return AFTER
        t=trim1Scratch(pyleStmt[2],scratch)
        if t==AFTER or t==BEFORE:
            return t
        return [S('while'),pyleStmt[1],t]

    if pyleStmt[0] is S('def'):
        # (def) doesn't have to do anything, because scratch vars are
        #   local to function bodies.
        return BEFORE

    if pyleStmt[0] is S('begin'):
        i=len(pyleStmt)-1
        while i>0:
            t=trim1Scratch(pyleStmt[i],scratch)
            if t==AFTER:
                return pyleStmt[:(i+1)]+[trimmer(scratch)]+pyleStmt[i+1:]
            if t==BEFORE:
                i-=1
                continue
            return pyleStmt[:i]+[t]+pyleStmt[i+1:]
        return BEFORE

    if scratch in childVars(pyleStmt):
        return AFTER
    else:
        return BEFORE

def trimScratches(pyleStmt):
    scratches=set()
    for var in descendantVars(pyleStmt):
        if var.isScratch:
            scratches.add(var)
    for scratch in sorted(scratches):
        t=trim1Scratch(pyleStmt,scratch)
        if t==AFTER:
            pyleStmt=trimAfter(pyleStmt,scratch)
        else:
            if t!=BEFORE:
                pyleStmt=t
    return pyleStmt

# And intermediate form for use in compiling Gomer to Pyle.  Inspired
#  by 3-address form.  The main characteristic is that there are no
#  function arguments which include function calls.  See
#  doc/compiler.html for the syntax.

from adder.common import Symbol as S

def toPyle(il):
    return il.toPyle()

class IL:
    pass

class Simple(IL):
    pass

class Var(Simple):
    def __init__(self,varSym):
        assert isinstance(varSym,S)
        self.varSym=varSym

    def __str__(self):
        return str(self.varSym)

    def toPyle(self):
        return self.varSym

class Literal(Simple):
    def __init__(self,value):
        self.value=value

    def __str__(self):
        return repr(self.value)

    def toPyle(self):
        if isinstance(self.value,S) or isinstance(self.value,list):
            return [S('quote'),[self.value]]
        return self.value

class Stmt(IL):
    pass

class Call(Stmt):
    def __init__(self,lhs,f,posArgs,kwArgs):
        assert isinstance(lhs,Var)
        assert isinstance(f,Var)
        for arg in posArgs:
            assert isinstance(arg,Simple)
        for (key,value) in kwArgs:
            assert isinstance(key,Var)
            assert isinstance(value,Simple)

        self.lhs=lhs
        self.f=f
        self.posArgs=list(posArgs)
        self.kwArgs=list(map(tuple,kwArgs))

    def __str__(self):
        def kwArgToStr(arg):
            (key,value)=arg
            return '%s=%s' % (str(key),str(value))

        return '%s=%s(%s)' % (str(self.lhs),
                              str(self.f),
                              ','.join(list(map(str,self.posArgs))
                                       +list(map(kwArgToStr,self.kwArgs))
                                       )
                              )

    def toPyle(self):
        return [S(':='),[self.lhs.toPyle(),
                         [self.f.toPyle(),
                          list(map(toPyle,self.posArgs)),
                          list(map(lambda kx: [str(kx[0]),kx[1].toPyle()],
                                   self.kwArgs))
                          ]
                         ]
                ]

class Assign(Stmt):
    def __init__(self,lhs,rhs):
        assert isinstance(lhs,Var)
        assert isinstance(rhs,Simple)
        self.lhs=lhs
        self.rhs=rhs

    def __str__(self):
        return '%s=%s' % (str(self.lhs),str(self.rhs))

    def toPyle(self):
        return [S(':='),[self.lhs.toPyle(),self.rhs.toPyle()]]

class Return(Stmt):
    def __init__(self,value):
        assert isinstance(value,Simple)
        self.value=value

    def __str__(self):
        return 'return %s' % str(self.value)

    def toPyle(self):
        return [S('return'),[self.value.toPyle()]]

class Yield(Stmt):
    def __init__(self,value):
        assert isinstance(value,Simple)
        self.value=value

    def __str__(self):
        return 'yield %s' % str(self.value)

    def toPyle(self):
        return [S('yield'),[self.value.toPyle()]]

class Raise(Stmt):
    def __init__(self,value):
        assert isinstance(value,Var)
        self.value=value

    def __str__(self):
        return 'raise %s' % str(self.value)

    def toPyle(self):
        return [S('raise'),[self.value.toPyle()]]

class Reraise(Stmt):
    def __str__(self):
        return 'raise'

    def toPyle(self):
        return [S('raise'),[]]

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

    def toPyle(self):
        return [S('try'),
                [self.body.toPyle()],
                (list(map(lambda klassVarBody: [str(klassVarBody[0].varSym),
                                                klassVarBody[1].toPyle(),
                                                klassVarBody[2].toPyle()],
                          self.klassClauses))
                 +([['finally',None,self.finallyBody.toPyle()]]
                   if self.finallyBody else [])
                 )]

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

    def toPyle(self):
        if self.elseBody:
            return [S('if-stmt'),[self.cond.toPyle(),
                                  self.thenBody.toPyle(),
                                  self.elseBody.toPyle()]]
        else:
            return [S('if-stmt'),[self.cond.toPyle(),
                                  self.thenBody.toPyle()]]
                 

class While(Stmt):
    def __init__(self,cond,body):
        assert isinstance(cond,Simple)
        assert isinstance(body,Stmt)
        self.cond=cond
        self.body=body

    def __str__(self):
        return '{while %s %s}' % (str(self.cond),str(self.body))

    def toPyle(self):
        return [S('while'),
                [self.cond.toPyle(),self.body.toPyle()]
                ]

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

    def toPyle(self):
        args=list(map(toPyle,self.posArgs))
        for (marker,vars) in [('&key',self.kwArgs),
                              ('&globals',self.globals),
                              ('&nonlocals',self.nonlocals)]:
            if vars:
                args.append(S(marker))
                args+=list(map(toPyle,vars))
            
        return [S('def'),
                [self.f.toPyle(),args,self.body.toPyle()]
                ]

class Break(Stmt):
    def __str__(self):
        return 'break'

    def toPyle(self):
        return [S('break'),[]]

class Continue(Stmt):
    def __str__(self):
        return 'continue'

    def toPyle(self):
        return [S('continue'),[]]

class Pass(Stmt):
    def __str__(self):
        return 'pass'

    def toPyle(self):
        return [S('begin'),[]]

class Block(Stmt):
    def __init__(self,stmts):
        for stmt in stmts:
            assert isinstance(stmt,Stmt)
        self.stmts=stmts

    def __str__(self):
        return '{%s}' % '; '.join(map(str,self.stmts))

    def toPyle(self):
        return [S('begin'),list(map(toPyle,self.stmts))]

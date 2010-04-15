# Reimplementation of Gomer, using a 3-address intermediate form.
#  Well, it can't really be 3-address, can it? Sometimes you need to
#  call a function with >2 args.  The main characteristic is that
#  there are no function arguments which include function calls.  So:
#
#   list<x> := "" | ( x ("," x)* )
#   simple := var | literal
#   fcall := var "=" var "(" list<simple> ( "," var "=" simple )* ")"
#   assign := var "=" simple
#   return := "return" simple
#   yield := "yield" simple
#   try := "try" stmt ("except" var var stmt)* ("finally" stmt)?
#   raise := "raise" var
#   reraise := "reraise"
#   if := "if" simple "then" stmt ["else" stmt]
#   while := "while" simple stmt
#   def := "def" var "(" list<var> [ ",*" ("," var)+] ")" stmt
#   break := "break"
#   continue := "continue"
#   global := "global" list<var>
#   nonlocal := "nonlocal" list<var>
#   pass := "pass"
#   stmt := fcall | assign | return | yield | try | raise
#         | if | while | def | break | continue
#         | global | nonlocal | pass
#         | list<stmt>

from adder.common import Symbol as S

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

class Literal(Simple):
    def __init__(self,value):
        self.value=value

    def __str__(self):
        return repr(self.value)

class Stmt(IL):
    pass

class Call(Stmt):
    def __init__(self,lhs,f,posArgs,kwArgs):
        assert isinstance(lhs,Var)
        assert isinstance(f,Var)
        for arg in posArgs:
            assert isinstance(arg,Var)
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

class Assign(Stmt):
    def __init__(self,lhs,rhs):
        assert isinstance(lhs,Var)
        assert isinstance(rhs,Simple)
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

class Raise(Stmt):
    def __init__(self,value):
        assert isinstance(value,Var)
        self.value=value

    def __str__(self):
        return 'raise %s' % str(self.value)

class Reraise(Stmt):
    def __str__(self):
        return 'raise'

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
            res+=' %s' % str(self.finallyBody)

        res+='}'
        return res

class If(Stmt):
    def __init__(self,cond,thenBody,elseBody):
        assert isinstance(cond,Simple)
        assert isinstance(thenBody,Stmt)
        assert (elseBody is None) or isinstance(elseBody,Stmt)
        self.cond=cond
        self.thenBody=thenBody
        self.elseBody=elseBody

    def __str__(self):
        res='{if %s then %s' % (str(self.cond),str(self.then))
        if self.elseBody:
            res+=' %s' % self.elseBody
        res+='}'
        return res

class While(Stmt):
    def __init__(self,cond,body):
        assert isinstance(cond,Simple)
        assert isinstance(body,Stmt)
        self.cond=cond
        self.body=body

    def __str__(self):
        return '{while %s %s}' % (str(self.cond),str(self.body))

class Def(Stmt):
    def __init__(self,f,posArgs,kwArgs,body):
        assert isinstance(f,Var)
        for arg in posArgs:
            assert isinstance(arg,Var)
        for arg in kwArgs:
            assert isinstance(arg,Var)
        assert isinstance(body,Stmt)

        self.f=f
        self.body=body
        self.posArgs=list(posArgs)
        self.kwArgs=list(kwArgs)

    def __str__(self):
        res='{def %s(%s) %s}' % (str(self.f),
                                 ','.join(map(str,
                                              self.posArgs+self.kwArgs)),
                                 str(self.body))

class Break(Stmt):
    def __str__(self):
        return 'break'

class Continue(Stmt):
    def __str__(self):
        return 'break'

class Global(Stmt):
    def __init__(self,vars):
        for var in vars:
            assert isinstance(var,Var)
        self.vars=vars

    def __str__(self):
        return 'global %s' % ','.join(map(str,self.vars))

class Nonlocal(Stmt):
    def __init__(self,vars):
        for var in vars:
            assert isinstance(var,Var)
        self.vars=vars

    def __str__(self):
        return 'nonlocal %s' % ','.join(map(str,self.vars))

class Pass(Stmt):
    def __str__(self):
        return 'pass'

class Block(Stmt):
    def __init__(self,stmts):
        for stmt in stmts:
            assert isinstance(stmt,Stmt)
        self.stmts=stmts

    def __str__(self):
        return '{%s}' % ';'.join(map(str,self.stmts))

from adder.common import Symbol as S
import adder.gomer,adder.runtime

class Macro(adder.gomer.Function):
    def __init__(self,context,transformer):
        self.context=context
        self.transformer=transformer

    def compyleCall(self,f,args,kwArgs,stmtCollector):
        stmts=[]
        expr=self.transformer(self.context,
                              f,args,kwArgs,
                              stmts.append)
        for stmt in stmts:
            context.eval(stmt)
        return context.compyle(expr,stmtCollector)

class Context:
    def __init__(self,parent):
        self.parent=parent
        self.scope=adder.gomer.Scope(parent.scope if parent else None)
        if parent:
            self.globals=parent.globals
        else:
            self.globals={'adder': adder,
                          'gensym': adder.common.gensym}

    def __getitem__(self,name):
        return self.globals[name]

    def __setitem__(self,name,value):
        self.globals[name]=value

    def __contains__(self,name):
        return name in self.globals

    def addDef(self,name,value):
        self.scope.addDef(S(name),
                          (None if (value is None)
                           else adder.gomer.Constant(self.scope,value)
                           ))
        self.globals[name]=value

    def addFuncDef(self,name,f):
        self.addDef(name,
                    adder.gomer.PyleExpr(self.scope,
                                         name)
                    )
        self.globals[name]=f

    def eval(self,expr):
        return adder.gomer.evalTopLevel(expr,self.scope,self.globals)

    def compyle(self,expr,stmtCollector):
        return adder.gomer.build(self.scope,expr).compyle(stmtCollector)

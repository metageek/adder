import adder.gomer

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
        return context.compile(expr)

class Context:
    def __init__(self,parent):
        self.parent=parent
        self.scope=adder.gomer.Scope(parent.scope if parent else None)
        if parent:
            self.globals=parent.globals
        else:
            self.globals=None

def evalTopLevel(expr,scope,globals):
    gomerAST=adder.gomer.build(scope,expr)
    

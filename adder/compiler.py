import os,pdb

import adder.gomer,adder.runtime
from adder.common import Symbol as S
from adder.parser import parse,parseFile
from adder.gomer import TwoConsecutiveKeywords,VarRef

class Macro(adder.gomer.Function):
    def __init__(self,name,context,transformer):
        self.name=name
        self.context=context
        self.transformer=transformer

    def transform(self,srcExpr):
        posArgs=[]
        kwArgs=[]

        curKeyword=None
        for arg in srcExpr[1:]:
            # Need to operate on symbols, not VarRefs.
            isKeyword=isinstance(arg,S) and arg.startswith(':')

            if curKeyword:
                if isKeyword:
                    varRef=VarRef(self.context.scope,curKeyword)
                    raise TwoConsecutiveKeywords(varRef,arg)
                kwArgs.append([curKeyword[1:],arg])
                curKeyword=None
            else:
                if isKeyword:
                    assert len(arg.name)>1
                    curKeyword=arg
                else:
                    posArgs.append(arg)

        expr=self.transformer(posArgs,kwArgs)
        if False:
            print('Macro %s:' % self.name)
            print('\tbefore:',srcExpr[0],posArgs,kwArgs)
            print('\tafter:',expr)

        return expr

class Context:
    def __init__(self,parent,*,loadPrelude=True):
        self.parent=parent
        self.scope=adder.gomer.Scope(parent.scope if parent else None)
        if parent:
            self.globals=parent.globals
        else:
            self.globals={'adder': adder,
                          'gensym': adder.common.gensym}
        self.addMacroDef('defmacro',self.defmacroTransformer)
        if loadPrelude:
            self.load('prelude.+',inSrcDir=True)

    def defmacroTransformer(self,posArgs,kwArgs):
        assert not kwArgs
        assert len(posArgs)>=2

        transformerExpr=[S('lambda')]+posArgs[1:]
        transformer=self.eval(transformerExpr)
        print(transformerExpr)
        self.addMacroDef(posArgs[0],
                         lambda ps,ks: transformer(*ps,**(dict(ks)))
                         )
        return None

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

    def addMacroDef(self,name,transformer):
        self.scope.addDef(S(name),
                          adder.gomer.Constant(self.scope,
                                               Macro(name,self,transformer)
                                               )
                          )

    def addFuncDef(self,name,f):
        self.addDef(name,
                    adder.gomer.PyleExpr(self.scope,
                                         name)
                    )
        self.globals[name]=f

    def eval(self,expr,*,verbose=False):
        return adder.gomer.evalTopLevel(expr,self.scope,self.globals,
                                        verbose=verbose)

    def evalStrN(self,exprStr):
        return map(lambda expr: self.eval(expr),parse(exprStr))

    # Ignores any expressions in exprStr after the first.
    def evalStr1(self,exprStr):
        return next(self.evalStrN(exprStr))

    def load(self,path,*,inSrcDir=False):
        def stripPositions(expr):
            (expr,pos)=expr
            if isinstance(expr,list):
                return list(map(stripPositions,expr))
            else:
                return expr

        if inSrcDir:
            srcFile=self.__class__.load.__code__.co_filename
            srcDir=os.path.split(srcFile)[0]
            path=os.path.join(srcDir,path)
        last=None
        for expr in parseFile(path):
            last=self.eval(stripPositions(expr))
        return last

    def compyle(self,expr,stmtCollector):
        return adder.gomer.build(self.scope,expr).compyle(stmtCollector)

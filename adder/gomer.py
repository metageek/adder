# A structured internal representation; basically an annotated form of
#  Adder itself, with macros expanded.  Gets converted to Pyle.
#  Includes a basic interpreter, for use in macro expansion.

import itertools,functools,re,pdb,adder.pyle,sys
from adder.common import Symbol as S, gensym, mkScratch
import adder.runtime

def maybeBegin(body):
    if len(body)==1:
        return body[0]
    else:
        return [S('begin')]+body

class Reducer:
    def reduce(self,gomer,isStmt,stmtCollector):
        pass

class ReduceDefault(Reducer):
    def getF(self,gomer,stmtCollector):
        return reduce(gomer[0],False,stmtCollector)

    def reduce(self,gomer,isStmt,stmtCollector):
        f=self.getF(gomer,stmtCollector)
        posArgs=[]
        kwArgs=[]
        keyword=None
        for arg in gomer[1:]:
            if isinstance(arg,S) and arg.isKeyword():
                curKeyword=S(str(arg)[1:])
            else:
                curKeyword=None
                argExpr=reduce(arg,False,stmtCollector)

            if keyword is None:
                if curKeyword:
                    keyword=curKeyword
                else:
                    posArgs.append(argExpr)
            else:
                if curKeyword:
                    raise TwoConsecutiveKeywords(keyword,curKeyword)
                else:
                    kwArgs.append([keyword,argExpr])
                    keyword=None

        return [S('call'),f,posArgs,kwArgs]

class ReduceDont(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        return gomer

class ReduceRenameFunc(ReduceDefault):
    def __init__(self,pyFunc,isPure):
        self.pyFunc=S(pyFunc)
        self.isPure=isPure

    def getF(self,gomer,stmtCollector):
        return self.pyFunc

    def reduce(self,gomer,isStmt,stmtCollector):
        res=ReduceDefault.reduce(self,gomer,isStmt,stmtCollector)
        if not (isStmt and self.isPure):
            return res

class ReduceFuncToSame(Reducer):
    def __init__(self,pyleTag,isPure):
        self.pyleTag=S(pyleTag)
        self.isPure=isPure

    def reduce(self,gomer,isStmt,stmtCollector):
        res=[self.pyleTag]+list(map(lambda s: reduce(s,False,stmtCollector),
                                    gomer[1:]))
        if not (isStmt and self.isPure):
            return res

class ReduceMkDict(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        def groupPairs(i):
            (first,hasFirst)=(None,False)
            for x in i:
                if hasFirst:
                    yield (first,x)
                    (first,hasFirst)=(None,False)
                else:
                    (first,hasFirst)=(x,True)
            assert not hasFirst

        res=[S('mk-dict')]
        for (key,val) in groupPairs(gomer[1:]):
            assert isinstance(key,S) and key.isKeyword()
            res.append([S(str(key)[1:]),reduce(val,False,stmtCollector)])
        if not isStmt:
            return res

class ReduceReverse(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        assert len(gomer)==2
        if isStmt:
            return reduce([[S('.'),gomer[1],S('reverse')]],
                          isStmt,stmtCollector)
        else:
            scratch=mkScratch()
            return reduce([S('begin'),
                           [S(':='),scratch,[S('to-list'),gomer[1]]],
                           [[S('.'),scratch,S('reverse')]],
                           scratch],
                          isStmt,stmtCollector)
        

class ReduceApply(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        assert len(gomer) in [3,4]
        f=reduce(gomer[1],False,stmtCollector)
        if gomer[2]==[S('quote'),[]]:
            posArgs=[]
        else:
            posArgs=reduce(gomer[2],False,stmtCollector)
        if len(gomer)>3:
            kwArgs=reduce(gomer[3],False,stmtCollector)
        else:
            kwArgs=[]

        return [S('call'),f,posArgs,kwArgs]

class ReduceTry(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        def clauseStmt(clauseStmts):
            clauseBody=[]
            expr=reduce([S('begin')]+clauseStmts,
                        isStmt,
                        clauseBody.append)
            return (maybeBegin(clauseBody),expr)

        scratch=mkScratch() if not isStmt else None
        last=None
        gomerBody=[]
        exnClauses=[]
        finallyClause=None
        for g in gomer[1:]:
            assert not finallyClause
            if isinstance(g,list) and isinstance(g[0],S) and g[0].isKeyword():
                if g[0]==S(':finally'):
                    (finallyStmt,_)=clauseStmt(g[1:])
                    finallyClause=[S(':finally'),finallyStmt]
                else:
                    (exnStmt,exnScratch)=clauseStmt(g[2:])
                    if scratch:
                        assignment=[S(':='),scratch,exnScratch]
                        if (isinstance(exnStmt,list)
                            and isinstance(exnStmt[0],S)
                            and exnStmt[0]==S('begin')):
                            exnStmt.append(assignment)
                        else:
                            exnStmt=[S('begin'),exnStmt,assignment]
                    exnClauses.append([g[0],g[1],exnStmt])
            else:
                assert not exnClauses
                gomerBody.append(g)
        pyleBody=[]
        for g in gomerBody[:-1]:
            reduce(g,True,pyleBody.append)
        if gomerBody:
            last=reduce(gomerBody[-1],isStmt,pyleBody.append)
        if scratch:
            pyleBody.append([S(':='),scratch,last])
        res=[S('try'),maybeBegin(pyleBody)]+exnClauses
        if finallyClause:
            res.append(finallyClause)
        stmtCollector(res)
        return scratch

class ReduceIf(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        assert len(gomer) in [3,4]
        condExpr=reduce(gomer[1],False,stmtCollector)
        thenBody=[]
        thenExpr=reduce(gomer[2],isStmt,thenBody.append)
        if isStmt:
            scratch=None
        else:
            scratch=mkScratch('if')
            thenBody.append([S(':='),scratch,thenExpr])
        if len(gomer)==4:
            elseBody=[]
            elseExpr=reduce(gomer[3],isStmt,elseBody.append)
            if not isStmt:
                elseBody.append([S(':='),scratch,elseExpr])
            if not elseBody:
                stmtCollector([S('if'),condExpr,
                               maybeBegin(thenBody)])
            else:
                stmtCollector([S('if'),condExpr,
                               maybeBegin(thenBody),
                               maybeBegin(elseBody)])
        else:
            pyle=[S('if'),condExpr,maybeBegin(thenBody)]
            if not isStmt:
                pyle.append([S(':='),scratch,None])
            stmtCollector(pyle)
        return scratch

class ReduceWhile(Reducer):
    scratchStack=[]

    def reduce(self,gomer,isStmt,stmtCollector):
        assert len(gomer)>=2
        if isStmt:
            scratch=None
        else:
            scratch=mkScratch('while')
            stmtCollector([S(':='),scratch,None])
        ReduceWhile.scratchStack.append(scratch)
        condBody=[]
        condExpr=reduce(gomer[1],False,condBody.append)
        for cb in condBody:
            stmtCollector(cb)
        body=[]
        bodyExpr=None
        for (i,b) in enumerate(gomer[2:]):
            bodyExpr=reduce(b,
                            isStmt or ((i+2)<(len(gomer)-1)),
                            body.append)
        if body and not isStmt:
            body.append([S(':='),scratch,bodyExpr])
        for cb in condBody:
            body.append(cb)
        stmtCollector([S('while'),condExpr,maybeBegin(body)])
        ReduceWhile.scratchStack.pop()
        return scratch

class ReduceDefun(Reducer):
    isGeneratorStack=[]
    def reduce(self,gomer,isStmt,stmtCollector):
        ReduceDefun.isGeneratorStack.append(False)
        name=gomer[1]
        argList=gomer[2]
        body=[]
        bodyGs=gomer[3:]
        if bodyGs:
            for g in bodyGs[:-1]:
                reduce(g,True,body.append)
            resExpr=reduce(bodyGs[-1],False,body.append)
            if not ReduceDefun.isGeneratorStack.pop():
                reduce([S('return'),resExpr],True,body.append)
        if body:
            body=maybeBegin(body)
        else:
            body=[S('pass')]
        stmtCollector([S('def'),name,gomer[2],body])
        if not isStmt:
            return name

class ReduceLambda(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        if isStmt:
            return None
        name=gensym('lambda')
        reduce([S('defun'),name]+gomer[1:],True,stmtCollector)
        return name

class ReduceAssign(Reducer):
    def isSimple(self,rhs):
        if not isinstance(rhs,list):
            return True
        assert rhs
        if rhs[0] in reductionRules:
            return False
        for arg in rhs[1:]:
            if isinstance(arg,list):
                return False
        return True

    def reduce(self,gomer,isStmt,stmtCollector):
        lhs=gomer[1]
        rhs=gomer[2]
        assert (isinstance(lhs,S)
                or (isinstance(lhs,list)
                    and isinstance(lhs[0],S)
                    and (lhs[0]==S('.') or lhs[0]==S('[]'))
                    ))
        rhsExpr=reduce(rhs,False,stmtCollector,inAssignment=True)
        if self.isSimple(rhs):
            stmtCollector([gomer[0],gomer[1],rhsExpr])
        else:
            stmtCollector([S(':='),lhs,rhsExpr])
        if not isStmt:
            return lhs

class ReduceBegin(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        parts=gomer[1:]
        if not parts:
            return None

        for p in parts[:-1]:
            reduce(p,True,stmtCollector)
        lastExpr=reduce(parts[-1],isStmt,stmtCollector)
        if not isStmt:
            return lastExpr

class ReduceImport(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        last=None
        for module in gomer[1:]:
            assert isinstance(module,S)
            stmtCollector([S('import'),module])
            last=module
        if not isStmt:
            return last

class ReduceBreakOrContinue(Reducer):
    def __init__(self,name):
        self.name=S(name)

    def reduce(self,gomer,isStmt,stmtCollector):
        assert isStmt
        assert len(gomer)==1
        scratch=ReduceWhile.scratchStack[-1]
        if scratch:
            stmtCollector([S(':='),scratch,None])
        stmtCollector([self.name])

class ReduceQuote(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        if isStmt:
            return
        assert len(gomer)==2
        if gomer[1] is None:
            return gomer[1]
        for t in [bool,int,float,str]:
            if isinstance(gomer[1],t):
                return gomer[1]
        return gomer

class ReduceReturn(Reducer):
    # Always make (return) a statment.  If you use it as an expr,
    #  it'll get put into the statement stream in the correct
    #  order.  Of course, it *can't* have a value, since it skips
    #  past the value, so it doesn't matter what we return as the
    #  expr code.  So we don't, and let the caller get None.
    def reduce(self,gomer,isStmt,stmtCollector):
        assert len(gomer)==2
        stmtCollector([S('return'),reduce(gomer[1],False,stmtCollector)])

class ReduceYield(Reducer):
    # Python yield has to be a statement; Adder (yield) does not.  If
    #  you use it as an expr, it'll get put into the statement stream
    #  in the correct order, and the value yielded will be used as
    #  the value of the expr.
    def reduce(self,gomer,isStmt,stmtCollector):
        assert len(gomer)==2

        # This guard is in place to permit the unit tests to test
        # (yield) code generation independently.  When using (yield)
        # correctly, the guard should never be needed.
        if ReduceDefun.isGeneratorStack:
            ReduceDefun.isGeneratorStack[-1]=True

        expr=reduce(gomer[1],False,stmtCollector)
        stmtCollector([S('yield'),expr])
        if not isStmt:
            return expr

class ReduceAnd(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        if len(gomer)==1:
            if isStmt:
                return
            else:
                return True
        if len(gomer)==2:
            return reduce(gomer[1],isStmt,stmtCollector)
        cond=reduce(gomer[1],False,stmtCollector)
        return reduce([S('if'),
                       cond,
                       [S('and')]+gomer[2:],
                       cond
                       ],
                      isStmt,stmtCollector)

class ReduceOr(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        if len(gomer)==1:
            if isStmt:
                return
            else:
                return False
        if len(gomer)==2:
            return reduce(gomer[1],isStmt,stmtCollector)
        cond=reduce(gomer[1],False,stmtCollector)
        return reduce([S('if'),
                       cond,
                       cond,
                       [S('or')]+gomer[2:]
                       ],
                      isStmt,stmtCollector)

class ReduceDot(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        assert len(gomer)>1
        if len(gomer)==2:
            return reduce(gomer[1],isStmt,stmtCollector)
        obj=reduce(gomer[1],False,stmtCollector)
        if isStmt:
            # x.y as a statement is a nop,
            # But f().y as a statement is equiv to f().
            return

        res=[S('.'),obj]
        for name in gomer[2:]:
            assert isinstance(name,S)
            res.append(name)
        return res

class ReduceRaise(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        assert len(gomer) in [1,2]
        if len(gomer)==1:
            stmtCollector([S('reraise')])
        else:
            stmtCollector([S('raise'),reduce(gomer[1],False,stmtCollector)])

class ReducePrint(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        expr=None
        stmt=[S('call'),S('print')]
        args=[]
        for arg in gomer[1:]:
            expr=reduce(arg,False,stmtCollector)
            args.append(expr)
        stmt.append(args)
        stmt.append([])
        stmtCollector(stmt)
        if not isStmt:
            return expr

class ReduceAdditiveBinop(Reducer):
    def __init__(self,op,identity):
        self.op=op
        self.identity=identity

    def reduce(self,gomer,isStmt,stmtCollector):
        def expr():
            if len(gomer)==1:
                return self.identity
            op1=reduce(gomer[1],False,stmtCollector)
            if len(gomer)==2:
                return op1
            return [S('binop'),self.op,op1,
                    reduce([self.op]+gomer[2:],False,stmtCollector)
                    ]
        e=expr()
        if not isStmt:
            return e

class ReduceSubtractiveBinop(Reducer):
    def __init__(self,op,identity,unop):
        self.op=op
        self.identity=identity
        self.unop=unop

    def reduce(self,gomer,isStmt,stmtCollector):
        def expr():
            if len(gomer)==1:
                return self.identity
            if len(gomer)==2 and isinstance(gomer[1],int) and self.unop:
                    return self.unop(gomer[1])
            op1=reduce(gomer[1],False,stmtCollector)
            if len(gomer)==2:
                return [S('binop'),self.op,self.identity,op1]
            op2=reduce(gomer[2],False,stmtCollector)
            if len(gomer)==3:
                return [S('binop'),self.op,op1,op2]
            scratch=mkScratch()
            stmtCollector([S(':='),scratch,[S('binop'),self.op,op1,op2]])
            return reduce([S('binop'),self.op,
                           scratch
                           ]+gomer[3:],
                           isStmt,stmtCollector)
        e=expr()
        if not isStmt:
            return e

class ReduceComparisonBinop(Reducer):
    def __init__(self,op):
        self.op=op

    def reduce(self,gomer,isStmt,stmtCollector):
        def expr():
            if len(gomer)<=2:
                return True
            op1=reduce(gomer[1],False,stmtCollector)
            op2=reduce(gomer[2],False,stmtCollector)
            cmp12=[S('binop'),self.op,op1,op2]
            if len(gomer)==3:
                return cmp12
            else:
                return reduce([S('and'),
                               cmp12,
                               [self.op,op2]+gomer[3:]
                               ],
                              False,stmtCollector
                              )
        e=expr()
        if not isStmt:
            return e

class ReduceSimpleBinop(Reducer):
    def __init__(self,op):
        self.op=op

    def reduce(self,gomer,isStmt,stmtCollector):
        assert len(gomer)==3
        op1=reduce(gomer[1],False,stmtCollector)
        op2=reduce(gomer[2],False,stmtCollector)
        if not isStmt:
            return [S('binop'),self.op,op1,op2]

class ReduceSubscript(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        assert len(gomer)==3
        obj=reduce(gomer[1],False,stmtCollector)
        index=reduce(gomer[2],False,stmtCollector)
        if not isStmt:
            return [S('[]'),obj,index]

class ReduceSlice(Reducer):
    def reduce(self,gomer,isStmt,stmtCollector):
        assert len(gomer) in [3,4]
        obj=reduce(gomer[1],False,stmtCollector)
        left=reduce(gomer[2],False,stmtCollector)
        right=reduce(gomer[3],False,stmtCollector) if len(gomer)==4 else None
        if not isStmt:
            return [S('slice'),obj,left,right]

reductionRules={S('if') : ReduceIf(),
                S('while') : ReduceWhile(),
                S('defun') : ReduceDefun(),
                S('lambda') : ReduceLambda(),
                S(':=') : ReduceAssign(),
                S('begin') : ReduceBegin(),
                S('import') : ReduceImport(),
                S('break') : ReduceBreakOrContinue('break'),
                S('continue') : ReduceBreakOrContinue('continue'),
                S('quote') : ReduceQuote(),
                S('return') : ReduceReturn(),
                S('yield') : ReduceYield(),
                S('and') : ReduceAnd(),
                S('or') : ReduceOr(),
                S('.') : ReduceDot(),
                S('raise') : ReduceRaise(),
                S('print') : ReducePrint(),
                S('+') : ReduceAdditiveBinop(S('+'),0),
                S('*') : ReduceAdditiveBinop(S('*'),1),
                S('-') : ReduceSubtractiveBinop(S('-'),0,lambda x: -x),
                S('/') : ReduceSubtractiveBinop(S('/'),1,lambda x: 1/x),
                S('//') : ReduceSubtractiveBinop(S('//'),1,lambda x: 1//x),
                S('==') : ReduceComparisonBinop(S('==')),
                S('!=') : ReduceComparisonBinop(S('!=')),
                S('<=') : ReduceComparisonBinop(S('<=')),
                S('<') : ReduceComparisonBinop(S('<')),
                S('>=') : ReduceComparisonBinop(S('>=')),
                S('>') : ReduceComparisonBinop(S('>')),
                S('in') : ReduceSimpleBinop(S('in')),
                S('%') : ReduceSimpleBinop(S('%')),
                S('[]') : ReduceSubscript(),
                S('slice') : ReduceSlice(),
                S('binop') : ReduceDont(),
                S('to-list') : ReduceRenameFunc('python.list',True),
                S('to-tuple') : ReduceRenameFunc('python.tuple',True),
                S('to-set') : ReduceRenameFunc('python.set',True),
                S('to-dict') : ReduceRenameFunc('python.dict',True),
                S('isinstance') : ReduceRenameFunc('python.isinstance',
                                                   True),
                S('mk-list') : ReduceFuncToSame('mk-list',True),
                S('mk-tuple') : ReduceFuncToSame('mk-tuple',True),
                S('mk-set') : ReduceFuncToSame('mk-set',True),
                S('mk-dict') : ReduceMkDict(),
                S('mk-symbol') : ReduceRenameFunc('adder.common.Symbol',
                                                  True),
                S('reverse') : ReduceReverse(),
                S('apply') : ReduceApply(),
                S('try') : ReduceTry(),
                }
reduceDefault=ReduceDefault()

def getReducer(f):
    if isinstance(f,S) and f in reductionRules:
        return reductionRules[f]
    else:
        return reduceDefault

def reduce(gomer,isStmt,stmtCollector,*,inAssignment=False):
    if isinstance(gomer,list):
        assert gomer
        reducer=getReducer(gomer[0])
        gomer=reducer.reduce(gomer,isStmt,stmtCollector)
    if isStmt:
        if isinstance(gomer,list):
            stmtCollector(gomer)
    else:
        if ((not inAssignment)
            and isinstance(gomer,list)
            and gomer[0]!=S(':=')
            ):
            scratch=mkScratch()
            stmtCollector([S(':='),scratch,gomer])
            gomer=scratch
        return gomer

def mkGlobals():
    g=dict(adder.runtime.__dict__)
    class O:
        pass
    python=O()
    for (k,v) in __builtins__.items():
        setattr(python,k,v)
    g['python']=python
    a=O()
    a.common=adder.common
    g['adder']=a
    g['none']=None
    return g

def geval(gomer,*,globalDict=None,localDict=None,verbose=False):
    if globalDict is None:
        globalDict=mkGlobals()
    if localDict is None:
        localDict=globalDict
    pyleBody=[]
    pyleExpr=reduce(gomer,False,pyleBody.append)
    stmtTrees=[]
    if verbose:
        print(pyleBody)
        print(pyleExpr)
    for pyleStmt in pyleBody:
        il=adder.pyle.build(pyleStmt)
        stmtTree=il.toPythonTree()
        stmtTrees.append(stmtTree)
    stmtFlat=adder.pyle.flatten(tuple(stmtTrees))
    il=adder.pyle.build(pyleExpr)
    if il is None:
        exprFlat=''
    else:
        exprTree=il.toPythonTree()
        exprFlat=adder.pyle.flatten(exprTree)
    if verbose:
        print(stmtFlat)
        print(exprFlat)
    try:
        exec(stmtFlat,globalDict,localDict)
    except TypeError as te:
        print(gomer)
        print(stmtFlat)
        pdb.set_trace()
        raise
    res=eval(exprFlat,globalDict,localDict)
    if verbose:
        pdb.set_trace()
    return res

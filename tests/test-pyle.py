#!/usr/bin/env python3

import unittest,pdb,sys,os
from adder.pyle import *
from adder.common import Symbol as S

def deepToPython(x):
    if isinstance(x,S):
        return x.toPython()
    if isinstance(x,list):
        return list(map(lambda elt: deepToPython(elt),x))
    return x

class ExprTestCase(unittest.TestCase):
    def testInt(self):
        expr=Constant(17)
        assert expr.toPython(False)=='17'
        assert expr.toPython(True)=='17'

    def testVar(self):
        expr=VarExpr('barney')
        assert expr.toPython(False)=='barney'
        assert expr.toPython(True)=='barney'

    def testVarEscaped(self):
        expr=VarExpr('barney-rubble')
        assert expr.toPython(False)==S('barney-rubble').toPython()
        assert expr.toPython(True)==S('barney-rubble').toPython()

    def testVarEscapedParts(self):
        expr=VarExpr('barney-rubble.bedrock')
        assert expr.toPython(False)==(S('barney-rubble').toPython()
                                      +'.bedrock')
        assert expr.toPython(True)==(S('barney-rubble').toPython()
                                     +'.bedrock')

    def testStr(self):
        expr=Constant('fred')
        assert expr.toPython(False)=="'fred'"
        assert expr.toPython(True)=="'fred'"

    def testPlusExpr(self):
        expr=BinaryOperator('*',Constant(9),Constant(7))
        assert expr.toPython(False)=="9*7"
        assert expr.toPython(True)=="(9*7)"

    def testNestedExpr(self):
        expr=BinaryOperator('*',
                            Constant(9),
                            BinaryOperator('+',
                                           Constant(3),
                                           VarExpr('z')))
        assert expr.toPython(False)=="9*(3+z)"
        assert expr.toPython(True)=="(9*(3+z))"

    def testUnaryMinus(self):
        expr=UnaryOperator('-',Constant(9))
        assert expr.toPython(False)=="-9"
        assert expr.toPython(True)=="(-9)"

    def testUnaryNot(self):
        expr=UnaryOperator('not',Constant(False))
        assert expr.toPython(False)=="not False"
        assert expr.toPython(True)=="(not False)"

    def testCallExprNoArgs(self):
        expr=CallExpr(VarExpr('f'),[])
        assert expr.toPython(False)=="f()"
        assert expr.toPython(True)=="f()"

    def testCallExprOnlyPosArgs(self):
        expr=CallExpr(VarExpr('f'),[Constant(9),Constant(7)])
        assert expr.toPython(False)=="f(9, 7)"
        assert expr.toPython(True)=="f(9, 7)"

    def testCallExprOnlyKWArgs(self):
        expr=CallExpr(VarExpr('f'),[],{'a': Constant(9), 'b': Constant(7)})
        assert expr.toPython(False)=="f(a=9, b=7)"
        assert expr.toPython(True)=="f(a=9, b=7)"

    def testCallExprPosAndKWArgs(self):
        expr=CallExpr(VarExpr('f'),
                      [VarExpr('x'),Constant(12)],
                      {'a': Constant(9), 'b': Constant(7)})
        assert expr.toPython(False)=="f(x, 12, a=9, b=7)"
        assert expr.toPython(True)=="f(x, 12, a=9, b=7)"

    def testIfOperator(self):
        expr=IfOperator(BinaryOperator('==',VarExpr('x'),Constant(9)),
                        BinaryOperator('*',VarExpr('x'),Constant(7)),
                        BinaryOperator('*',Constant(9),VarExpr('x')))
        assert expr.toPython(False)=="(x*7) if (x==9) else (9*x)"
        assert expr.toPython(True)=="((x*7) if (x==9) else (9*x))"

    def testListConstructor0(self):
        expr=ListConstructor([])
        assert expr.toPython(False)=="[]"
        assert expr.toPython(True)=="[]"

    def testListConstructor1(self):
        expr=ListConstructor([Constant(9)])
        assert expr.toPython(False)=="[9]"
        assert expr.toPython(True)=="[9]"

    def testListConstructor2(self):
        expr=ListConstructor([Constant(9),Constant(7)])
        assert expr.toPython(False)=="[9, 7]"
        assert expr.toPython(True)=="[9, 7]"

    def testTupleConstructor0(self):
        expr=TupleConstructor([])
        assert expr.toPython(False)=="()"
        assert expr.toPython(True)=="()"

    def testTupleConstructor1(self):
        expr=TupleConstructor([Constant(9)])
        assert expr.toPython(False)=="(9,)"
        assert expr.toPython(True)=="(9,)"

    def testTupleConstructor2(self):
        expr=TupleConstructor([Constant(9),Constant(7)])
        assert expr.toPython(False)=="(9, 7)"
        assert expr.toPython(True)=="(9, 7)"

    def testSetConstructor0(self):
        expr=SetConstructor([])
        assert expr.toPython(False)=="set()"
        assert expr.toPython(True)=="set()"

    def testSetConstructor1(self):
        expr=SetConstructor([Constant(9)])
        assert expr.toPython(False)=="{9}"
        assert expr.toPython(True)=="{9}"

    def testSetConstructor2(self):
        expr=SetConstructor([Constant(9),Constant(7)])
        assert expr.toPython(False)=="{9, 7}"
        assert expr.toPython(True)=="{9, 7}"

    def testDictConstructor0(self):
        expr=DictConstructor([])
        assert expr.toPython(False)=="{}"
        assert expr.toPython(True)=="{}"

    def testDictConstructor1(self):
        expr=DictConstructor([(VarExpr('a'),Constant(9))])
        assert expr.toPython(False)=="{a: 9}"
        assert expr.toPython(True)=="{a: 9}"

    def testDictConstructor2(self):
        expr=DictConstructor([(VarExpr('a'),Constant(9)),
                              (Constant('x'),Constant(7))])
        matches=["{a: 9, 'x': 7}","{'x': 7, a: 9}"]
        assert expr.toPython(False) in matches
        assert expr.toPython(True) in matches

    def testDot0(self):
        expr=DotExpr(VarExpr('a'),[])
        assert expr.toPython(False)=="a"
        assert expr.toPython(True)=="a"

    def testDot1(self):
        expr=DotExpr(VarExpr('a'),['x'])
        assert expr.toPython(False)=="a.x"
        assert expr.toPython(True)=="a.x"

    def testDot2(self):
        expr=DotExpr(VarExpr('a'),['x','y'])
        assert expr.toPython(False)=="a.x.y"
        assert expr.toPython(True)=="a.x.y"

    def testIndexSimple(self):
        expr=IndexOperator(VarExpr('a'),Constant(1))
        assert expr.toPython(False)=="a[1]"
        assert expr.toPython(True)=="a[1]"

    def testIndexComplex(self):
        expr=IndexOperator(BinaryOperator('+',VarExpr('a'),VarExpr('b')),
                           Constant(1))
        assert expr.toPython(False)=="(a+b)[1]"
        assert expr.toPython(True)=="(a+b)[1]"

class BuildExprTestCase(unittest.TestCase):
    def testInt(self):
        expr=buildExpr(7)
        assert isinstance(expr,Constant)
        assert expr.py=='7'

    def testVar(self):
        expr=buildExpr(S('barney'))
        assert isinstance(expr,VarExpr)
        assert expr.py=="barney"

    def testStr(self):
        expr=buildExpr('fred')
        assert isinstance(expr,Constant)
        assert expr.py=="'fred'"

    def testPlusExpr(self):
        expr=buildExpr([S('+'),[9,7]])
        assert isinstance(expr,BinaryOperator)
        assert isinstance(expr.left,Constant)
        assert expr.left.py=='9'
        assert isinstance(expr.right,Constant)
        assert expr.right.py=='7'

    def testNestedExpr(self):
        expr=buildExpr([S('*'),[9,
                                [S('+'),[3,S('z')]]
                                ]])
        assert isinstance(expr,BinaryOperator)
        assert isinstance(expr.left,Constant)
        assert expr.left.py=='9'
        assert isinstance(expr.right,BinaryOperator)
        assert expr.right.operator==S('+')
        assert isinstance(expr.right.left,Constant)
        assert expr.right.left.py=='3'
        assert isinstance(expr.right.right,VarExpr)
        assert expr.right.right.py=='z'

    def testUnaryMinus(self):
        expr=buildExpr([S('-'),[9]])
        assert isinstance(expr,UnaryOperator)
        assert expr.operator==S('-')
        assert isinstance(expr.operand,Constant)
        assert expr.operand.py=='9'

    def testUnaryNot(self):
        expr=buildExpr([S('not'),[False]])
        assert isinstance(expr,UnaryOperator)
        assert expr.operator==S('not')
        assert isinstance(expr.operand,Constant)
        assert expr.operand.py=='False'

    def testCallExprNoArgs(self):
        expr=buildExpr([S('f'),[]])
        assert isinstance(expr,CallExpr)
        assert isinstance(expr.f,VarExpr)
        assert expr.f.py=='f'
        assert expr.posArgs==[]
        assert expr.kwArgs=={}

    def testCallExprOnlyPosArgs(self):
        expr=buildExpr([S('f'),[9,7]])
        assert isinstance(expr,CallExpr)
        assert isinstance(expr.f,VarExpr)
        assert expr.f.py=='f'
        assert len(expr.posArgs)==2
        assert isinstance(expr.posArgs[0],Constant)
        assert expr.posArgs[0].py=='9'
        assert isinstance(expr.posArgs[1],Constant)
        assert expr.posArgs[1].py=='7'
        assert expr.kwArgs=={}

    def testCallExprOnlyKWArgs(self):
        expr=buildExpr([S('f'),[],[('a',9),('b',7)]])
        assert isinstance(expr,CallExpr)
        assert isinstance(expr.f,VarExpr)
        assert expr.f.py=='f'
        assert expr.posArgs==[]
        assert len(expr.kwArgs)==2
        assert isinstance(expr.kwArgs['a'],Constant)
        assert expr.kwArgs['a'].py=='9'
        assert isinstance(expr.kwArgs['b'],Constant)
        assert expr.kwArgs['b'].py=='7'

    def testCallExprPosAndKWArgs(self):
        expr=buildExpr([S('f'),[S('x'),12],[('a',9),('b',7)]])
        assert isinstance(expr,CallExpr)
        assert isinstance(expr.f,VarExpr)
        assert expr.f.py=='f'

        assert len(expr.posArgs)==2
        assert isinstance(expr.posArgs[0],VarExpr)
        assert expr.posArgs[0].py=='x'
        assert isinstance(expr.posArgs[1],Constant)
        assert expr.posArgs[1].py=='12'

        assert len(expr.kwArgs)==2
        assert isinstance(expr.kwArgs['a'],Constant)
        assert expr.kwArgs['a'].py=='9'
        assert isinstance(expr.kwArgs['b'],Constant)
        assert expr.kwArgs['b'].py=='7'

    def testIfOperator(self):
        expr=buildExpr([S('if-expr'), [
                    [S('=='),[S('x'),9]],
                    [S('*'),[S('x'),7]],
                    [S('*'),[9,S('x')]]
                    ]])
        assert isinstance(expr,IfOperator)

        assert isinstance(expr.condExpr,BinaryOperator)
        assert expr.condExpr.operator==S('==')
        assert isinstance(expr.condExpr.left,VarExpr)
        assert expr.condExpr.left.py=='x'
        assert isinstance(expr.condExpr.right,Constant)
        assert expr.condExpr.right.py=='9'

        assert isinstance(expr.thenExpr,BinaryOperator)
        assert expr.thenExpr.operator==S('*')
        assert isinstance(expr.thenExpr.left,VarExpr)
        assert expr.thenExpr.left.py=='x'
        assert isinstance(expr.thenExpr.right,Constant)
        assert expr.thenExpr.right.py=='7'

        assert isinstance(expr.elseExpr,BinaryOperator)
        assert expr.elseExpr.operator==S('*')
        assert isinstance(expr.elseExpr.left,Constant)
        assert expr.elseExpr.left.py=='9'
        assert isinstance(expr.elseExpr.right,VarExpr)
        assert expr.elseExpr.right.py=='x'

    def testListConstructor0(self):
        expr=buildExpr([S('mk-list'),[]])
        assert isinstance(expr,ListConstructor)
        assert expr.elementExprs==[]

    def testListConstructor1(self):
        expr=buildExpr([S('mk-list'),[9]])
        assert isinstance(expr,ListConstructor)
        assert len(expr.elementExprs)==1
        assert isinstance(expr.elementExprs[0],Constant)
        assert expr.elementExprs[0].py=='9'

    def testListConstructor2(self):
        expr=buildExpr([S('mk-list'),[9,7]])
        assert isinstance(expr,ListConstructor)
        assert len(expr.elementExprs)==2
        assert isinstance(expr.elementExprs[0],Constant)
        assert expr.elementExprs[0].py=='9'
        assert isinstance(expr.elementExprs[1],Constant)
        assert expr.elementExprs[1].py=='7'

    def testTupleConstructor0(self):
        expr=buildExpr([S('mk-tuple'),[]])
        assert isinstance(expr,TupleConstructor)
        assert expr.elementExprs==[]

    def testTupleConstructor1(self):
        expr=buildExpr([S('mk-tuple'),[9]])
        assert isinstance(expr,TupleConstructor)
        assert len(expr.elementExprs)==1
        assert isinstance(expr.elementExprs[0],Constant)
        assert expr.elementExprs[0].py=='9'

    def testTupleConstructor2(self):
        expr=buildExpr([S('mk-tuple'),[9,7]])
        assert isinstance(expr,TupleConstructor)
        assert len(expr.elementExprs)==2
        assert isinstance(expr.elementExprs[0],Constant)
        assert expr.elementExprs[0].py=='9'
        assert isinstance(expr.elementExprs[1],Constant)
        assert expr.elementExprs[1].py=='7'

    def testSetConstructor0(self):
        expr=buildExpr([S('mk-set'),[]])
        assert isinstance(expr,SetConstructor)
        assert expr.elementExprs==[]

    def testSetConstructor1(self):
        expr=buildExpr([S('mk-set'),[9]])
        assert isinstance(expr,SetConstructor)
        assert len(expr.elementExprs)==1
        assert isinstance(expr.elementExprs[0],Constant)
        assert expr.elementExprs[0].py=='9'

    def testSetConstructor2(self):
        expr=buildExpr([S('mk-set'),[9,7]])
        assert isinstance(expr,SetConstructor)
        assert len(expr.elementExprs)==2
        assert isinstance(expr.elementExprs[0],Constant)
        assert expr.elementExprs[0].py=='9'
        assert isinstance(expr.elementExprs[1],Constant)
        assert expr.elementExprs[1].py=='7'

    def testDictConstructor0(self):
        expr=buildExpr([S('mk-dict'),None,[]])
        assert isinstance(expr,DictConstructor)
        assert expr.pairExprs==[]

    def testDictConstructor1(self):
        expr=buildExpr([S('mk-dict'),None,[[S('a'), 9]]])
        assert isinstance(expr,DictConstructor)
        assert len(expr.pairExprs)==1
        assert isinstance(expr.pairExprs[0][0],VarExpr)
        assert expr.pairExprs[0][0].py=='a'
        assert isinstance(expr.pairExprs[0][1],Constant)
        assert expr.pairExprs[0][1].py=='9'

    def testDictConstructor2(self):
        expr=buildExpr([S('mk-dict'),None,[[S('a'), 9],['x',7]]])
        assert isinstance(expr,DictConstructor)
        assert len(expr.pairExprs)==2
        assert isinstance(expr.pairExprs[0][0],VarExpr)
        assert expr.pairExprs[0][0].py=='a'
        assert isinstance(expr.pairExprs[0][1],Constant)
        assert expr.pairExprs[0][1].py=='9'
        assert isinstance(expr.pairExprs[1][0],Constant)
        assert expr.pairExprs[1][0].py=="'x'"
        assert isinstance(expr.pairExprs[1][1],Constant)
        assert expr.pairExprs[1][1].py=='7'

    def testDot0(self):
        expr=buildExpr([S('.'),[S('a')]])
        assert isinstance(expr,VarExpr)
        assert expr.py=='a'

    def testDot1(self):
        expr=buildExpr([S('.'),[S('a'),S('x')]])
        assert isinstance(expr,DotExpr)
        assert isinstance(expr.base,VarExpr)
        assert expr.base.py=='a'
        assert expr.path==[S('x')]

    def testDot2(self):
        expr=buildExpr([S('.'),[S('a'),S('x'),S('y')]])
        assert isinstance(expr,DotExpr)
        assert isinstance(expr.base,VarExpr)
        assert expr.base.py=='a'
        assert expr.path==[S('x'),S('y')]

    def testIndexSimple(self):
        expr=buildExpr([S('[]'),[S('a'),1]])
        assert isinstance(expr,IndexOperator)
        assert isinstance(expr.left,VarExpr)
        assert expr.left.py=='a'
        assert isinstance(expr.right,Constant)
        assert expr.right.py=='1'

    def testIndexComplex(self):
        expr=buildExpr([S('[]'),
                        [[S('+'),[S('a'),S('b')]],
                        1]])
        assert isinstance(expr,IndexOperator)
        assert isinstance(expr.left,BinaryOperator)
        assert expr.left.operator==S('+')
        assert isinstance(expr.left.left,VarExpr)
        assert expr.left.left.py=='a'
        assert isinstance(expr.left.right,VarExpr)
        assert expr.left.right.py=='b'
        assert isinstance(expr.right,Constant)
        assert expr.right.py=='1'

class StmtTestCase(unittest.TestCase):
    def testAssignment(self):
        stmt=Assignment(VarExpr('foo.bar'),
                        BinaryOperator('*',Constant(9),Constant(7)))
        assert(stmt.toPythonTree()=='foo.bar=9*7')
        assert(stmt.toPythonFlat()=='foo.bar=9*7\n')

    def testBlock(self):
        stmt=Block([Assignment(VarExpr('x'),Constant(9)),
                    Assignment(VarExpr('foo.bar'),
                               BinaryOperator('*',VarExpr('x'),Constant(7)))])
        assert(stmt.toPythonTree()==('x=9','foo.bar=x*7'))
        assert(stmt.toPythonFlat()=="""x=9
foo.bar=x*7
""")

    def testIfNoElse(self):
        stmt=IfStmt(BinaryOperator('<',VarExpr('n'),Constant(2)),
                    Assignment(VarExpr('x'),Constant(1)))
        assert(stmt.toPythonTree()==('if n<2:',['x=1']))
        assert(stmt.toPythonFlat()=="""if n<2:
    x=1
""")

    def testIfElse(self):
        stmt=IfStmt(BinaryOperator('<',VarExpr('n'),Constant(2)),
                    Assignment(VarExpr('x'),Constant(1)),
                    Assignment(VarExpr('x'),BinaryOperator('*',Constant(9),Constant(7))))
        assert(stmt.toPythonTree()==('if n<2:',['x=1'],'else:',['x=9*7']))
        assert(stmt.toPythonFlat()=="""if n<2:
    x=1
else:
    x=9*7
""")

    def testBreak(self):
        stmt=BreakStmt()
        assert(stmt.toPythonTree()=='break')
        assert(stmt.toPythonFlat()=="""break
""")

    def testContinue(self):
        stmt=ContinueStmt()
        assert(stmt.toPythonTree()=='continue')
        assert(stmt.toPythonFlat()=="""continue
""")

    def testReturn(self):
        stmt=ReturnStmt(Constant(0))
        assert(stmt.toPythonTree()=='return 0')
        assert(stmt.toPythonFlat()=="""return 0
""")

    def testYield(self):
        stmt=YieldStmt(Constant(0))
        assert(stmt.toPythonTree()=='yield 0')
        assert(stmt.toPythonFlat()=="""yield 0
""")

    def testDefNoArgs(self):
        stmt=DefStmt(S('f'),[],[],None,[],ReturnStmt(Constant(0)))
        assert(stmt.toPythonTree()==('def f():',['return 0']))
        assert(stmt.toPythonFlat()=="""def f():
    return 0
""")

    def testDefNoArgsGlobals1(self):
        stmt=DefStmt(S('f'),[],[],None,[],
                     ReturnStmt(Constant(0)),
                     [S('x')])
        assert(stmt.toPythonTree()==('def f():',['global x','return 0']))
        assert(stmt.toPythonFlat()=="""def f():
    global x
    return 0
""")

    def testDefNoArgsGlobals2(self):
        stmt=DefStmt(S('f'),[],[],None,[],
                     ReturnStmt(Constant(0)),
                     [S('x'),S('y')])
        assert(stmt.toPythonTree()==('def f():',['global x,y','return 0']))
        assert(stmt.toPythonFlat()=="""def f():
    global x,y
    return 0
""")

    def testDefNoArgsNonlocals1(self):
        stmt=DefStmt(S('f'),[],[],None,[],ReturnStmt(Constant(0)),[],[S('x')])
        assert(stmt.toPythonTree()==('def f():',['nonlocal x','return 0']))
        assert(stmt.toPythonFlat()=="""def f():
    nonlocal x
    return 0
""")

    def testDefNoArgsNonlocals2(self):
        stmt=DefStmt(S('f'),[],[],None,[],
                     ReturnStmt(Constant(0)),[],[S('x'),S('y')])
        assert(stmt.toPythonTree()==('def f():',['nonlocal x,y','return 0']))
        assert(stmt.toPythonFlat()=="""def f():
    nonlocal x,y
    return 0
""")

    def testDefNoArgsGlobals2Nonlocals2(self):
        stmt=DefStmt(S('f'),[],[],None,[],
                     ReturnStmt(Constant(0)),
                     [S('a'),S('b')],
                     [S('x'),S('y')])
        assert(stmt.toPythonTree()==('def f():',['global a,b','nonlocal x,y','return 0']))
        assert(stmt.toPythonFlat()=="""def f():
    global a,b
    nonlocal x,y
    return 0
""")

    def testDefOnlyFixedArgs(self):
        stmt=DefStmt(S('f'),[S('n')],[],None,[],ReturnStmt(VarExpr(S('n'))))
        assert(stmt.toPythonTree()==('def f(n):',['return n']))
        assert(stmt.toPythonFlat()=="""def f(n):
    return n
""")

    def testDefOnlyOptionalArgs(self):
        stmt=DefStmt(S('f'),[],[(S('n'),Constant(None))],None,[],
                     ReturnStmt(VarExpr(S('n'))))
        assert(stmt.toPythonTree()==('def f(n=None):',['return n']))
        assert(stmt.toPythonFlat()=="""def f(n=None):
    return n
""")

    def testDefOnlyKwArgsNoDefaults(self):
        stmt=DefStmt(S('f'),[],[],None,[S('n')],ReturnStmt(VarExpr(S('n'))))
        assert(stmt.toPythonTree()==('def f(*,n):',['return n']))
        assert(stmt.toPythonFlat()=="""def f(*,n):
    return n
""")

    def testDefOnlyKwArgsWithDefaults(self):
        stmt=DefStmt(S('f'),[],[],None,[(S('n'),Constant(None))],ReturnStmt(VarExpr(S('n'))))
        assert(stmt.toPythonTree()==('def f(*,n=None):',['return n']))
        assert(stmt.toPythonFlat()=="""def f(*,n=None):
    return n
""")

    def testDefAllArgTypes(self):
        stmt=DefStmt(S('f'),
                     [S('a')],[(S('b'),Constant(9))],None,[S('c'),(S('d'),Constant(7))],
                     ReturnStmt(VarExpr(S('a'))))
        assert(stmt.toPythonTree()==('def f(a,b=9,*,c,d=7):',['return a']))
        assert(stmt.toPythonFlat()=="""def f(a,b=9,*,c,d=7):
    return a
""")

    def testClassNoParentsNoBody(self):
        stmt=ClassStmt(S('C'),[],None)
        assert(stmt.toPythonTree()==('class C():',['pass']))
        assert(stmt.toPythonFlat()=="""class C():
    pass
""")

    def testClass1ParentNoBody(self):
        stmt=ClassStmt(S('C'),[S('A')],None)
        assert(stmt.toPythonTree()==('class C(A):',['pass']))
        assert(stmt.toPythonFlat()=="""class C(A):
    pass
""")

    def testClass2ParentsNoBody(self):
        stmt=ClassStmt(S('C'),[S('A'),S('B')],None)
        assert(stmt.toPythonTree()==('class C(A,B):',['pass']))
        assert(stmt.toPythonFlat()=="""class C(A,B):
    pass
""")

    def testClassNoParentsBlockBody(self):
        stmt=ClassStmt(S('C'),[],
                       Block([Assignment(VarExpr(S('z')),Constant(7)),
                              DefStmt('__init__',[S('n')],[],None,[],
                                      Assignment(DotExpr(VarExpr('self'),[S('q')]),
                                                 VarExpr(S('n')))),
                              DefStmt('sq',[],[],None,[],
                                      ReturnStmt(BinaryOperator('*',
                                                                DotExpr(VarExpr('self'),[S('q')]),
                                                                DotExpr(VarExpr('self'),[S('q')])
                                                                )
                                                 )
                                      )
                              ]))
        assert(stmt.toPythonTree()==('class C():',
                                     [('z=7',
                                       ('def __init__(n):',
                                        ['self.q=n']),
                                       ('def sq():',
                                        ['return self.q*self.q'])
                                       )]))
        assert(stmt.toPythonFlat()=="""class C():
    z=7
    def __init__(n):
        self.q=n
    def sq():
        return self.q*self.q
""")

    def testImport1(self):
        stmt=ImportStmt(['re'])
        assert stmt.toPythonTree()=='import re'
        assert stmt.toPythonFlat()=="""import re
"""

    def testImport2(self):
        stmt=ImportStmt(['re','adder.parser'])
        assert stmt.toPythonTree()=='import re, adder.parser'
        assert stmt.toPythonFlat()=="""import re, adder.parser
"""

class BuildStmtTestCase(unittest.TestCase):
    def testAssignment(self):
        stmt=buildStmt([S(':='),[S('foo.bar'),
                        [S('*'),[9,7]]]])
        assert(stmt.toPythonTree()=='foo.bar=9*7')
        assert(stmt.toPythonFlat()=='foo.bar=9*7\n')

    def testBlock(self):
        stmt=buildStmt([S('begin'),
                        [[S(':='),[S('x'),9]],
                        [S(':='),[S('foo.bar'),[S('*'),[S('x'),7]]]]]])
        assert(stmt.toPythonTree()==('x=9','foo.bar=x*7'))
        assert(stmt.toPythonFlat()=="""x=9
foo.bar=x*7
""")

    def testBlockEmpty(self):
        stmt=buildStmt([S('begin'),[]])
        assert(stmt.toPythonTree()==('assert True'))
        assert(stmt.toPythonFlat()=='assert True\n')

    def testIfNoElse(self):
        stmt=buildStmt([S('if-stmt'),[
                        [S('<'),[S('n'),2]],
                        [S(':='),[S('x'),1]]
                        ]
                        ])
        assert(stmt.toPythonTree()==('if n<2:',['x=1']))
        assert(stmt.toPythonFlat()=="""if n<2:
    x=1
""")

    def testIfElse(self):
        stmt=buildStmt([S('if-stmt'),[
                        [S('<'),[S('n'),2]],
                        [S(':='),[S('x'),1]],
                        [S(':='),[
                            S('x'),
                         [S('*'),[9,7]]
                         ]]
                        ]
                        ])
        assert(stmt.toPythonTree()==('if n<2:',['x=1'],'else:',['x=9*7']))
        assert(stmt.toPythonFlat()=="""if n<2:
    x=1
else:
    x=9*7
""")

    def testBreak(self):
        stmt=buildStmt([S('break'),[]])
        assert(stmt.toPythonTree()=='break')
        assert(stmt.toPythonFlat()=="""break
""")

    def testContinue(self):
        stmt=buildStmt([S('continue'),[]])
        assert(stmt.toPythonTree()=='continue')
        assert(stmt.toPythonFlat()=="""continue
""")

    def testReturn(self):
        stmt=buildStmt([S('return'),[0]])
        assert(stmt.toPythonTree()=='return 0')
        assert(stmt.toPythonFlat()=="""return 0
""")

    def testYield(self):
        stmt=buildStmt([S('yield'),[0]])
        assert(stmt.toPythonTree()=='yield 0')
        assert(stmt.toPythonFlat()=="""yield 0
""")

    def testRaise(self):
        stmt=buildStmt([S('raise'),[0]])
        assert(stmt.toPythonTree()=='raise 0')
        assert(stmt.toPythonFlat()=="""raise 0
""")

    def testRaiseReraise(self):
        stmt=buildStmt([S('raise'),[]])
        assert(stmt.toPythonTree()=='raise')
        assert(stmt.toPythonFlat()=="""raise
""")

    def testDefNoArgs(self):
        stmt=buildStmt([S('def'),[S('f'),[],[S('return'),[0]]]])
        assert(stmt.toPythonTree()==('def f():',['return 0']))
        assert(stmt.toPythonFlat()=="""def f():
    return 0
""")

    def testDefNoArgsGlobals1(self):
        stmt=buildStmt([S('def'),[S('f'),
                        [S('&global'),S('x')],
                        [S('return'),[0]]]])
        assert(stmt.toPythonTree()==('def f():',['global x','return 0']))
        assert(stmt.toPythonFlat()=="""def f():
    global x
    return 0
""")

    def testDefNoArgsGlobals2(self):
        stmt=buildStmt([S('def'),[S('f'),
                        [S('&global'),S('x'),S('y')],
                        [S('return'),[0]]]])
        assert(stmt.toPythonTree()==('def f():',['global x,y','return 0']))
        assert(stmt.toPythonFlat()=="""def f():
    global x,y
    return 0
""")

    def testDefNoArgsNonlocals1(self):
        stmt=buildStmt([S('def'),[S('f'),
                        [S('&nonlocal'),S('x')],
                        [S('return'),[0]]]])
        assert(stmt.toPythonTree()==('def f():',['nonlocal x','return 0']))
        assert(stmt.toPythonFlat()=="""def f():
    nonlocal x
    return 0
""")

    def testDefNoArgsNonlocals2(self):
        stmt=buildStmt([S('def'),[S('f'),
                        [S('&nonlocal'),S('x'),S('y')],
                        [S('return'),[0]]]])
        assert(stmt.toPythonTree()==('def f():',['nonlocal x,y','return 0']))
        assert(stmt.toPythonFlat()=="""def f():
    nonlocal x,y
    return 0
""")

    def testDefNoArgsGlobals2Nonlocals2(self):
        stmt=buildStmt([S('def'),[S('f'),
                        [S('&global'),S('a'),S('b'),
                         S('&nonlocal'),S('x'),S('y')],
                        [S('return'),[0]]]])
        assert(stmt.toPythonTree()==('def f():',['global a,b','nonlocal x,y','return 0']))
        assert(stmt.toPythonFlat()=="""def f():
    global a,b
    nonlocal x,y
    return 0
""")

    def testDefOnlyFixedArgs(self):
        stmt=buildStmt([S('def'),[S('f'),[S('n')],[S('return'),[S('n')]]]])
        assert(stmt.toPythonTree()==('def f(n):',['return n']))
        assert(stmt.toPythonFlat()=="""def f(n):
    return n
""")

    def testDefOnlyOptionalArgs(self):
        stmt=buildStmt([S('def'),
                        [S('f'),
                        [S('&optional'),S('n'),(S('x'),9)],
                        [S('return'),[S('n')]]]])
        assert(stmt.toPythonTree()==('def f(n=None,x=9):',['return n']))
        assert(stmt.toPythonFlat()=="""def f(n=None,x=9):
    return n
""")

    def testDefOnlyKwArgsNoDefaults(self):
        stmt=buildStmt([S('def'),[S('f'),
                        [S('&key'),S('n')],
                        [S('return'),[S('n')]]]])
        assert(stmt.toPythonTree()==('def f(*,n):',['return n']))
        assert(stmt.toPythonFlat()=="""def f(*,n):
    return n
""")

    def testDefOnlyKwArgsWithDefaults(self):
        stmt=buildStmt([S('def'),[S('f'),
                        [S('&key'),(S('n'),6),(S('x'),None)],
                        [S('return'),[S('n')]]]])
        assert(stmt.toPythonTree()==('def f(*,n=6,x=None):',['return n']))
        assert(stmt.toPythonFlat()=="""def f(*,n=6,x=None):
    return n
""")

    def testDefAllArgTypes(self):
        stmt=DefStmt(S('f'),
                     [S('a')],[(S('b'),Constant(9))],None,[S('c'),(S('d'),Constant(7))],
                     ReturnStmt(VarExpr(S('a'))))
        stmt=buildStmt([S('def'),[S('f'),
                        [S('a'),
                         S('&optional'),(S('b'),9),
                         S('&key'),S('c'),(S('d'),7)],
                        [S('return'),[S('a')]]]])
        assert(stmt.toPythonTree()==('def f(a,b=9,*,c,d=7):',['return a']))
        assert(stmt.toPythonFlat()=="""def f(a,b=9,*,c,d=7):
    return a
""")

    def testClassNoParentsNoBody(self):
        stmt=buildStmt([S('class'),[S('C'),[]]])
        assert(stmt.toPythonTree()==('class C():',['pass']))
        assert(stmt.toPythonFlat()=="""class C():
    pass
""")

    def testClass1ParentNoBody(self):
        stmt=buildStmt([S('class'),[S('C'),[S('A')]]])
        assert(stmt.toPythonTree()==('class C(A):',['pass']))
        assert(stmt.toPythonFlat()=="""class C(A):
    pass
""")

    def testClass2ParentsNoBody(self):
        stmt=ClassStmt(S('C'),[S('A'),S('B')],None)
        stmt=buildStmt([S('class'),[S('C'),[S('A'),S('B')]]])
        assert(stmt.toPythonTree()==('class C(A,B):',['pass']))
        assert(stmt.toPythonFlat()=="""class C(A,B):
    pass
""")

    def testClassNoParentsBlockBody(self):
        stmt=buildStmt([S('class'),[S('C'),[],
                        [S(':='),[S('z'),7]],
                        [S('def'),[
                            S('__init__'),
                            [S('n')],
                            [S(':='),[
                                    [S('.'),[S('self'),S('q')]],
                                    S('n')
                                    ]]
                         ]],
                        [S('def'),[S('sq'),[],
                         [S('return'),[
                                    [S('*'),[
                                            [S('.'),[S('self'),S('q')]],
                                            [S('.'),[S('self'),S('q')]]
                                            ]]
                                    ]]
                         ]]
                        ]])
        assert(stmt.toPythonTree()==('class C():',
                                     [('z=7',
                                       ('def __init__(n):',
                                        ['self.q=n']),
                                       ('def sq():',
                                        ['return self.q*self.q'])
                                       )]))
        assert(stmt.toPythonFlat()=="""class C():
    z=7
    def __init__(n):
        self.q=n
    def sq():
        return self.q*self.q
""")

    def testImport1(self):
        stmt=buildStmt([S('import'),[S('re')]])
        assert stmt.toPythonTree()=='import re'
        assert stmt.toPythonFlat()=="""import re
"""

    def testImport2(self):
        stmt=buildStmt([S('import'),[S('re'),S('adder.parser')]])
        assert stmt.toPythonTree()=='import re, adder.parser'
        assert stmt.toPythonFlat()=="""import re, adder.parser
"""

suite=unittest.TestSuite(
    ( unittest.makeSuite(ExprTestCase,'test'),
      unittest.makeSuite(BuildExprTestCase,'test'),
      unittest.makeSuite(StmtTestCase,'test'),
      unittest.makeSuite(BuildStmtTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

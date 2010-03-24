#!/usr/bin/env python3

import unittest,pdb,sys,os
from adder.pyle import *

class ExprTestCase(unittest.TestCase):
    def testInt(self):
        expr=Constant(17)
        assert expr.toPython(False)=='17'
        assert expr.toPython(True)=='17'

    def testVar(self):
        expr=VarExpr('barney')
        assert expr.toPython(False)=='barney'
        assert expr.toPython(True)=='barney'

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
        assert expr.toPython(False)=="{a: 9, 'x': 7}"
        assert expr.toPython(True)=="{a: 9, 'x': 7}"

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

    def testIf(self):
        stmt=IfStmt(BinaryOperator('<',VarExpr('n'),Constant(2)),
                    Assignment(VarExpr('x'),Constant(1)),
                    Assignment(VarExpr('x'),BinaryOperator('*',Constant(9),Constant(7))))
        assert(stmt.toPythonTree()==('if n<2:',['x=1'],'else:',['x=9*7']))
        assert(stmt.toPythonFlat()=="""if n<2:
    x=1
else:
    x=9*7
""")

    def testReturn(self):
        stmt=ReturnStmt(Constant(0))
        assert(stmt.toPythonTree()=='return 0')
        assert(stmt.toPythonFlat()=="""return 0
""")

    def testDefNoArgs(self):
        stmt=DefStmt('f',[],[],[],ReturnStmt(Constant(0)))
        assert(stmt.toPythonTree()==('def f():',['return 0']))
        assert(stmt.toPythonFlat()=="""def f():
    return 0
""")

    def testDefOnlyFixedArgs(self):
        stmt=DefStmt('f',['n'],[],[],ReturnStmt(VarExpr('n')))
        assert(stmt.toPythonTree()==('def f(n):',['return n']))
        assert(stmt.toPythonFlat()=="""def f(n):
    return n
""")

    def testDefOnlyOptionalArgs(self):
        stmt=DefStmt('f',[],[('n',Constant(None))],[],ReturnStmt(VarExpr('n')))
        assert(stmt.toPythonTree()==('def f(n=None):',['return n']))
        assert(stmt.toPythonFlat()=="""def f(n=None):
    return n
""")

    def testDefOnlyKwArgsNoDefaults(self):
        stmt=DefStmt('f',[],[],['n'],ReturnStmt(VarExpr('n')))
        assert(stmt.toPythonTree()==('def f(*,n):',['return n']))
        assert(stmt.toPythonFlat()=="""def f(*,n):
    return n
""")

    def testDefOnlyKwArgsWithDefaults(self):
        stmt=DefStmt('f',[],[],[('n',Constant(None))],ReturnStmt(VarExpr('n')))
        assert(stmt.toPythonTree()==('def f(*,n=None):',['return n']))
        assert(stmt.toPythonFlat()=="""def f(*,n=None):
    return n
""")

    def testDefAllArgTypes(self):
        stmt=DefStmt('f',['a'],[('b',Constant(9))],['c',('d',Constant(7))],
                     ReturnStmt(VarExpr('a')))
        assert(stmt.toPythonTree()==('def f(a,b=9,*,c,d=7):',['return a']))
        assert(stmt.toPythonFlat()=="""def f(a,b=9,*,c,d=7):
    return a
""")

suite=unittest.TestSuite(
    ( unittest.makeSuite(ExprTestCase,'test'),
      unittest.makeSuite(StmtTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

#!/usr/bin/env python3

import unittest,pdb,sys,os
from adder.reg import *
from adder.common import Symbol as S
import adder.common
import adder.pyle

class StrTestCase(unittest.TestCase):
    def testVar(self):
        assert str(Var(S('fred')))=='fred'

    def testLiteralInt(self):
        assert str(Literal(9))=='9'

    def testLiteralSym(self):
        assert str(Literal(S('fred')))=="adder.common.Symbol('fred')"

    def testQuoteList(self):
        assert str(Quote(List([Literal(S('fred')),
                               Literal(5),
                               List([Literal(S('barney'))])
                               ]
                              )
                         )
                   )=="(adder.common.Symbol('fred') 5 (adder.common.Symbol('barney')))"

    def testCall0(self):
        assert str(Call(Var(S('barney')),
                        [],[]))=='barney()'

    def testCall1Pos(self):
        assert str(Call(Var(S('barney')),
                        [Var(S('wilma'))],[]))=='barney(wilma)'
        assert str(Call(Var(S('barney')),
                        [Literal(9)],[]))=='barney(9)'

    def testCall1Kw(self):
        assert str(Call(Var(S('barney')),
                        [],[(Var(S('wilma')),Var(S('betty')))]
                        ))=='barney(wilma=betty)'
        assert str(Call(Var(S('barney')),
                        [],[(Var(S('wilma')),Literal(9))]
                        ))=='barney(wilma=9)'

    def testCall1Pos1Kw(self):
        assert str(Call(Var(S('barney')),
                        [Var(S('dino'))],
                        [(Var(S('wilma')),Var(S('betty')))]
                        ))=='barney(dino,wilma=betty)'

    def testCall2Pos1Kw(self):
        assert str(Call(Var(S('barney')),
                        [Var(S('dino')),Literal(9)],
                        [(Var(S('wilma')),Var(S('betty')))]
                        ))=='barney(dino,9,wilma=betty)'

    def testCall2Pos2Kw(self):
        assert str(Call(Var(S('barney')),
                        [Var(S('dino')),Literal(9)],
                        [(Var(S('wilma')),Var(S('betty'))),
                         (Var(S('pebbles')),Literal(3))]
                        ))=='barney(dino,9,wilma=betty,pebbles=3)'

    def testAssign(self):
        assert str(Assign(Var(S('fred')),Var(S('barney'))))=='fred=barney'
        assert str(Assign(Var(S('fred')),Literal(7)))=='fred=7'

    def testReturn(self):
        assert str(Return(Var(S('fred'))))=='return fred'
        assert str(Return(Literal(7)))=='return 7'

    def testYield(self):
        assert str(Yield(Var(S('fred'))))=='yield fred'
        assert str(Yield(Literal(7)))=='yield 7'

    def testRaise(self):
        assert str(Raise(Var(S('fred'))))=='raise fred'

    def testReraise(self):
        assert str(Reraise())=='raise'

    def testTry(self):
        assert str(Try(Return(Literal(7)),
                       [(Var(S('TypeError')),Var(S('te')),
                         Return(Literal(12))),
                        (Var(S('ValueError')),Var(S('ve')),
                         Reraise())],
                       Assign(Var(S('x')),Literal(3))))==(
            '{try return 7'
            +' {except TypeError as te: return 12}'
            +' {except ValueError as ve: raise}'
            +' {finally: x=3}}'
            )

    def testIf(self):
        assert str(If(Var(S('x')),
                      Return(Literal(9)),
                      None)
                   )=='{if x then return 9}'
        assert str(If(Literal(True),
                      Return(Literal(9)),
                      None)
                   )=='{if True then return 9}'

    def testIfElse(self):
        assert str(If(Var(S('x')),
                      Return(Literal(9)),
                      Return(Literal(3)))
                   )=='{if x then return 9 else return 3}'
        assert str(If(Literal(True),
                      Return(Literal(9)),
                      Return(Literal(3)))
                   )=='{if True then return 9 else return 3}'

    def testWhile(self):
        assert str(While(Var(S('x')),
                         Return(Literal(9)))
                   )=='{while x return 9}'
        assert str(While(Literal(True),
                         Return(Literal(9)))
                   )=='{while True return 9}'

    def testDef0(self):
        assert str(Def(Var(S('g')),[],[],
                       [],[],
                       Return(Literal(9))))=='{def g() return 9}'

    def testDef1Pos(self):
        assert str(Def(Var(S('g')),[Var(S('x'))],[],
                       [],[],
                       Return(Literal(9))))=='{def g(x) return 9}'

    def testDef1Kw(self):
        assert str(Def(Var(S('g')),[],[Var(S('x'))],
                       [],[],
                       Return(Literal(9))))=='{def g(*,x) return 9}'

    def testDef1Pos1Kw(self):
        assert str(Def(Var(S('g')),[Var(S('x'))],[Var(S('y'))],
                       [],[],
                       Return(Literal(9))))=='{def g(x,*,y) return 9}'

    def testDef2Pos1Kw(self):
        assert str(Def(Var(S('g')),[Var(S('x')),Var(S('y'))],
                       [Var(S('z'))],
                       [],[],
                       Return(Literal(9))))=='{def g(x,y,*,z) return 9}'

    def testDef2Pos2Kw(self):
        assert str(Def(Var(S('g')),[Var(S('x')),Var(S('y'))],
                       [Var(S('a')),Var(S('b'))],
                       [],[],
                       Return(Literal(9))))=='{def g(x,y,*,a,b) return 9}'

    def testBreak(self):
        assert str(Break())=='break'

    def testContinue(self):
        assert str(Continue())=='continue'

    def testPass(self):
        assert str(Pass())=='pass'

    def testBegin0(self):
        assert str(Begin([]))=='{}'

    def testBegin1(self):
        assert str(Begin([Assign(Var(S('x')),Literal(9))]))=='{x=9}'

    def testBegin2(self):
        assert str(Begin([
                    Assign(Var(S('x')),Literal(9)),
                    Assign(Var(S('z')),Literal(7))]))=='{x=9; z=7}'

class ToPythonTestCase(unittest.TestCase):
    def toP(self,il):
        tree=il.toPythonTree()
        flat=flatten(tree)
        return (tree,flat)

    def testVar(self):
        assert Var(S('fred')).toPythonTree()=='fred'

    def testLiteralInt(self):
        assert Literal(9).toPythonTree()=='9'

    def testLiteralSym(self):
        assert Literal(S('fred')).toPythonTree()=="adder.common.Symbol('fred')"

    def testCall0(self):
        assert self.toP(Call(Var(S('fred')),[],[]))==("fred()","fred()\n")

    def testCall1Pos(self):
        assert self.toP(Call(Var(S('fred')),
                             [Var(S('x'))],
                             []))==("fred(x)","fred(x)\n")

    def testCall2Pos(self):
        assert self.toP(Call(Var(S('fred')),
                             [Var(S('x')),Var(S('y'))],
                             []))==("fred(x,y)","fred(x,y)\n")

    def testCall1Kw(self):
        assert self.toP(Call(Var(S('fred')),
                             [],
                             [(Var(S('x')),Literal(9))]
                             ))==("fred(x=9)","fred(x=9)\n")

    def testCall2Kw(self):
        assert self.toP(Call(Var(S('fred')),
                             [],
                             [(Var(S('x')),Literal(9)),
                              (Var(S('y')),Literal(7)),
                              ]
                             ))==("fred(x=9,y=7)","fred(x=9,y=7)\n")

    def testCall2Pos1Kw(self):
        assert self.toP(Call(Var(S('fred')),
                             [Literal(3),Literal(5)],
                             [(Var(S('x')),Literal(9))]
                             ))==("fred(3,5,x=9)","fred(3,5,x=9)\n")

    def testCall2Pos2Kw(self):
        assert self.toP(Call(Var(S('fred')),
                             [Literal(3),Literal(5)],
                             [(Var(S('x')),Literal(9)),
                              (Var(S('y')),Literal(7)),
                              ]
                             ))==("fred(3,5,x=9,y=7)","fred(3,5,x=9,y=7)\n")

    def testAssignLiteral(self):
        assert self.toP(Assign(Var(S('fred')),
                               Literal(7)))==("fred=7","fred=7\n")

    def testAssignVar(self):
        assert self.toP(Assign(Var(S('fred')),
                               Var(S('x'))))==("fred=x","fred=x\n")

    def testAssignCall(self):
        assert self.toP(Assign(Var(S('fred')),
                               Call(Var(S('barney')),
                                    [Literal(3)],[])))==("fred=barney(3)",
                                                         "fred=barney(3)\n")

suite=unittest.TestSuite(
    ( 
      unittest.makeSuite(StrTestCase,'test'),
      unittest.makeSuite(ToPythonTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

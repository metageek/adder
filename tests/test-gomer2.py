#!/usr/bin/env python3

import unittest,pdb,sys,os
from adder.gomer2 import *
from adder.common import Symbol as S
import adder.common

class StrTestCase(unittest.TestCase):
    def testVar(self):
        assert str(Var(S('fred')))=='fred'

    def testLiteralInt(self):
        assert str(Literal(9))=='9'

    def testLiteralSym(self):
        assert str(Literal(S('fred')))=="adder.common.Symbol('fred')"

    def testCall0(self):
        assert str(Call(Var(S('fred')),Var(S('barney')),
                        [],[]))=='fred=barney()'

    def testCall1Pos(self):
        assert str(Call(Var(S('fred')),Var(S('barney')),
                        [Var(S('wilma'))],[]))=='fred=barney(wilma)'
        assert str(Call(Var(S('fred')),Var(S('barney')),
                        [Literal(9)],[]))=='fred=barney(9)'

    def testCall1Kw(self):
        assert str(Call(Var(S('fred')),Var(S('barney')),
                        [],[(Var(S('wilma')),Var(S('betty')))]
                        ))=='fred=barney(wilma=betty)'
        assert str(Call(Var(S('fred')),Var(S('barney')),
                        [],[(Var(S('wilma')),Literal(9))]
                        ))=='fred=barney(wilma=9)'

    def testCall1Pos1Kw(self):
        assert str(Call(Var(S('fred')),Var(S('barney')),
                        [Var(S('dino'))],
                        [(Var(S('wilma')),Var(S('betty')))]
                        ))=='fred=barney(dino,wilma=betty)'

    def testCall2Pos1Kw(self):
        assert str(Call(Var(S('fred')),Var(S('barney')),
                        [Var(S('dino')),Literal(9)],
                        [(Var(S('wilma')),Var(S('betty')))]
                        ))=='fred=barney(dino,9,wilma=betty)'

    def testCall2Pos2Kw(self):
        assert str(Call(Var(S('fred')),Var(S('barney')),
                        [Var(S('dino')),Literal(9)],
                        [(Var(S('wilma')),Var(S('betty'))),
                         (Var(S('pebbles')),Literal(3))]
                        ))=='fred=barney(dino,9,wilma=betty,pebbles=3)'

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
                       Return(Literal(9))))=='{def g() return 9}'

    def testDef1Pos(self):
        assert str(Def(Var(S('g')),[Var(S('x'))],[],
                       Return(Literal(9))))=='{def g(x) return 9}'

    def testDef1Kw(self):
        assert str(Def(Var(S('g')),[],[Var(S('x'))],
                       Return(Literal(9))))=='{def g(*,x) return 9}'

    def testDef1Pos1Kw(self):
        assert str(Def(Var(S('g')),[Var(S('x'))],[Var(S('y'))],
                       Return(Literal(9))))=='{def g(x,*,y) return 9}'

    def testDef2Pos1Kw(self):
        assert str(Def(Var(S('g')),[Var(S('x')),Var(S('y'))],
                       [Var(S('z'))],
                       Return(Literal(9))))=='{def g(x,y,*,z) return 9}'

    def testDef2Pos2Kw(self):
        assert str(Def(Var(S('g')),[Var(S('x')),Var(S('y'))],
                       [Var(S('a')),Var(S('b'))],
                       Return(Literal(9))))=='{def g(x,y,*,a,b) return 9}'

    def testBreak(self):
        assert str(Break())=='break'

    def testContinue(self):
        assert str(Continue())=='continue'

    def testPass(self):
        assert str(Pass())=='pass'

    def testGlobal(self):
        assert str(Global([Var(S('fred')),Var(S('barney'))])
                   )=='global fred,barney'

    def testNonlocal(self):
        assert str(Nonlocal([Var(S('fred')),Var(S('barney'))])
                   )=='nonlocal fred,barney'

    def testBlock0(self):
        assert str(Block([]))=='{}'

    def testBlock1(self):
        assert str(Block([Assign(Var(S('x')),Literal(9))]))=='{x=9}'

    def testBlock2(self):
        assert str(Block([
                    Assign(Var(S('x')),Literal(9)),
                    Assign(Var(S('z')),Literal(7))]))=='{x=9; z=7}'

suite=unittest.TestSuite(
    ( 
      unittest.makeSuite(StrTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

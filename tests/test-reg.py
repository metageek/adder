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

    def testBlock0(self):
        assert str(Block([]))=='{}'

    def testBlock1(self):
        assert str(Block([Assign(Var(S('x')),Literal(9))]))=='{x=9}'

    def testBlock2(self):
        assert str(Block([
                    Assign(Var(S('x')),Literal(9)),
                    Assign(Var(S('z')),Literal(7))]))=='{x=9; z=7}'

class ToPyleTestCase(unittest.TestCase):
    def testVar(self):
        assert Var(S('fred')).toPyle()==S('fred')

    def testLiteralInt(self):
        assert Literal(9).toPyle()==9

    def testLiteralSym(self):
        assert Literal(S('fred')).toPyle()==[S('quote'),[S('fred')]]

    def testCall0(self):
        assert Call(Var(S('fred')),Var(S('barney')),
                        [],[]).toPyle()==[S(':='),
                                          [S('fred'),
                                           [S('barney'),[],[]]
                                           ]
                                          ]

    def testCall1Pos(self):
        assert Call(Var(S('fred')),Var(S('barney')),
                        [Var(S('wilma'))],[]).toPyle()==[
            S(':='),
            [S('fred'),
             [S('barney'),[S('wilma')],[]]
             ]
            ]
        assert Call(Var(S('fred')),Var(S('barney')),
                        [Literal(9)],[]).toPyle()==[
            S(':='),
            [S('fred'),
             [S('barney'),[9],[]]
             ]
            ]

    def testCall1Kw(self):
        assert Call(Var(S('fred')),Var(S('barney')),
                        [],[(Var(S('wilma')),Var(S('betty')))]
                        ).toPyle()==[
            S(':='),
            [S('fred'),
             [S('barney'),[],[['wilma',S('betty')]]]
             ]
            ]
        assert Call(Var(S('fred')),Var(S('barney')),
                        [],[(Var(S('wilma')),Literal(9))]
                        ).toPyle()==[
            S(':='),
            [S('fred'),
             [S('barney'),[],[['wilma',9]]]
             ]
            ]

    def testCall1Pos1Kw(self):
        assert Call(Var(S('fred')),Var(S('barney')),
                        [Var(S('dino'))],
                        [(Var(S('wilma')),Var(S('betty')))]
                        ).toPyle()==[
            S(':='),
            [S('fred'),
             [S('barney'),[S('dino')],[['wilma',S('betty')]]]
             ]
            ]

    def testCall2Pos1Kw(self):
        assert Call(Var(S('fred')),Var(S('barney')),
                        [Var(S('dino')),Literal(9)],
                        [(Var(S('wilma')),Var(S('betty')))]
                        ).toPyle()==[
            S(':='),
            [S('fred'),
             [S('barney'),[S('dino'),9],[['wilma',S('betty')]]]
             ]
            ]

    def testCall2Pos2Kw(self):
        assert Call(Var(S('fred')),Var(S('barney')),
                        [Var(S('dino')),Literal(9)],
                        [(Var(S('wilma')),Var(S('betty'))),
                         (Var(S('pebbles')),Literal(3))]
                        ).toPyle()==[
            S(':='),
            [S('fred'),
             [S('barney'),[S('dino'),9],[['wilma',S('betty')],['pebbles',3]]]
             ]
            ]

    def testAssign(self):
        assert Assign(Var(S('fred')),Var(S('barney'))).toPyle()==[
            S(':='),[S('fred'),S('barney')]
            ]
        assert Assign(Var(S('fred')),Literal(7)).toPyle()==[
            S(':='),[S('fred'),7]
            ]

    def testReturn(self):
        assert Return(Var(S('fred'))).toPyle()==[S('return'),[S('fred')]]
        assert Return(Literal(7)).toPyle()==[S('return'),[7]]

    def testYield(self):
        assert Yield(Var(S('fred'))).toPyle()==[S('yield'),[S('fred')]]
        assert Yield(Literal(7)).toPyle()==[S('yield'),[7]]

    def testRaise(self):
        assert Raise(Var(S('fred'))).toPyle()==[S('raise'),[S('fred')]]

    def testReraise(self):
        assert Reraise().toPyle()==[S('raise'),[]]

    def testTry(self):
        assert Try(Return(Literal(7)),
                   [(Var(S('TypeError')),Var(S('te')),
                     Return(Literal(12))),
                    (Var(S('ValueError')),Var(S('ve')),
                     Reraise())],
                   Assign(Var(S('x')),Literal(3))).toPyle()==[
            S('try'),
            [[S('return'),[7]]],
            [['TypeError',S('te'),[S('return'),[12]]],
             ['ValueError',S('ve'),[S('raise'),[]]],
             ['finally',None,[S(':='),[S('x'),3]]]
             ]
            ]

    def testIf(self):
        assert If(Var(S('x')),
                      Return(Literal(9)),
                      None).toPyle()==[S('if-stmt'),
                                       [S('x'),
                                        [S('return'),[9]]]
                                       ]
        assert If(Literal(True),
                      Return(Literal(9)),
                      None).toPyle()==[S('if-stmt'),
                                       [True,
                                        [S('return'),[9]]]
                                       ]

    def testIfElse(self):
        assert If(Var(S('x')),
                      Return(Literal(9)),
                      Return(Literal(3))).toPyle()==[S('if-stmt'),
                                                     [S('x'),
                                                      [S('return'),[9]],
                                                      [S('return'),[3]]]
                                                     ]
        assert If(Literal(True),
                      Return(Literal(9)),
                      Return(Literal(3))).toPyle()==[S('if-stmt'),
                                                     [True,
                                                      [S('return'),[9]],
                                                      [S('return'),[3]]]
                                                     ]

    def testWhile(self):
        assert While(Var(S('x')),
                     Return(Literal(9))).toPyle()==[
            S('while'),
            [S('x'),
             [S('return'),[9]]
             ]
            ]
        assert While(Literal(True),
                     Return(Literal(9))).toPyle()==[
            S('while'),
            [True,
             [S('return'),[9]]
             ]
            ]

    def testDef0(self):
        assert Def(Var(S('g')),[],[],
                   [],[],
                   Return(Literal(9))).toPyle()==[
            S('def'),
            [S('g'),
             [],
             [S('return'),[9]]
             ]
            ]

    def testDef1Pos(self):
        assert Def(Var(S('g')),[Var(S('x'))],[],
                   [],[],
                   Return(Literal(9))).toPyle()==[
            S('def'),
            [S('g'),
             [S('x')],
             [S('return'),[9]]
             ]
            ]

    def testDef1Kw(self):
        assert Def(Var(S('g')),[],[Var(S('x'))],
                   [],[],
                   Return(Literal(9))).toPyle()==[
            S('def'),
            [S('g'),
             [S('&key'),S('x')],
             [S('return'),[9]]
             ]
            ]

    def testDef1Pos1Kw(self):
        assert Def(Var(S('g')),[Var(S('x'))],[Var(S('y'))],
                   [],[],
                   Return(Literal(9))).toPyle()==[
            S('def'),
            [S('g'),
             [S('x'),S('&key'),S('y')],
             [S('return'),[9]]
             ]
            ]

    def testDef2Pos1Kw(self):
        assert Def(Var(S('g')),[Var(S('x')),Var(S('y'))],
                   [Var(S('z'))],
                   [],[],
                   Return(Literal(9))).toPyle()==[
            S('def'),
            [S('g'),
             [S('x'),S('y'),S('&key'),S('z')],
             [S('return'),[9]]
             ]
            ]

    def testDef2Pos2Kw(self):
        assert Def(Var(S('g')),[Var(S('x')),Var(S('y'))],
                   [Var(S('a')),Var(S('b'))],
                   [],[],
                   Return(Literal(9))).toPyle()==[
            S('def'),
            [S('g'),
             [S('x'),S('y'),S('&key'),S('a'),S('b')],
             [S('return'),[9]]
             ]
            ]

    def testBreak(self):
        assert Break().toPyle()==[S('break'),[]]

    def testContinue(self):
        assert Continue().toPyle()==[S('continue'),[]]

    def testPass(self):
        assert Pass().toPyle()==[S('begin'),[]]

    def testBlock0(self):
        assert Block([]).toPyle()==[
            S('begin'),
            []
            ]

    def testBlock1(self):
        assert Block([Assign(Var(S('x')),Literal(9))]).toPyle()==[
            S('begin'),
            [
                [S(':='),[S('x'),9]]
                ]
            ]

    def testBlock2(self):
        assert Block([
                    Assign(Var(S('x')),Literal(9)),
                    Assign(Var(S('z')),Literal(7))]).toPyle()==[
            S('begin'),
            [
                [S(':='),[S('x'),9]],
                [S(':='),[S('z'),7]]
                ]
            ]

class ToPythonTestCase(unittest.TestCase):
    def setUp(self):
        self.verbose=False

    def tearDown(self):
        self.verbose=False

    def toPython(self,g2,isStmt=True):
        build=adder.pyle.buildStmt if isStmt else adder.pyle.buildExpr
        pyle=g2.toPyle()
        if isStmt:
            pyleAST=adder.pyle.buildStmt(pyle)
            pythonTree=pyleAST.toPythonTree()
            pythonFlat=adder.pyle.flatten(pythonTree)
            if self.verbose:
                print(pyle)
                print(pythonTree)
                print('{%s}' % pythonFlat)
            return pythonFlat
        else:
            pyleAST=adder.pyle.buildExpr(pyle)
            pythonExpr=pyleAST.toPython(False)
            if self.verbose:
                print('{%s}' % pythonExpr)
            return pythonExpr

    def testVar(self):
        assert self.toPython(Var(S('fred')),False)=='fred'

    def testLiteralInt(self):
        assert self.toPython(Literal(9),False)=='9'

    def testLiteralSym(self):
        assert self.toPython(Literal(S('fred')))=="adder.common.Symbol('fred')\n"

    def testCall0(self):
        assert self.toPython(Call(Var(S('fred')),Var(S('barney')),
                        [],[]))=="fred=barney()\n"

    def testCall1Pos(self):
        assert self.toPython(Call(Var(S('fred')),Var(S('barney')),
                        [Var(S('wilma'))],[]))=="fred=barney(wilma)\n"
        assert self.toPython(Call(Var(S('fred')),Var(S('barney')),
                        [Literal(9)],[]))=="fred=barney(9)\n"

    def testCall1Kw(self):
        assert self.toPython(Call(Var(S('fred')),Var(S('barney')),
                        [],[(Var(S('wilma')),Var(S('betty')))]
                        ))=="fred=barney(wilma=betty)\n"
        assert self.toPython(Call(Var(S('fred')),Var(S('barney')),
                        [],[(Var(S('wilma')),Literal(9))]
                        ))=="fred=barney(wilma=9)\n"

    def testCall1Pos1Kw(self):
        assert self.toPython(Call(Var(S('fred')),Var(S('barney')),
                        [Var(S('dino'))],
                        [(Var(S('wilma')),Var(S('betty')))]
                        ))=="fred=barney(dino, wilma=betty)\n"

    def testCall2Pos1Kw(self):
        assert self.toPython(Call(Var(S('fred')),Var(S('barney')),
                        [Var(S('dino')),Literal(9)],
                        [(Var(S('wilma')),Var(S('betty')))]
                        ))=="fred=barney(dino, 9, wilma=betty)\n"

    def testCall2Pos2Kw(self):
        assert self.toPython(Call(Var(S('fred')),Var(S('barney')),
                        [Var(S('dino')),Literal(9)],
                        [(Var(S('wilma')),Var(S('betty'))),
                         (Var(S('pebbles')),Literal(3))]
                        ))=="fred=barney(dino, 9, pebbles=3, wilma=betty)\n"

    def testAssign(self):
        assert self.toPython(Assign(Var(S('fred')),Var(S('barney'))))=="fred=barney\n"
        assert self.toPython(Assign(Var(S('fred')),Literal(7)))=="fred=7\n"

    def testReturn(self):
        assert self.toPython(Return(Var(S('fred'))))=='return fred\n'
        assert self.toPython(Return(Literal(7)))=='return 7\n'

    def testYield(self):
        assert self.toPython(Yield(Var(S('fred'))))=='yield fred\n'
        assert self.toPython(Yield(Literal(7)))=='yield 7\n'

    def testRaise(self):
        assert self.toPython(Raise(Var(S('fred'))))=='raise fred\n'

    def testReraise(self):
        assert self.toPython(Reraise())=='raise\n'

    def testTry(self):
        assert self.toPython(Try(Return(Literal(7)),
                   [(Var(S('TypeError')),Var(S('te')),
                     Return(Literal(12))),
                    (Var(S('ValueError')),Var(S('ve')),
                     Reraise())],
                   Assign(Var(S('x')),Literal(3))))=="""try:
    return 7
except TypeError as te:
    return 12
except ValueError as ve:
    raise
finally:
    x=3
"""

    def testIf(self):
        assert self.toPython(If(Var(S('x')),
                      Return(Literal(9)),
                      None))=="""if x:
    return 9
"""
        assert self.toPython(If(Literal(True),
                      Return(Literal(9)),
                      None))=="""if True:
    return 9
"""

    def testIfElse(self):
        assert self.toPython(If(Var(S('x')),
                      Return(Literal(9)),
                      Return(Literal(3))))=="""if x:
    return 9
else:
    return 3
"""

        assert self.toPython(If(Literal(True),
                      Return(Literal(9)),
                      Return(Literal(3))))=="""if True:
    return 9
else:
    return 3
"""

    def testWhile(self):
        assert self.toPython(While(Var(S('x')),
                     Return(Literal(9))))=="""while x:
    return 9
"""

        assert self.toPython(While(Literal(True),
                     Return(Literal(9))))=="""while True:
    return 9
"""

    def testDef0(self):
        assert self.toPython(Def(Var(S('g')),[],[],
                   [],[],
                   Return(Literal(9))))=="""def g():
    return 9
"""

    def testDef1Pos(self):
        assert self.toPython(Def(Var(S('g')),[Var(S('x'))],[],
                   [],[],
                   Return(Literal(9))))=="""def g(x):
    return 9
"""

    def testDef1Kw(self):
        assert self.toPython(Def(Var(S('g')),[],[Var(S('x'))],
                   [],[],
                   Return(Literal(9))))=="""def g(*,x):
    return 9
"""

    def testDef1Pos1Kw(self):
        assert self.toPython(Def(Var(S('g')),[Var(S('x'))],[Var(S('y'))],
                   [],[],
                   Return(Literal(9))))=="""def g(x,*,y):
    return 9
"""

    def testDef2Pos1Kw(self):
        assert self.toPython(Def(Var(S('g')),[Var(S('x')),Var(S('y'))],
                   [Var(S('z'))],
                   [],[],
                   Return(Literal(9))))=="""def g(x,y,*,z):
    return 9
"""

    def testDef2Pos2Kw(self):
        assert self.toPython(Def(Var(S('g')),[Var(S('x')),Var(S('y'))],
                   [Var(S('a')),Var(S('b'))],
                   [],[],
                   Return(Literal(9))))=="""def g(x,y,*,a,b):
    return 9
"""

    def testBreak(self):
        assert self.toPython(Break())=='break\n'

    def testContinue(self):
        assert self.toPython(Continue())=='continue\n'

    def testPass(self):
        assert self.toPython(Pass())=='assert True\n'

    def testBlock0(self):
        assert self.toPython(Block([]))=="assert True\n"

    def testBlock1(self):
        assert self.toPython(Block([Assign(Var(S('x')),Literal(9))]))=="""x=9
"""

    def testBlock2(self):
        assert self.toPython(Block([
                    Assign(Var(S('x')),Literal(9)),
                    Assign(Var(S('z')),Literal(7))]))=="""x=9
z=7
"""

suite=unittest.TestSuite(
    ( 
      unittest.makeSuite(StrTestCase,'test'),
      unittest.makeSuite(ToPyleTestCase,'test'),
      unittest.makeSuite(ToPythonTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

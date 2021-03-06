#!/usr/bin/env python3

import unittest,pdb,sys,os
from adder.pyle import *
from adder.common import Symbol as S, mkScratch
import adder.common

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

    def testAssignVar(self):
        assert str(Assign(Var(S('fred')),Var(S('barney'))))=='fred=barney'
        assert str(Assign(Var(S('fred')),Literal(7)))=='fred=7'

    def testAssignDot(self):
        assert str(Assign(Dot(Var(S('fred')),
                              [Var(S('x')),Var(S('y'))]),
                          Var(S('barney'))))=='fred.x.y=barney'

    def testAssignSubscript(self):
        assert str(Assign(Subscript(Var(S('fred')),
                                    Literal(3)),
                          Var(S('barney'))))=='fred[3]=barney'

    def testReturn(self):
        assert str(Return(Var(S('fred'))))=='return fred'
        assert str(Return(Literal(7)))=='return 7'
        assert str(Return())=='return'

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
        assert str(Def(Var(S('g')),[],[],[],
                       [],[],[],
                       Return(Literal(9))))=='{def g() return 9}'

    def testDef1Pos(self):
        assert str(Def(Var(S('g')),[Var(S('x'))],[],[],
                       [],[],[],
                       Return(Literal(9))))=='{def g(x) return 9}'

    def testDef1Pos1Opt(self):
        assert str(Def(Var(S('g')),[Var(S('x'))],[(Var(S('y')),None)],[],
                       [],[],[],
                       Return(Literal(9))))=='{def g(x,y=None) return 9}'

    def testDef1Pos1OptD(self):
        assert str(Def(Var(S('g')),[Var(S('x'))],[(Var(S('y')),Literal(12))],[],
                       [],[],[],
                       Return(Literal(9))))=='{def g(x,y=12) return 9}'

    def testDef1Kw(self):
        assert str(Def(Var(S('g')),[],[],[Var(S('x'))],
                       [],[],[],
                       Return(Literal(9))))=='{def g(*,x=None) return 9}'

    def testDef1Pos1Kw(self):
        assert str(Def(Var(S('g')),[Var(S('x'))],[],[Var(S('y'))],
                       [],[],[],
                       Return(Literal(9))))=='{def g(x,*,y=None) return 9}'

    def testDef2Pos1Kw(self):
        assert str(Def(Var(S('g')),[Var(S('x')),Var(S('y'))],[],
                       [Var(S('z'))],
                       [],[],[],
                       Return(Literal(9)))
                   )=='{def g(x,y,*,z=None) return 9}'

    def testDef2Pos2Kw(self):
        assert str(Def(Var(S('g')),[Var(S('x')),Var(S('y'))],[],
                       [Var(S('a')),Var(S('b'))],
                       [],[],[],
                       Return(Literal(9)))
                   )=='{def g(x,y,*,a=None,b=None) return 9}'

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
    def toP(self,il,*,v=False):
        tree=il.toPythonTree()
        flat=flatten(tree)
        if v:
            print()
            print(tree)
            print(flat)
        return (tree,flat)

    def testVar(self):
        assert Var(S('fred')).toPythonTree()=='fred'

    def testLiteralInt(self):
        assert Literal(9).toPythonTree()=='9'

    def testLiteralSym(self):
        assert Literal(S('fred')).toPythonTree()=="adder.common.Symbol('fred')"

    def testQuoteList(self):
        t=Quote(List([Literal(S('fred')),
                      Literal(5),
                      List([Literal(S('barney'))])
                      ]
                     )
                ).toPythonTree()
        assert t=="[adder.common.Symbol('fred'), 5, [adder.common.Symbol('barney')]]"

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

    def testAssignRLiteral(self):
        assert self.toP(Assign(Var(S('fred')),
                               Literal(7)))==("fred=7","fred=7\n")

    def testAssignLDotRLiteral(self):
        assert self.toP(Assign(Dot(Var(S('fred')),
                                   [Var(S('x')),Var(S('y'))]),
                               Literal(7)))==("fred.x.y=7","fred.x.y=7\n")

    def testAssignLSubscriptRLiteral(self):
        assert self.toP(Assign(Subscript(Var(S('fred')),Literal(3)),
                               Literal(7)))==("fred[3]=7","fred[3]=7\n")

    def testAssignRVar(self):
        assert self.toP(Assign(Var(S('fred')),
                               Var(S('x'))))==("fred=x","fred=x\n")

    def testAssignRCall(self):
        assert self.toP(Assign(Var(S('fred')),
                               Call(Var(S('barney')),
                                    [Literal(3)],[])))==("fred=barney(3)",
                                                         "fred=barney(3)\n")

    def testReturn(self):
        assert self.toP(Return(Literal(7)))==("return 7","return 7\n")

    def testReturnBlank(self):
        assert self.toP(Return())==("return","return\n")

    def testYield(self):
        assert self.toP(Yield(Literal(7)))==("yield 7","yield 7\n")

    def testTry1Exn(self):
        assert self.toP(Try(Call(Var(S('f')),[],[]),
                            [(Var(S('Exception')),
                              Var(S('e')),
                              Call(Var(S('print')),[Var(S('e'))],[]))],
                            None))==(
            ("try:",
             ["f()"],
             "except Exception as e:",
             ["print(e)"]
             ),
            """try:
    f()
except Exception as e:
    print(e)
""")

    def testTry2Exn(self):
        assert self.toP(Try(Call(Var(S('f')),[],[]),
                            [(Var(S('ValueError')),
                              Var(S('v')),
                              Call(Var(S('f')),[Var(S('v'))],[])),
                             (Var(S('Exception')),
                              Var(S('e')),
                              Call(Var(S('print')),[Var(S('e'))],[])),
                             ],
                            None))==(
            ("try:",
             ["f()"],
             "except ValueError as v:",
             ["f(v)"],
             "except Exception as e:",
             ["print(e)"]
             ),
            """try:
    f()
except ValueError as v:
    f(v)
except Exception as e:
    print(e)
""")

    def testTry0ExnFinally(self):
        assert self.toP(Try(Call(Var(S('f')),[],[]),
                            [],
                            Call(Var(S('g')),[],[])
                            ))==(
            ("try:",
             ["f()"],
             "finally:",
             ["g()"]
             ),
            """try:
    f()
finally:
    g()
""")

    def testTry1ExnFinally(self):
        assert self.toP(Try(Call(Var(S('f')),[],[]),
                            [(Var(S('ValueError')),
                              Var(S('v')),
                              Call(Var(S('f')),[Var(S('v'))],[])),
                             ],
                            Call(Var(S('g')),[],[])
                            ))==(
            ("try:",
             ["f()"],
             "except ValueError as v:",
             ["f(v)"],
             "finally:",
             ["g()"]
             ),
            """try:
    f()
except ValueError as v:
    f(v)
finally:
    g()
""")

    def testTry2ExnFinally(self):
        assert self.toP(Try(Call(Var(S('f')),[],[]),
                            [(Var(S('ValueError')),
                              Var(S('v')),
                              Call(Var(S('f')),[Var(S('v'))],[])),
                             (Var(S('Exception')),
                              Var(S('e')),
                              Call(Var(S('print')),[Var(S('e'))],[])),
                             ],
                            Call(Var(S('g')),[],[])
                            ))==(
            ("try:",
             ["f()"],
             "except ValueError as v:",
             ["f(v)"],
             "except Exception as e:",
             ["print(e)"],
             "finally:",
             ["g()"]
             ),
            """try:
    f()
except ValueError as v:
    f(v)
except Exception as e:
    print(e)
finally:
    g()
""")

    def testRaise(self):
        assert self.toP(Raise(Var(S('x'))))==("raise x","raise x\n")

    def testReraise(self):
        assert self.toP(Reraise())==("raise","raise\n")

    def testBinop(self):
        assert Binop(Var(S('*')),
                     Literal(9),
                     Literal(7)).toPythonTree()=="9*7"

    def testMkList(self):
        assert MkList([Literal(9),
                       Literal(7)]).toPythonTree()=="[9, 7]"

    def testMkTuple(self):
        assert MkTuple([Literal(9),
                        Literal(7)]).toPythonTree()=="(9, 7)"

    def testMkSet0(self):
        assert MkSet([]).toPythonTree()=="set()"


    def testMkSet1(self):
        assert MkSet([Literal(9)]).toPythonTree()=="{9}"

    def testMkSet2(self):
        assert MkSet([Literal(9),
                      Literal(7)]).toPythonTree()=="{9, 7}"

    def testMkDict(self):
        assert MkDict([[Var(S('x')),Literal(9)],
                       [Var(S('y')),Literal(7)]
                       ]).toPythonTree()=="{'x': 9, 'y': 7}"

    def testDot(self):
        assert Dot(Var(S('x')),
                   [Var(S('y')),
                    Var(S('z'))]).toPythonTree()=="x.y.z"

    def testSubscript(self):
        assert Subscript(Var(S('x')),Var(S('y'))).toPythonTree()=="x[y]"

    def testSliceLR(self):
        assert Slice(Var(S('x')),
                     Var(S('y')),
                     Var(S('z'))).toPythonTree()=="x[y:z]"

    def testIf(self):
        assert self.toP(If(Var(S('c')),
                           Call(Var(S('print')),[Var(S('c'))],[]),
                           None))==(("if c:",["print(c)"]),
                                    """if c:
    print(c)
""")

    def testIfElse(self):
        assert self.toP(If(Var(S('c')),
                           Call(Var(S('print')),[Var(S('c'))],[]),
                           Call(Var(S('f')),[Var(S('q'))],[])
                           ))==(("if c:",
                                 ["print(c)"],
                                 "else:",
                                 ["f(q)"]
                                 ),
                                    """if c:
    print(c)
else:
    f(q)
""")

    def testWhile(self):
        assert self.toP(While(Var(S('c')),
                              Call(Var(S('print')),[Var(S('c'))],[])
                              ))==(("while c:",["print(c)"]),
                                   """while c:
    print(c)
""")

    def testDef0(self):
        assert self.toP(Def(Var(S('f')),
                            [],[],
                            [],[],[],[],
                            Return(Literal(9))))==(("def f():",["return 9"]),
                                                    """def f():
    return 9
""")

    def testDef1Pos(self):
        assert self.toP(Def(Var(S('f')),
                            [Var(S('x'))],[],
                            [],[],[],[],
                            Return(Var(S('x')))))==(("def f(x):",["return x"]),
                                                    """def f(x):
    return x
""")

    def testDef2Pos(self):
        assert self.toP(Def(Var(S('f')),
                            [Var(S('x')),Var(S('y'))],[],
                            [],[],[],[],
                            Return(Var(S('x')))))==(("def f(x,y):",["return x"]),
                                                    """def f(x,y):
    return x
""")

    def testDef2Pos1Kw(self):
        assert self.toP(Def(Var(S('f')),
                            [Var(S('x')),Var(S('y'))],[],
                            [Var(S('z'))],[],[],[],
                            Return(Var(S('x')))))==(
            ("def f(x,y,*,z=None):",["return x"]),
            """def f(x,y,*,z=None):
    return x
""")

    def testDef2Pos2Kw(self):
        assert self.toP(Def(Var(S('f')),
                            [Var(S('x')),Var(S('y'))],[],
                            [Var(S('z')),Var(S('a'))],[],[],[],
                            Return(Var(S('x')))))==(
            ("def f(x,y,*,z=None,a=None):",["return x"]),
            """def f(x,y,*,z=None,a=None):
    return x
""")

    def testDef0Pos2Kw(self):
        assert self.toP(Def(Var(S('f')),
                            [],[],
                            [Var(S('z')),Var(S('a'))],[],[],[],
                            Return(Var(S('z'))))
                        )==(("def f(*,z=None,a=None):",["return z"]),
                            """def f(*,z=None,a=None):
    return z
""")

    def testDef1Pos2Kw(self):
        assert self.toP(Def(Var(S('f')),
                            [Var(S('x'))],[],
                            [Var(S('z')),Var(S('a'))],[],[],[],
                            Return(Var(S('x')))))==(
            ("def f(x,*,z=None,a=None):",["return x"]),
            """def f(x,*,z=None,a=None):
    return x
""")

    def testDef1Pos2Kw2Globals(self):
        assert self.toP(Def(Var(S('f')),
                            [Var(S('x'))],[],
                            [Var(S('z')),Var(S('a'))],
                            [],
                            [Var(S('g1')),Var(S('g2'))],
                            [],
                            Return(Var(S('x')))))==(
            ("def f(x,*,z=None,a=None):",
             ["global g1,g2",
              "return x"
              ]),
            """def f(x,*,z=None,a=None):
    global g1,g2
    return x
""")

    def testDef1Pos2Kw2Nonlocals(self):
        assert self.toP(Def(Var(S('f')),
                            [Var(S('x'))],[],
                            [Var(S('z')),Var(S('a'))],
                            [],[],
                            [Var(S('nl1')),Var(S('nl2'))],
                            Return(Var(S('x'))))
                        )==(("def f(x,*,z=None,a=None):",
                             ["nonlocal nl1,nl2",
                              "return x"
                              ]),
                            """def f(x,*,z=None,a=None):
    nonlocal nl1,nl2
    return x
""")

    def testDef1Pos2Kw2Globals2Nonlocals(self):
        assert self.toP(Def(Var(S('f')),
                            [Var(S('x'))],[],
                            [Var(S('z')),Var(S('a'))],
                            [],
                            [Var(S('g1')),Var(S('g2'))],
                            [Var(S('nl1')),Var(S('nl2'))],
                            Return(Var(S('x'))))
                        )==(("def f(x,*,z=None,a=None):",
                             ["global g1,g2",
                              "nonlocal nl1,nl2",
                              "return x"
                              ]),
                            """def f(x,*,z=None,a=None):
    global g1,g2
    nonlocal nl1,nl2
    return x
""")

    def testClassTopEmpty(self):
        assert self.toP(Class(Var(S('C')),[],[]))==(
            ("class C:",["pass"]),
            """class C:
    pass
""")

    def testClass1BaseEmpty(self):
        assert self.toP(Class(Var(S('C')),
                              [Var(S('Base'))],
                              []))==(
            ("class C(Base):",["pass"]),
            """class C(Base):
    pass
""")

    def testClass2BaseEmpty(self):
        assert self.toP(Class(Var(S('C')),
                              [Var(S('Base1')),Var(S('Base2'))],
                              []))==(
            ("class C(Base1,Base2):",["pass"]),
            """class C(Base1,Base2):
    pass
""")

    def testClass2BaseFunc(self):
        assert self.toP(Class(Var(S('C')),
                              [Var(S('Base1')),Var(S('Base2'))],
                              [Def(Var(S('__init__')),
                                   [Var(S('self'))],[],
                                   [],[],[],[],
                                   Assign(Dot(Var(S('self')),
                                              [Var(S('x'))]),
                                          Literal(9)))
                               ]))==(
            ("class C(Base1,Base2):",
             [("def __init__(self):",
               ["self.x=9"])
              ]
             ),
            """class C(Base1,Base2):
    def __init__(self):
        self.x=9
""")

    def testClass2BaseFuncStatic(self):
        assert self.toP(Class(Var(S('C')),
                              [Var(S('Base1')),Var(S('Base2'))],
                              [Assign(Var(S('y')),
                                      Literal(7)),
                               Def(Var(S('__init__')),
                                   [Var(S('self'))],[],
                                   [],[],[],[],
                                   Assign(Dot(Var(S('self')),
                                              [Var(S('x'))]),
                                          Literal(9))
                                   )
                               ]))==(
            ("class C(Base1,Base2):",
             ["y=7",
              ("def __init__(self):",
               ["self.x=9"])
              ]
             ),
            """class C(Base1,Base2):
    y=7
    def __init__(self):
        self.x=9
""")

    def testBreak(self):
        assert self.toP(Break())==("break","break\n")

    def testContinue(self):
        assert self.toP(Continue())==("continue","continue\n")

    def testPass(self):
        assert self.toP(Pass())==("pass","pass\n")

    def testBegin0(self):
        assert self.toP(Begin([]))==("pass","pass\n")

    def testBegin1(self):
        assert self.toP(Begin([Call(Var(S('f')),
                                    [Literal(9)],
                                    [])]))==("f(9)","f(9)\n")

    def testBegin2(self):
        assert self.toP(Begin([Assign(Var(S('x')),Literal(9)),
                               Call(Var(S('f')),
                                    [Var(S('x'))],
                                    [])]))==(("x=9","f(x)"),
                                             """x=9
f(x)
""")

    def testBegin4(self):
        assert self.toP(Begin([Assign(Var(S('x')),Literal(9)),
                               Assign(Var(S('y')),Literal(7)),
                               Assign(Var(S('z')),
                                      Binop(Var(S('*')),
                                            Var(S('x')),
                                            Var(S('y')))),
                               Call(Var(S('print')),
                                    [Var(S('z'))],
                                    [])]))==(("x=9","y=7","z=x*y","print(z)"),
                                             """x=9
y=7
z=x*y
print(z)
""")

    def testImport(self):
        assert self.toP(Import(Var(S('re'))))==("import re","import re\n")

class BuildToPythonTestCase(unittest.TestCase):
    def toP(self,pyle,*,v=False):
        il=build(pyle)
        tree=il.toPythonTree()
        flat=flatten(tree)
        if v:
            print()
            print(tree)
            print(flat)
        return (tree,flat)

    def testVar(self):
        assert build(S('fred')).toPythonTree()=='fred'

    def testLiteralInt(self):
        assert build(9).toPythonTree()=='9'

    def testLiteralSym(self):
        assert build([S('quote'),S('fred')]).toPythonTree()=="adder.common.Symbol('fred')"

    def testQuoteList(self):
        t=build([S('quote'),[S('fred'),5,[S('barney')]]]).toPythonTree()
        assert t=="[adder.common.Symbol('fred'), 5, [adder.common.Symbol('barney')]]"

    def testCall0(self):
        assert self.toP([S('call'),S('fred'),[],[]])==("fred()","fred()\n")

    def testCallVarargsPos(self):
        assert self.toP([S('call'),S('fred'),S('args'),
                         []])==("fred(*args)",
                                "fred(*args)\n")

    def testCallVarargsKw(self):
        assert self.toP([S('call'),S('fred'),[],S('args')]
                        )==("fred(**args)",
                            "fred(**args)\n")

    def testCallVarargsPosVarargsKw(self):
        assert self.toP([S('call'),S('fred'),S('posArgs'),S('kwArgs')]
                        )==("fred(*posArgs,**kwArgs)",
                            "fred(*posArgs,**kwArgs)\n")

    def testCall1Pos(self):
        assert self.toP([S('call'),S('fred'),
                         [S('x')],
                         []])==("fred(x)","fred(x)\n")

    def testCall2Pos(self):
        assert self.toP([S('call'),S('fred'),
                         [S('x'),S('y')],
                         []])==("fred(x,y)","fred(x,y)\n")

    def testCall1Kw(self):
        assert self.toP([S('call'),S('fred'),
                         [],
                         [[S('x'),9]]
                         ])==("fred(x=9)","fred(x=9)\n")

    def testCall2Kw(self):
        assert self.toP([S('call'),S('fred'),
                         [],
                         [[S('x'),9],[S('y'),7]]
                         ])==("fred(x=9,y=7)","fred(x=9,y=7)\n")

    def testCall2Pos1Kw(self):
        assert self.toP([S('call'),S('fred'),
                         [3,5],
                         [[S('x'),9]]
                         ])==("fred(3,5,x=9)","fred(3,5,x=9)\n")

    def testCall2Pos2Kw(self):
        assert self.toP([S('call'),S('fred'),
                         [3,5],
                         [[S('x'),9],[S('y'),7]]
                         ])==("fred(3,5,x=9,y=7)","fred(3,5,x=9,y=7)\n")

    def testAssignRLiteral(self):
        assert self.toP([S(':='),S('fred'),7])==("fred=7","fred=7\n")

    def testAssignLDotRLiteral(self):
        assert self.toP([S(':='),
                         [S('.'),S('fred'),S('x'),S('y')],
                         7])==("fred.x.y=7","fred.x.y=7\n")

    def testAssignLSubscriptRLiteral(self):
        assert self.toP([S(':='),
                         [S('[]'),S('fred'),3],
                         7])==("fred[3]=7","fred[3]=7\n")

    def testAssignRVar(self):
        assert self.toP([S(':='),S('fred'),S('x')])==("fred=x","fred=x\n")

    def testAssignRCall(self):
        assert self.toP([S(':='),S('fred'),
                         [S('call'),S('barney'),[3],[]]
                         ])==("fred=barney(3)",
                              "fred=barney(3)\n")

    def testReturn(self):
        assert self.toP([S('return'),7])==("return 7","return 7\n")

    def testReturnBlank(self):
        assert self.toP([S('return')])==("return","return\n")

    def testYield(self):
        assert self.toP([S('yield'),7])==("yield 7","yield 7\n")

    def testTry1Exn(self):
        assert self.toP([S('try'),
                         [S('call'),S('f'),[],[]],
                         [S(':Exception'),S('e'),
                          [S('call'),S('print'),[S('e')],[]]
                          ]
                         ])==(
            ("try:",
             ["f()"],
             "except Exception as e:",
             ["print(e)"]
             ),
            """try:
    f()
except Exception as e:
    print(e)
""")

    def testTry2Exn(self):
        assert self.toP([S('try'),
                         [S('call'),S('f'),[],[]],
                         [S(':ValueError'),S('v'),
                          [S('call'),S('f'),[S('v')],[]]
                          ],
                         [S(':Exception'),S('e'),
                          [S('call'),S('print'),[S('e')],[]]
                          ]
                         ])==(
            ("try:",
             ["f()"],
             "except ValueError as v:",
             ["f(v)"],
             "except Exception as e:",
             ["print(e)"]
             ),
            """try:
    f()
except ValueError as v:
    f(v)
except Exception as e:
    print(e)
""")

    def testTry0ExnFinally(self):
        assert self.toP([S('try'),
                         [S('call'),S('f'),[],[]],
                         [S(':finally'),
                          [S('call'),S('g'),[],[]
                           ]
                          ]
                         ])==(
            ("try:",
             ["f()"],
             "finally:",
             ["g()"]
             ),
            """try:
    f()
finally:
    g()
""")

    def testTry1ExnFinally(self):
        assert self.toP([S('try'),
                         [S('call'),S('f'),[],[]],
                         [S(':ValueError'),S('v'),
                          [S('call'),S('f'),[S('v')],[]]
                          ],
                         [S(':finally'),
                          [S('call'),S('g'),[],[]
                           ]
                          ]
                         ])==(
            ("try:",
             ["f()"],
             "except ValueError as v:",
             ["f(v)"],
             "finally:",
             ["g()"]
             ),
            """try:
    f()
except ValueError as v:
    f(v)
finally:
    g()
""")

    def testTry2ExnFinally(self):
        assert self.toP([S('try'),
                         [S('call'),S('f'),[],[]],
                         [S(':ValueError'),S('v'),
                          [S('call'),S('f'),[S('v')],[]]
                          ],
                         [S(':Exception'),S('e'),
                          [S('call'),S('print'),[S('e')],[]]
                          ],
                         [S(':finally'),
                          [S('call'),S('g'),[],[]
                           ]
                          ]
                         ])==(
            ("try:",
             ["f()"],
             "except ValueError as v:",
             ["f(v)"],
             "except Exception as e:",
             ["print(e)"],
             "finally:",
             ["g()"]
             ),
            """try:
    f()
except ValueError as v:
    f(v)
except Exception as e:
    print(e)
finally:
    g()
""")

    def testRaise(self):
        assert self.toP([S('raise'),S('x')])==("raise x","raise x\n")

    def testReraise(self):
        assert self.toP([S('reraise')])==("raise","raise\n")

    def testBinop(self):
        assert build([S('binop'),S('*'),9,7]).toPythonTree()=="9*7"

    def testMkList(self):
        assert build([S('mk-list'),9,7]).toPythonTree()=="[9, 7]"

    def testMkTuple(self):
        assert build([S('mk-tuple'),9,7]).toPythonTree()=="(9, 7)"

    def testMkSet0(self):
        assert build([S('mk-set')]).toPythonTree()=="set()"

    def testMkSet1(self):
        assert build([S('mk-set'),9]).toPythonTree()=="{9}"

    def testMkSet2(self):
        assert build([S('mk-set'),9,7]).toPythonTree()=="{9, 7}"

    def testMkDict(self):
        assert build([S('mk-dict'),[S('x'),9],[S('y'),7]]
                      ).toPythonTree()=="{'x': 9, 'y': 7}"

    def testDot(self):
        assert build([S('.'),
                      S('x'),
                      S('y'),
                      S('z')]).toPythonTree()=="x.y.z"

    def testSubscript(self):
        assert build([S('[]'),S('x'),S('y')]).toPythonTree()=="x[y]"

    def testSliceLR(self):
        assert build([S('slice'),S('x'),
                      S('y'),S('z')]).toPythonTree()=="x[y:z]"

    def testIf(self):
        assert self.toP([S('if'),
                         S('c'),
                         [S('call'),S('print'),[S('c')],[]]
                         ])==(("if c:",["print(c)"]),
                                    """if c:
    print(c)
""")

    def testIfElse(self):
        assert self.toP([S('if'),
                         S('c'),
                         [S('call'),S('print'),[S('c')],[]],
                         [S('call'),S('f'),[S('q')],[]]
                         ])==(("if c:",
                                 ["print(c)"],
                                 "else:",
                                 ["f(q)"]
                                 ),
                                    """if c:
    print(c)
else:
    f(q)
""")

    def testWhile(self):
        assert self.toP([S('while'),
                         S('c'),
                         [S('call'),S('print'),[S('c')],[]]
                         ])==(("while c:",["print(c)"]),
                                   """while c:
    print(c)
""")

    def testDef0(self):
        assert self.toP([S('def'),
                         S('f'),
                         [],
                         [S('return'),9]
                         ])==(("def f():",["return 9"]),
                              """def f():
    return 9
""")

    def testDef1Pos(self):
        assert self.toP([S('def'),
                         S('f'),
                         [S('x')],
                         [S('return'),S('x')]
                         ])==(("def f(x):",["return x"]),
                              """def f(x):
    return x
""")

    def testDef1PosRest(self):
        assert self.toP([S('def'),
                         S('f'),
                         [S('x'),S('&rest'),S('args')],
                         [S('return'),S('x')]
                         ])==(("def f(x,*args):",["return x"]),
                              """def f(x,*args):
    return x
""")

    def testDef2Pos(self):
        assert self.toP([S('def'),
                         S('f'),
                         [S('x'),S('y')],
                         [S('return'),S('x')]
                         ])==(("def f(x,y):",["return x"]),
                                                    """def f(x,y):
    return x
""")

    def testDef2Pos1Kw(self):
        assert self.toP([S('def'),
                         S('f'),
                         [S('x'),S('y'),S('&key'),S('z')],
                         [S('return'),S('x')]
                         ])==(("def f(x,y,*,z=None):",["return x"]),
                                                    """def f(x,y,*,z=None):
    return x
""")

    def testDef2Pos2Kw(self):
        assert self.toP([S('def'),
                         S('f'),
                         [S('x'),S('y'),S('&key'),S('z'),S('a')],
                         [S('return'),S('x')]
                         ])==(("def f(x,y,*,z=None,a=None):",["return x"]),
                              """def f(x,y,*,z=None,a=None):
    return x
""")

    def testDef0Pos2Kw(self):
        assert self.toP([S('def'),
                         S('f'),
                         [S('&key'),S('z'),S('a')],
                         [S('return'),S('z')]
                         ])==(("def f(*,z=None,a=None):",["return z"]),
                              """def f(*,z=None,a=None):
    return z
""")

    def testDef1Pos2Kw(self):
        assert self.toP([S('def'),
                         S('f'),
                         [S('x'),S('&key'),S('z'),S('a')],
                         [S('return'),S('x')]
                         ])==(("def f(x,*,z=None,a=None):",["return x"]),
                              """def f(x,*,z=None,a=None):
    return x
""")

    def testDef1Pos2Kw2Globals(self):
        assert self.toP([S('def'),
                         S('f'),
                         [S('x'),
                          S('&key'),S('z'),S('a'),
                          S('&global'),S('g1'),S('g2')
                          ],
                         [S('return'),S('x')]
                         ])==(("def f(x,*,z=None,a=None):",
                               ["global g1,g2",
                                "return x"
                                ]),
                              """def f(x,*,z=None,a=None):
    global g1,g2
    return x
""")

    def testDef1Pos2Kw2Nonlocals(self):
        assert self.toP([S('def'),
                         S('f'),
                         [S('x'),
                          S('&key'),S('z'),S('a'),
                          S('&nonlocal'),S('nl1'),S('nl2'),
                          ],
                         [S('return'),S('x')]
                         ])==(("def f(x,*,z=None,a=None):",
                               ["nonlocal nl1,nl2",
                                "return x"
                                ]),
                              """def f(x,*,z=None,a=None):
    nonlocal nl1,nl2
    return x
""")

    def testDef1Pos2Kw2Globals2Nonlocals(self):
        assert self.toP([S('def'),
                         S('f'),
                         [S('x'),
                          S('&key'),S('z'),S('a'),
                          S('&global'),S('g1'),S('g2'),
                          S('&nonlocal'),S('nl1'),S('nl2'),
                          ],
                         [S('return'),S('x')]
                         ])==(("def f(x,*,z=None,a=None):",
                               ["global g1,g2",
                                "nonlocal nl1,nl2",
                                "return x"
                                ]),
                              """def f(x,*,z=None,a=None):
    global g1,g2
    nonlocal nl1,nl2
    return x
""")

    def testClassTopEmpty(self):
        assert self.toP([S('class'),S('C'),[]])==(
            ("class C:",["pass"]),
            """class C:
    pass
""")

    def testClass1BaseEmpty(self):
        assert self.toP([S('class'),S('C'),[S('Base')]])==(
            ("class C(Base):",["pass"]),
            """class C(Base):
    pass
""")

    def testClass2BaseEmpty(self):
        assert self.toP([S('class'),S('C'),[S('Base1'),S('Base2')]])==(
            ("class C(Base1,Base2):",["pass"]),
            """class C(Base1,Base2):
    pass
""")

    def testClass2BaseFunc(self):
        assert self.toP([S('class'),S('C'),
                         [S('Base1'),S('Base2')],
                         [S('def'),S('__init__'),[S('self')],
                          [S(':='),[S('.'),S('self'),S('x')],9]
                          ]])==(
            ("class C(Base1,Base2):",
             [("def __init__(self):",
               ["self.x=9"])
              ]
             ),
            """class C(Base1,Base2):
    def __init__(self):
        self.x=9
""")

    def testClass2BaseFuncStatic(self):
        assert self.toP([S('class'),S('C'),
                         [S('Base1'),S('Base2')],
                         [S(':='),S('y'),7],
                         [S('def'),S('__init__'),[S('self')],
                          [S(':='),[S('.'),S('self'),S('x')],9]
                          ]])==(
            ("class C(Base1,Base2):",
             ["y=7",
              ("def __init__(self):",
               ["self.x=9"])
              ]
             ),
            """class C(Base1,Base2):
    y=7
    def __init__(self):
        self.x=9
""")

    def testBreak(self):
        assert self.toP([S('break')])==("break","break\n")

    def testContinue(self):
        assert self.toP([S('continue')])==("continue","continue\n")

    def testPass(self):
        assert self.toP([S('pass')])==("pass","pass\n")

    def testBegin0(self):
        assert self.toP([S('begin')])==("pass","pass\n")

    def testBegin1(self):
        assert self.toP([S('begin'),
                         [S('call'),S('f'),[9],[]]
                         ])==("f(9)","f(9)\n")

    def testBegin2(self):
        assert self.toP([S('begin'),
                         [S(':='),S('x'),9],
                         [S('call'),S('f'),[S('x')],[]]
                         ])==(("x=9","f(x)"),
                              """x=9
f(x)
""")

    def testBegin4(self):
        assert self.toP([S('begin'),
                         [S(':='),S('x'),9],
                         [S(':='),S('y'),7],
                         [S(':='),S('z'),
                          [S('binop'),S('*'),S('x'),S('y')]
                          ],
                         [S('call'),S('print'),[S('z')],[]]
                         ])==(("x=9","y=7","z=x*y","print(z)"),
                              """x=9
y=7
z=x*y
print(z)
""")

    def testImport(self):
        assert self.toP([S('import'),S('re')])==("import re","import re\n")

class TrimScratchesTestCase(unittest.TestCase):
    def tst(self,stmt,expected):
        actual=trimScratches(stmt)
        if expected is None:
            success=(actual is stmt)
        else:
            success=(actual==expected)
        if not success:
            print(stmt)
            print(actual)
            print(expected)
        assert success

    def testReturn(self):
        s1=mkScratch()
        self.tst([S('return'),s1],None)

    def testYield(self):
        s1=mkScratch()
        self.tst([S('yield'),s1],
                 [S('begin'),
                  [S('yield'),s1],
                  [S(':='),s1,None]])

    def testTry1(self):
        s1=mkScratch()
        self.tst([S('try'),
                  [S('call'),S('f'),[s1],[]],
                  [S(':finally'),[S('call'),S('g'),[],[]]]
                  ],
                 [S('begin'),
                  [S('try'),
                   [S('call'),S('f'),[s1],[]],
                   [S(':finally'),[S('call'),S('g'),[],[]]]
                   ],
                  [S(':='),s1,None]
                  ])

    def testTry2(self):
        s1=mkScratch()
        self.tst([S('try'),
                  [S('call'),S('f'),[s1],[]],
                  [S(':ValueError'),S('ve'),
                   [S('call'),S('h'),[s1,S('ve')],[]]],
                  [S(':finally'),[S('call'),[S('g')],[],[]]]
                  ],
                 [S('begin'),
                  [S('try'),
                   [S('call'),S('f'),[s1],[]],
                   [S(':ValueError'),S('ve'),
                    [S('call'),S('h'),[s1,S('ve')],[]]],
                   [S(':finally'),[S('call'),[S('g')],[],[]]]
                   ],
                  [S(':='),s1,None]
                  ])

    def testRaise(self):
        s1=mkScratch()
        self.tst([S('raise'),s1],None)

    def testIfNoElse(self):
        s1=mkScratch()
        self.tst([S('if'),S('foo'),
                  [S('call'),S('f'),[s1],[]]
                  ],
                 [S('if'),S('foo'),
                  [S('begin'),
                   [S('call'),S('f'),[s1],[]],
                   [S(':='),s1,None]]
                  ]
                 )

    def testIfWithElse1(self):
        s1=mkScratch()
        self.tst([S('if'),S('foo'),
                  [S('call'),S('f'),[s1],[]],
                  [S('call'),S('g'),[17,s1],[]]],
                 [S('begin'),
                  [S('if'),S('foo'),
                   [S('call'),S('f'),[s1],[]],
                   [S('call'),S('g'),[17,s1],[]]],
                  [S(':='),s1,None]]
                 )

    def testIfWithElse2(self):
        s1=mkScratch()
        self.tst([S('if'),S('foo'),
                  [S('call'),S('f'),[9],[]],
                  [S('call'),S('g'),[17,s1],[]]],
                 [S('if'),S('foo'),
                  [S('begin'),
                   [S(':='),s1,None],
                   [S('call'),S('f'),[9],[]]],
                  [S('begin'),
                   [S('call'),S('g'),[17,s1],[]],
                   [S(':='),s1,None]]
                  ]
                 )

    def testIfWithElse3(self):
        s1=mkScratch()
        self.tst([S('if'),s1,
                  [S('call'),S('f'),[9],[]],
                  [S('call'),S('g'),[17,s1],[]]],
                 [S('if'),s1,
                  [S('begin'),
                   [S(':='),s1,None],
                   [S('call'),S('f'),[9],[]]],
                  [S('begin'),
                   [S('call'),S('g'),[17,s1],[]],
                   [S(':='),s1,None]]
                  ]
                 )

    def testWhile1(self):
        s1=mkScratch()
        self.tst([S('while'),s1,
                  [S('call'),S('f'),[9],[]]],
                 [S('begin'),
                  [S('while'),s1,
                   [S('call'),S('f'),[9],[]]],
                  [S(':='),s1,None]
                  ]
                 )

    def testWhile2(self):
        s1=mkScratch()
        self.tst([S('while'),S('foo'),
                  [S('call'),S('f'),[s1],[]]],
                 [S('begin'),
                  [S('while'),S('foo'),
                   [S('call'),S('f'),[s1],[]]],
                  [S(':='),s1,None]
                  ]
                 )

    def testBegin1(self):
        s1=mkScratch()
        self.tst([S('begin'),
                  [S('call'),S('f'),[s1],[]],
                  [S('call'),S('g'),[17,s1],[]]],
                 [S('begin'),
                  [S('call'),S('f'),[s1],[]],
                  [S('call'),S('g'),[17,s1],[]],
                  [S(':='),s1,None]
                  ]
                 )

    def testBegin2(self):
        s1=mkScratch()
        self.tst([S('begin'),
                  [S('call'),S('f'),[s1],[]],
                  [S('call'),S('g'),[17],[]]],
                 [S('begin'),
                  [S('call'),S('f'),[s1],[]],
                  [S(':='),s1,None],
                  [S('call'),S('g'),[17],[]]
                  ]
                 )

    def testAssignInt(self):
        s1=mkScratch()
        self.tst([S(':='),s1,7],
                 [S('begin'),
                  [S(':='),s1,7],
                  [S(':='),s1,None]
                  ]
                 )

    def testAssignOtherVar(self):
        s1=mkScratch()
        self.tst([S(':='),s1,S('foo')],
                 [S('begin'),
                  [S(':='),s1,S('foo')],
                  [S(':='),s1,None]
                  ]
                 )

    def testAssignScratchVar(self):
        s1=mkScratch()
        s2=mkScratch()
        self.tst([S(':='),S('foo'),s1],
                 [S('begin'),
                  [S(':='),S('foo'),s1],
                  [S(':='),s1,None]
                  ]
                 )

    def testAssignCall(self):
        s1=mkScratch()
        self.tst([S(':='),S('foo'),[S('call'),S('bar'),[s1],[]]],
                 [S('begin'),
                  [S(':='),S('foo'),[S('call'),S('bar'),[s1],[]]],
                  [S(':='),s1,None]
                  ]
                 )

    def testAssignBinop(self):
        s1=mkScratch()
        self.tst([S(':='),S('foo'),[S('binop'),S('<'),S('bar'),s1]],
                 [S('begin'),
                  [S(':='),S('foo'),[S('binop'),S('<'),S('bar'),s1]],
                  [S(':='),s1,None]
                  ]
                 )

    def testAssignDot1(self):
        s1=mkScratch()
        self.tst([S(':='),S('foo'),[S('.'),s1,S('bar')]],
                 [S('begin'),
                  [S(':='),S('foo'),[S('.'),s1,S('bar')]],
                  [S(':='),s1,None]
                  ]
                 )

    def testAssignDot2(self):
        s1=mkScratch()
        self.tst([S(':='),S('foo'),[S('.'),S('bar'),s1]],None)

    def testAssignSubscript1(self):
        s1=mkScratch()
        self.tst([S(':='),S('foo'),[S('[]'),s1,S('bar')]],
                 [S('begin'),
                  [S(':='),S('foo'),[S('[]'),s1,S('bar')]],
                  [S(':='),s1,None]
                  ]
                 )

    def testAssignSubscript2(self):
        s1=mkScratch()
        self.tst([S(':='),S('foo'),[S('[]'),S('bar'),s1]],
                 [S('begin'),
                  [S(':='),S('foo'),[S('[]'),S('bar'),s1]],
                  [S(':='),s1,None]
                  ]
                 )

    def testAssignSlice1(self):
        s1=mkScratch()
        self.tst([S(':='),S('foo'),[S('slice'),s1,S('bar')]],
                 [S('begin'),
                  [S(':='),S('foo'),[S('slice'),s1,S('bar')]],
                  [S(':='),s1,None]
                  ]
                 )

    def testAssignSlice2(self):
        s1=mkScratch()
        self.tst([S(':='),S('foo'),[S('slice'),S('bar'),s1]],
                 [S('begin'),
                  [S(':='),S('foo'),[S('slice'),S('bar'),s1]],
                  [S(':='),s1,None]
                  ]
                 )

    def testAssignSlice3(self):
        s1=mkScratch()
        self.tst([S(':='),S('foo'),[S('slice'),S('bar'),s1,7]],
                 [S('begin'),
                  [S(':='),S('foo'),[S('slice'),S('bar'),s1,7]],
                  [S(':='),s1,None]
                  ]
                 )

    def testAssignSlice4(self):
        s1=mkScratch()
        self.tst([S(':='),S('foo'),[S('slice'),S('bar'),7,s1]],
                 [S('begin'),
                  [S(':='),S('foo'),[S('slice'),S('bar'),7,s1]],
                  [S(':='),s1,None]
                  ]
                 )

    def testAssignSlice4(self):
        s1=mkScratch()
        s2=mkScratch()
        self.tst([S(':='),S('foo'),[S('slice'),S('bar'),s1,s2]],
                 [S('begin'),
                  [S(':='),S('foo'),[S('slice'),S('bar'),s1,s2]],
                  [S(':='),s2,None],
                  [S(':='),s1,None]
                  ]
                 )

    def testAssignQuote(self):
        s1=mkScratch()
        self.tst([S(':='),S('foo'),[S('quote'),s1]],None)

    def testAssignMkList(self):
        s1=mkScratch()
        self.tst([S(':='),S('foo'),[S('mk-list'),s1,17]],
                 [S('begin'),
                  [S(':='),S('foo'),[S('mk-list'),s1,17]],
                  [S(':='),s1,None]
                  ]
                 )

    def testAssignMkTuple(self):
        s1=mkScratch()
        self.tst([S(':='),S('foo'),[S('mk-tuple'),s1,17]],
                 [S('begin'),
                  [S(':='),S('foo'),[S('mk-tuple'),s1,17]],
                  [S(':='),s1,None]
                  ]
                 )

    def testAssignMkSet(self):
        s1=mkScratch()
        self.tst([S(':='),S('foo'),[S('mk-set'),s1,17]],
                 [S('begin'),
                  [S(':='),S('foo'),[S('mk-set'),s1,17]],
                  [S(':='),s1,None]
                  ]
                 )

    def testAssignMkDict(self):
        s1=mkScratch()
        self.tst([S(':='),S('foo'),[S('mk-dict'),[S('foo'),s1]]],
                 [S('begin'),
                  [S(':='),S('foo'),[S('mk-dict'),[S('foo'),s1]]],
                  [S(':='),s1,None]
                  ]
                 )

    def testCallWithArg(self):
        s1=mkScratch()
        self.tst([S('call'),S('foo'),[17,s1],[]],
                 [S('begin'),
                  [S('call'),S('foo'),[17,s1],[]],
                  [S(':='),s1,None]]
                 )

    def testCallWithF(self):
        s1=mkScratch()
        self.tst([S('call'),s1,[17,19],[]],
                 [S('begin'),
                  [S('call'),s1,[17,19],[]],
                  [S(':='),s1,None]]
                 )

    def testCallWithBoth(self):
        s1=mkScratch()
        self.tst([S('call'),s1,[17,s1],[]],
                 [S('begin'),
                  [S('call'),s1,[17,s1],[]],
                  [S(':='),s1,None]]
                 )

    def testCallWithout(self):
        s1=mkScratch()
        self.tst([S('foo'),17,19],None)

    def testCallVarargsPos(self):
        s1=mkScratch()
        self.tst([S('call'),S('foo'),s1,[]],
                 [S('begin'),
                  [S('call'),S('foo'),s1,[]],
                  [S(':='),s1,None]]
                 )

    def testCallVarargsKw(self):
        s1=mkScratch()
        self.tst([S('call'),S('foo'),[],s1],
                 [S('begin'),
                  [S('call'),S('foo'),[],s1],
                  [S(':='),s1,None]]
                 )

class ChildStmtsTestCase(unittest.TestCase):
    def c(self,pyleStmt):
        return list(map(lambda pathAndStmt: pathAndStmt[1],
                        adder.pyle.childStmts(pyleStmt)))

    def testReturn(self):
        assert self.c([S('return'),1])==[]

    def testYield(self):
        assert self.c([S('yield'),1])==[]

    def testTry(self):
        s1=mkScratch()
        assert self.c([S('try'),
                       [S('call'),S('f'),[s1],[]],
                       [S(':ValueError'),S('ve'),
                        [S('call'),S('h'),[s1,S('ve')],[]]],
                       [S(':finally'),[S('call'),[S('g')],[],[]]]
                       ])==[[S('call'),S('f'),[s1],[]],
                            [S('call'),S('h'),[s1,S('ve')],[]],
                            [S('call'),[S('g')],[],[]]]

    def testRaise(self):
        assert self.c([S('raise'),S('e')])==[]

    def testReraise(self):
        assert self.c([S('reraise')])==[]

    def testIf(self):
        assert self.c([S('if'),S('e'),
                       [S('call'),S('print'),[S('e')],[]]])==[
            [S('call'),S('print'),[S('e')],[]]
            ]

    def testIfElse(self):
        assert self.c([S('if'),S('e'),
                       [S('call'),S('print'),[S('e')],[]],
                       [S('call'),S('p'),[S('q')],[]]
                       ])==[
            [S('call'),S('print'),[S('e')],[]],
            [S('call'),S('p'),[S('q')],[]]
            ]

    def testWhile(self):
        assert self.c([S('while'),S('e'),
                       [S('call'),S('print'),[S('e')],[]]])==[
            [S('call'),S('print'),[S('e')],[]]
            ]

    def testBreak(self):
        assert self.c([S('break')])==[]

    def testContinue(self):
        assert self.c([S('continue')])==[]

    def testDef(self):
        assert self.c([S('def'),
                       S('f'),
                       [],
                       [S('return'),9]
                       ])==[[S('return'),9]]

    def testClass(self):
        assert self.c([S('class'),S('C'),
                       [S('Base1'),S('Base2')],
                       [S('def'),S('__init__'),[S('self')],
                        [S(':='),[S('.'),S('self'),S('x')],9]
                        ]])==[[S('def'),S('__init__'),[S('self')],
                               [S(':='),[S('.'),S('self'),S('x')],9]
                               ]]

    def testAssign(self):
        assert self.c([S(':='),S('e'),9])==[]

    def testImport(self):
        assert self.c([S('import'),S('e')])==[]

    def testPass(self):
        assert self.c([S('pass')])==[]

    def testBegin(self):
        assert self.c([S('begin'),
                       [S(':='),S('x'),9],
                       [S('call'),S('f'),[S('x')],[]]
                       ])==[
            [S(':='),S('x'),9],
            [S('call'),S('f'),[S('x')],[]]
            ]

    def testCall(self):
        assert self.c([S('call'),S('fred'),[],[]])==[]

suite=unittest.TestSuite(
    ( 
      unittest.makeSuite(StrTestCase,'test'),
      unittest.makeSuite(ToPythonTestCase,'test'),
      unittest.makeSuite(BuildToPythonTestCase,'test'),
      #unittest.makeSuite(TrimScratchesTestCase,'test'),
      unittest.makeSuite(ChildStmtsTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

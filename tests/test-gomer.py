#!/usr/bin/env python3

import unittest,pdb,sys,os
from adder.gomer import *
from adder.pyle import toPythonTree,toPythonFlat,flatten
from adder.common import Symbol as S,gensym
import adder.common

class O:
    pass

class ReduceTestCase(unittest.TestCase):
    def setUp(self):
        gensym.nextId=1
        self.stmts=[]

    def tearDown(self):
        self.stmts=None

    def r(self,gomer,isStmt):
        res=reduce(gomer,isStmt,self.stmts.append)
        gensym.nextId=1
        return res

    def testIntExpr(self):
        assert self.r(7,False)==7
        assert not self.stmts

    def testIntStmt(self):
        assert self.r(7,True) is None
        assert not self.stmts

    def testSymbolExpr(self):
        assert self.r(S('fred'),False)==S('fred')
        assert not self.stmts

    def testSymbolStmt(self):
        assert self.r(S('fred'),True) is None
        assert not self.stmts

    def testSimpleFuncExpr(self):
        scratch=gensym('scratch')
        gensym.nextId=1
        assert self.r([S('fred'),7,8],False)==scratch
        assert self.stmts==[[S(':='),scratch,[S('call'),S('fred'),[7,8],[]]]]

    def testSimpleFuncExprKw(self):
        scratch=gensym('scratch')
        gensym.nextId=1
        assert self.r([S('fred'),7,8,
                       S(':barney'),17,
                       S(':wilma'),19,
                       ],False)==scratch
        assert self.stmts==[[S(':='),scratch,[S('call'),
                                              S('fred'),
                                              [7,8],
                                              [[S('barney'),17],
                                               [S('wilma'),19],
                                               ]
                                              ]
                             ]
                            ]

    def testSimpleFuncExprKw2(self):
        scratch=gensym('scratch')
        gensym.nextId=1
        assert self.r([S('fred'),7,8,
                       S(':barney'),17,
                       12,
                       S(':wilma'),19,
                       ],False)==scratch
        assert self.stmts==[[S(':='),scratch,[S('call'),
                                              S('fred'),
                                              [7,8,12],
                                              [[S('barney'),17],
                                               [S('wilma'),19],
                                               ]
                                              ]
                             ]
                            ]

    def testNestedFuncExpr(self):
        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        gensym.nextId=1
        assert self.r([S('fred'),7,[S('barney'),9,S('pebbles')]],
                      False)==scratch2
        assert self.stmts==[
            [S(':='),scratch1,[S('call'),S('barney'),[9,S('pebbles')],[]]],
            [S(':='),scratch2,[S('call'),S('fred'),[7,scratch1],[]]]
            ]

    def testSimpleFuncStmt(self):
        scratch=gensym('scratch')
        gensym.nextId=1
        assert self.r([S('fred'),7,8],True) is None
        assert self.stmts==[[S('call'),S('fred'),[7,8],[]]]

    def testNestedFuncStmt(self):
        scratch1=gensym('scratch')
        gensym.nextId=1
        assert self.r([S('fred'),7,[S('barney'),9,S('pebbles')]],
                      True) is None
        assert self.stmts==[
            [S(':='),scratch1,[S('barney'),9,S('pebbles')]],
            [S('fred'),7,scratch1]
            ]

    def testNestedFuncStmt(self):
        scratch1=gensym('scratch')
        gensym.nextId=1
        assert self.r([S('fred'),7,[S('barney'),9,S('pebbles')]],
                      True) is None
        assert self.stmts==[
            [S(':='),scratch1,[S('call'),S('barney'),[9,S('pebbles')],[]]],
            [S('call'),S('fred'),[7,scratch1],[]]
            ]

    def testIfWithElseExpr(self):
        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        ifScratch=gensym('if')
        scratch4=gensym('scratch')
        gensym.nextId=1
        x=self.r([S('if'),
                       [S('<'),S('n'),10],
                       [S('barney'),9,S('bam-bam')],
                       [S('fred'),7,S('pebbles')],
                       ],
                      False)
        assert x==ifScratch
        assert self.stmts==[
            [S(':='),scratch1,[S('binop'),S('<'),S('n'),10]],
            [S('if'),
             scratch1,
             [S('begin'),
              [S(':='),scratch2,[S('call'),S('barney'),[9,S('bam-bam')],[]]],
              [S(':='),ifScratch,scratch2]],
             [S('begin'),
              [S(':='),scratch4,[S('call'),S('fred'),[7,S('pebbles')],[]]],
              [S(':='),ifScratch,scratch4]],
             ],
            ]

    def testIfWithElseStmt(self):
        ifScratch=gensym('scratch')
        gensym.nextId=1
        x=self.r([S('if'),
                  [S('<'),S('n'),10],
                  [S('barney'),9,S('bam-bam')],
                  [S('fred'),7,S('pebbles')],
                  ],
                 True)
        assert x is None
        assert self.stmts==[
            [S(':='),ifScratch,[S('binop'),S('<'),S('n'),10]],
            [S('if'),
             ifScratch,
             [S('call'),S('barney'),[9,S('bam-bam')],[]],
             [S('call'),S('fred'),[7,S('pebbles')],[]]
             ]
            ]

    def testIfWithEmptyElse(self):
        ifScratch=gensym('scratch')
        gensym.nextId=1
        x=self.r([S('if'),
                  [S('<'),S('n'),10],
                  [S('barney'),9,S('bam-bam')],
                  [S('begin')],
                  ],
                 True)
        assert x is None
        assert self.stmts==[
            [S(':='),ifScratch,[S('binop'),S('<'),S('n'),10]],
            [S('if'),
             ifScratch,
             [S('call'),S('barney'),[9,S('bam-bam')],[]]
             ]
            ]

    def testWhileExpr(self):
        whileScratch=gensym('while')
        condScratch=gensym('scratch')
        gensym.nextId=1
        x=self.r([S('while'),
                       [S('<'),S('n'),10],
                       [S(':='),S('n'),[S('+'),S('n'),1]]
                  ],
                 False)
        assert x==whileScratch
        assert self.stmts==[
            [S(':='),whileScratch,None],
            [S(':='),condScratch,[S('binop'),S('<'),S('n'),10]],
            [S('while'),
             condScratch,
             [S('begin'),
              [S(':='),S('n'),[S('binop'),S('+'),S('n'),1]],
              [S(':='),whileScratch,S('n')],
              [S(':='),condScratch,[S('binop'),S('<'),S('n'),10]]
              ]
             ]
            ]

    def testWhileStmt(self):
        condScratch=gensym('scratch')
        gensym.nextId=1
        x=self.r([S('while'),
                  [S('<'),S('n'),10],
                  [S(':='),S('n'),[S('+'),S('n'),1]]
                  ],
                 True)
        assert x is None
        assert self.stmts==[
            [S(':='),condScratch,[S('binop'),S('<'),S('n'),10]],
            [S('while'),
             condScratch,
             [S('begin'),
              [S(':='),S('n'),[S('binop'),S('+'),S('n'),1]],
              [S(':='),condScratch,[S('binop'),S('<'),S('n'),10]]
              ]
             ]
            ]

    def testWhileStmtWithBreak(self):
        whileCondScratch=gensym('scratch')
        ifCondScratch=gensym('scratch')
        gensym.nextId=1
        src=[S('while'),
                  [S('<'),S('n'),10],
                  [S(':='),S('n'),[S('+'),S('n'),1]],
                  [S('if'),[S('=='),S('n'),7],
                   [S('break')]
                   ]
                  ]
        x=self.r(src,
                 True)
        assert x is None
        expected=[
            [S(':='),whileCondScratch,[S('binop'),S('<'),S('n'),10]],
            [S('while'),
             whileCondScratch,
             [S('begin'),
              [S(':='),S('n'),[S('binop'),S('+'),S('n'),1]],
              [S(':='),ifCondScratch,[S('binop'),S('=='),S('n'),7]],
              [S('if'),
               ifCondScratch,
               [S('break')]
               ],
              [S(':='),whileCondScratch,[S('binop'),S('<'),S('n'),10]],
              ]
             ]
            ]
        assert self.stmts==expected

    def testWhileStmtWithContinue(self):
        whileCondScratch=gensym('scratch')
        ifCondScratch=gensym('scratch')
        gensym.nextId=1
        src=[S('while'),
                  [S('<'),S('n'),10],
                  [S(':='),S('n'),[S('+'),S('n'),1]],
                  [S('if'),[S('=='),S('n'),7],
                   [S('continue')]
                   ]
                  ]
        x=self.r(src,
                 True)
        assert x is None
        assert self.stmts==[
            [S(':='),whileCondScratch,[S('binop'),S('<'),S('n'),10]],
            [S('while'),
             whileCondScratch,
             [S('begin'),
              [S(':='),S('n'),[S('binop'),S('+'),S('n'),1]],
              [S(':='),ifCondScratch,[S('binop'),S('=='),S('n'),7]],
              [S('if'),
               ifCondScratch,
               [S('continue')]
               ],
              [S(':='),whileCondScratch,[S('binop'),S('<'),S('n'),10]],
              ]
             ]
            ]

    def testDefunStmt(self):
        x=self.r([S('defun'),S('fact'),[S('n')],
                  [S('if'),
                   [S('<'),S('n'),2],
                   1,
                   [S('*'),S('n'),[S('fact'),[S('-'),S('n'),1]]]
                   ]
                  ],
                 True)
        assert x is None

        gensym.nextId=1
        condScratch=gensym('scratch')
        ifScratch=gensym('if')
        scratch2=gensym('scratch')
        scratch3=gensym('scratch')
        scratch4=gensym('scratch')
        scratch5=gensym('scratch')

        expected=[
            [S('def'),S('fact'),[S('n')],
             [S('begin'),
              [S(':='),condScratch,[S('binop'),S('<'),S('n'),2]],
              [S('if'),
               condScratch,
               [S(':='),ifScratch,1],
               [S('begin'),
                [S(':='),scratch2,[S('binop'),S('-'),S('n'),1]],
                [S(':='),scratch3,[S('call'),S('fact'),[scratch2],[]]],
                [S(':='),scratch4,[S('binop'),S('*'),S('n'),scratch3]],
                [S(':='),ifScratch,scratch4]
                ]
               ],
              [S('return'),ifScratch],
              ]
             ]
            ]
        assert self.stmts==expected

    def testDefunExpr(self):
        x=self.r([S('defun'),S('fact'),[S('n')],
                  [S('if'),
                   [S('<'),S('n'),2],
                   1,
                   [S('*'),S('n'),[S('fact'),[S('-'),S('n'),1]]]
                   ]
                  ],
                 False)
        assert x==S('fact')

        gensym.nextId=1
        condScratch=gensym('scratch')
        ifScratch=gensym('if')
        scratch2=gensym('scratch')
        scratch3=gensym('scratch')
        scratch4=gensym('scratch')
        scratch5=gensym('scratch')

        expected=[
            [S('def'),S('fact'),[S('n')],
             [S('begin'),
              [S(':='),condScratch,[S('binop'),S('<'),S('n'),2]],
              [S('if'),
               condScratch,
               [S(':='),ifScratch,1],
               [S('begin'),
                [S(':='),scratch2,[S('binop'),S('-'),S('n'),1]],
                [S(':='),scratch3,[S('call'),S('fact'),[scratch2],[]]],
                [S(':='),scratch4,[S('binop'),S('*'),S('n'),scratch3]],
                [S(':='),ifScratch,scratch4]
                ]
               ],
              [S('return'),ifScratch],
              ]
             ]
            ]
        assert self.stmts==expected

    def testDefunStmtRest(self):
        x=self.r([S('defun'),S('fact'),[S('n'),S('&rest'),S('r')],
                  [S('if'),
                   [S('<'),S('n'),2],
                   1,
                   [S('*'),S('n'),[S('fact'),[S('-'),S('n'),1]]]
                   ]
                  ],
                 True)
        assert x is None

        gensym.nextId=1
        condScratch=gensym('scratch')
        ifScratch=gensym('if')
        scratch2=gensym('scratch')
        scratch3=gensym('scratch')
        scratch4=gensym('scratch')
        scratch5=gensym('scratch')

        expected=[
            [S('def'),S('fact'),[S('n'),S('&rest'),S('r')],
             [S('begin'),
              [S(':='),condScratch,[S('binop'),S('<'),S('n'),2]],
              [S('if'),
               condScratch,
               [S(':='),ifScratch,1],
               [S('begin'),
                [S(':='),scratch2,[S('binop'),S('-'),S('n'),1]],
                [S(':='),scratch3,[S('call'),S('fact'),[scratch2],[]]],
                [S(':='),scratch4,[S('binop'),S('*'),S('n'),scratch3]],
                [S(':='),ifScratch,scratch4]
                ]
               ],
              [S('return'),ifScratch],
              ]
             ]
            ]
        assert self.stmts==expected

    def testLambdaExpr(self):
        x=self.r([S('lambda'),[S('n')],
                  [S('if'),
                   [S('<'),S('n'),2],
                   1,
                   [S('*'),S('n'),[S('fact'),[S('-'),S('n'),1]]]
                   ]
                  ],
                 False)

        gensym.nextId=1
        lambdaScratch=gensym('lambda')
        condScratch=gensym('scratch')
        ifScratch=gensym('if')
        scratch2=gensym('scratch')
        scratch3=gensym('scratch')
        scratch4=gensym('scratch')
        scratch5=gensym('scratch')

        assert x==lambdaScratch

        expected=[
            [S('def'),lambdaScratch,[S('n')],
             [S('begin'),
              [S(':='),condScratch,[S('binop'),S('<'),S('n'),2]],
              [S('if'),
               condScratch,
               [S(':='),ifScratch,1],
               [S('begin'),
                [S(':='),scratch2,[S('binop'),S('-'),S('n'),1]],
                [S(':='),scratch3,[S('call'),S('fact'),[scratch2],[]]],
                [S(':='),scratch4,[S('binop'),S('*'),S('n'),scratch3]],
                [S(':='),ifScratch,scratch4]
                ]
               ],
              [S('return'),ifScratch],
              ]
             ]
            ]
        assert self.stmts==expected

    def testLambdaExprRest(self):
        x=self.r([S('lambda'),[S('n'),S('&rest'),S('r')],
                  [S('if'),
                   [S('<'),S('n'),2],
                   1,
                   [S('*'),S('n'),[S('fact'),[S('-'),S('n'),1]]]
                   ]
                  ],
                 False)

        gensym.nextId=1
        lambdaScratch=gensym('lambda')
        condScratch=gensym('scratch')
        ifScratch=gensym('if')
        scratch2=gensym('scratch')
        scratch3=gensym('scratch')
        scratch4=gensym('scratch')
        scratch5=gensym('scratch')

        assert x==lambdaScratch

        expected=[
            [S('def'),lambdaScratch,[S('n'),S('&rest'),S('r')],
             [S('begin'),
              [S(':='),condScratch,[S('binop'),S('<'),S('n'),2]],
              [S('if'),
               condScratch,
               [S(':='),ifScratch,1],
               [S('begin'),
                [S(':='),scratch2,[S('binop'),S('-'),S('n'),1]],
                [S(':='),scratch3,[S('call'),S('fact'),[scratch2],[]]],
                [S(':='),scratch4,[S('binop'),S('*'),S('n'),scratch3]],
                [S(':='),ifScratch,scratch4]
                ]
               ],
              [S('return'),ifScratch],
              ]
             ]
            ]
        assert self.stmts==expected

    def testLambdaStmt(self):
        x=self.r([S('lambda'),[S('n')],
                  [S('if'),
                   [S('<'),S('n'),2],
                   1,
                   [S('*'),S('n'),[S('fact'),[S('-'),S('n'),1]]]
                   ]
                  ],
                 True)

        assert x is None
        assert not self.stmts

    def testClassTopEmptyStmt(self):
        x=self.r([S('class'),S('C'),[]],
                 True)
        assert x is None

        assert self.stmts==[
            [S('class'),S('C'),[]]
            ]

    def testClass1BaseEmptyStmt(self):
        x=self.r([S('class'),S('C'),[S('B')]],
                 True)
        assert x is None

        assert self.stmts==[
            [S('class'),S('C'),[S('B')]]
            ]

    def testClass2BaseEmptyStmt(self):
        x=self.r([S('class'),S('C'),[S('B1'),S('B2')]],
                 True)
        assert x is None

        assert self.stmts==[
            [S('class'),S('C'),[S('B1'),S('B2')]]
            ]

    def testClass2BaseFuncStmt(self):
        scratch1=gensym('scratch')
        gensym.nextId=1

        x=self.r([S('class'),S('C'),[S('B1'),S('B2')],
                  [S('defun'),S('__init__'),[S('self'),S('x')],
                   [S(':='),[S('.'),S('self'),S('x')],S('x')]
                   ]
                  ],
                 True)
        assert x is None

        assert self.stmts==[
            [S('class'),S('C'),[S('B1'),S('B2')],
             [S('def'),S('__init__'),[S('self'),S('x')],
              [S('begin'),
               [S(':='),[S('.'),S('self'),S('x')],S('x')],
               [S(':='),scratch1,[S('.'),S('self'),S('x')]],
               [S('return'),scratch1]
               ]
              ]
             ]
            ]

    def testClass2BaseFuncStaticStmt(self):
        scratch1=gensym('scratch')
        gensym.nextId=1

        x=self.r([S('class'),S('C'),[S('B1'),S('B2')],
                  [S(':='),S('y'),7],
                  [S('defun'),S('__init__'),[S('self'),S('x')],
                   [S(':='),[S('.'),S('self'),S('x')],S('x')]
                   ]
                  ],
                 True)
        assert x is None

        assert self.stmts==[
            [S('class'),S('C'),[S('B1'),S('B2')],
             [S(':='),S('y'),7],
             [S('def'),S('__init__'),[S('self'),S('x')],
              [S('begin'),
               [S(':='),[S('.'),S('self'),S('x')],S('x')],
               [S(':='),scratch1,[S('.'),S('self'),S('x')]],
               [S('return'),scratch1]
               ]
              ]
             ]
            ]

    def testClass2BaseFuncStaticExpr(self):
        scratch1=gensym('scratch')
        gensym.nextId=1

        x=self.r([S('class'),S('C'),[S('B1'),S('B2')],
                  [S(':='),S('y'),7],
                  [S('defun'),S('__init__'),[S('self'),S('x')],
                   [S(':='),[S('.'),S('self'),S('x')],S('x')]
                   ]
                  ],
                 False)
        assert x is S('C')

        assert self.stmts==[
            [S('class'),S('C'),[S('B1'),S('B2')],
             [S(':='),S('y'),7],
             [S('def'),S('__init__'),[S('self'),S('x')],
              [S('begin'),
               [S(':='),[S('.'),S('self'),S('x')],S('x')],
               [S(':='),scratch1,[S('.'),S('self'),S('x')]],
               [S('return'),scratch1]
               ]
              ]
             ]
            ]

    def testBeginStmt(self):
        x=self.r([S('begin'),
                  [S(':='),S('x'),9],
                  [S(':='),S('y'),7],
                  [S(':='),S('z'),[S('*'),S('x'),S('y')]],
                  ],
                 True)

        assert x is None

        assert self.stmts==[
             [S(':='),S('x'),9],
             [S(':='),S('y'),7],
             [S(':='),S('z'),[S('binop'),S('*'),S('x'),S('y')]],
            ]

    def testBeginExpr(self):
        x=self.r([S('begin'),
                  [S(':='),S('x'),9],
                  [S(':='),S('y'),7],
                  [S(':='),S('z'),[S('*'),S('x'),S('y')]],
                  ],
                 False)

        assert x==S('z')

        assert self.stmts==[
             [S(':='),S('x'),9],
             [S(':='),S('y'),7],
             [S(':='),S('z'),[S('binop'),S('*'),S('x'),S('y')]],
            ]

    def testAssignStmt(self):
        x=self.r([S(':='),S('z'),[S('*'),9,7]],
                 True)

        assert x is None

        assert self.stmts==[
             [S(':='),S('z'),[S('binop'),S('*'),9,7]],
            ]

    def testAssignExpr(self):
        x=self.r([S(':='),S('z'),[S('*'),9,7]],
                 False)

        assert x==S('z')

        assert self.stmts==[
             [S(':='),S('z'),[S('binop'),S('*'),9,7]],
            ]

    def testAssignDotStmt(self):
        x=self.r([S(':='),
                  [S('.'),S('z'),S('x'),S('y')],
                  [S('*'),9,7]],
                 True)

        assert x is None

        assert self.stmts==[
             [S(':='),
              [S('.'),S('z'),S('x'),S('y')],
              [S('binop'),S('*'),9,7]],
            ]

    def testAssignSubscriptStmt(self):
        x=self.r([S(':='),
                  [S('[]'),S('z'),3],
                  [S('*'),9,7]],
                 True)

        assert x is None

        assert self.stmts==[
             [S(':='),
              [S('[]'),S('z'),3],
              [S('binop'),S('*'),9,7]]
            ]

    def testAssignExpr(self):
        x=self.r([S(':='),S('z'),[S('*'),9,7]],
                 False)

        assert x==S('z')

        assert self.stmts==[
             [S(':='),S('z'),[S('binop'),S('*'),9,7]],
            ]

    def testAssignDotExpr(self):
        x=self.r([S(':='),
                  [S('.'),S('z'),S('x'),S('y')],
                  [S('*'),9,7]],
                 False)

        gensym.nextId=1
        scratch=gensym('scratch')

        assert x==scratch

        assert self.stmts==[
             [S(':='),
              [S('.'),S('z'),S('x'),S('y')],
              [S('binop'),S('*'),9,7]],
             [S(':='),
              scratch,
              [S('.'),S('z'),S('x'),S('y')]
              ]
            ]

    def testAssignSubscriptExpr(self):
        x=self.r([S(':='),
                  [S('[]'),S('z'),3],
                  [S('*'),9,7]],
                 False)

        gensym.nextId=1
        scratch=gensym('scratch')

        assert x==scratch

        assert self.stmts==[
             [S(':='),
              [S('[]'),S('z'),3],
              [S('binop'),S('*'),9,7]],
             [S(':='),
              scratch,
              [S('[]'),S('z'),3]
              ]
            ]

    def testImportStmt(self):
        x=self.r([S('import'),S('re'),S('adder.runtime')],
                 True)

        assert x is None

        assert self.stmts==[
            [S('import'),S('re')],
            [S('import'),S('adder.runtime')],
            ]

    def testImportExpr(self):
        x=self.r([S('import'),S('re'),S('adder.runtime')],
                 False)

        assert x==S('adder.runtime')

        assert self.stmts==[
            [S('import'),S('re')],
            [S('import'),S('adder.runtime')],
            ]

    def testQuoteIntExpr(self):
        x=self.r([S('quote'),9],
                 False)

        assert x==9
        assert not self.stmts

    def testQuoteNoneExpr(self):
        x=self.r([S('quote'),None],
                 False)

        assert x is None
        assert not self.stmts

    def testQuoteListExpr(self):
        x=self.r([S('quote'),[1,2,3]],
                 False)

        scratch=gensym('scratch')

        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('quote'),[1,2,3]]]
            ]

    def testQuoteIntStmt(self):
        x=self.r([S('quote'),9],
                 True)

        assert x is None
        assert not self.stmts

    def testQuoteNoneStmt(self):
        x=self.r([S('quote'),None],
                 True)

        assert x is None
        assert not self.stmts

    def testQuoteListStmt(self):
        x=self.r([S('quote'),[1,2,3]],
                 True)

        assert x is None
        assert not self.stmts

    def testReturnStmt(self):
        x=self.r([S('return'),[S('*'),9,7]],
                 True)

        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('binop'),S('*'),9,7]],
            [S('return'),scratch],
            ]

    def testReturnInDefun(self):
        x=self.r([S('defun'),S('f'),[S('x')],
                  [S('return'),S('x')]
                  ],
                 True)

        assert x is None
        assert self.stmts==[
            [S('def'),S('f'),[S('x')],
             [S('begin'),
              [S('return'),S('x')],
              [S('return'),None]
              ]
             ]
            ]

    def testCallReturnInDefun(self):
        x=self.r([S('begin'),
                  [S('defun'),S('f'),[S('x')],
                   [S('return'),S('x')]
                   ],
                  [S('f'),9]
                  ],
                 False)

        scratch=gensym('scratch')

        assert x is scratch
        assert self.stmts==[
            [S('def'),S('f'),[S('x')],
             [S('begin'),
              [S('return'),S('x')],
              [S('return'),None]
              ]
             ],
            [S(':='),scratch,[S('call'),S('f'),[9],[]]]
            ]

    def testReturnExpr(self):
        x=self.r([S('return'),[S('*'),9,7]],
                 False)

        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('binop'),S('*'),9,7]],
            [S('return'),scratch],
            ]

    def testYieldStmt(self):
        x=self.r([S('yield'),[S('*'),9,7]],
                 True)

        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('binop'),S('*'),9,7]],
            [S('yield'),scratch],
            ]

    def testYieldExpr(self):
        x=self.r([S('yield'),[S('*'),9,7]],
                 False)

        scratch=gensym('scratch')

        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('binop'),S('*'),9,7]],
            [S('yield'),scratch],
            ]

    def testAnd0Expr(self):
        x=self.r([S('and')],
                 False)

        assert x is True
        assert not self.stmts

    def testAnd1Expr(self):
        x=self.r([S('and'),S('x')],
                 False)

        assert x==S('x')
        assert not self.stmts

    def testAnd2Expr(self):
        x=self.r([S('and'),S('x'),S('y')],
                 False)

        ifScratch=gensym('if')
        assert x==ifScratch
        assert self.stmts==[
            [S('if'),S('x'),
             [S(':='),ifScratch,S('y')],
             [S(':='),ifScratch,S('x')],
             ]
            ]

    def testAnd2Stmt(self):
        x=self.r([S('and'),[S('f'),1],[S('f'),2]],
                 True)

        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('call'),S('f'),[1],[]]],
            [S('if'),scratch,
             [S('call'),S('f'),[2],[]]
             ]
            ]

    def testAnd3Expr(self):
        x=self.r([S('and'),S('x'),S('y'),S('z')],
                 False)

        ifScratch1=gensym('if')
        ifScratch2=gensym('if')
        expected=[
            [S('if'),S('x'),
             [S('begin'),
              [S('if'),S('y'),
               [S(':='),ifScratch1,S('z')],
               [S(':='),ifScratch1,S('y')]
               ],
              [S(':='),ifScratch2,ifScratch1]
              ],
             [S(':='),ifScratch2,S('x')]
             ]
            ]
        assert x==ifScratch2
        assert self.stmts==expected

    def testOr0Expr(self):
        x=self.r([S('or')],
                 False)

        assert x is False
        assert not self.stmts

    def testOr1Expr(self):
        x=self.r([S('or'),S('x')],
                 False)

        assert x==S('x')
        assert not self.stmts

    def testOr2Expr(self):
        x=self.r([S('or'),S('x'),S('y')],
                 False)

        ifScratch=gensym('if')
        assert x==ifScratch
        assert self.stmts==[
            [S('if'),S('x'),
             [S(':='),ifScratch,S('x')],
             [S(':='),ifScratch,S('y')],
             ]
            ]

    def testOr2Stmt(self):
        x=self.r([S('or'),[S('f'),1],[S('f'),2]],
                 True)

        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('call'),S('f'),[1],[]]],
            [S('if'),scratch,
             [S('begin')],
             [S('call'),S('f'),[2],[]],
             ]
            ]

    def testOr3Expr(self):
        x=self.r([S('or'),S('x'),S('y'),S('z')],
                 False)

        ifScratch1=gensym('if')
        ifScratch2=gensym('if')
        expected=[
            [S('if'),S('x'),
             [S(':='),ifScratch1,S('x')],
             [S('begin'),
              [S('if'),S('y'),
               [S(':='),ifScratch2,S('y')],
               [S(':='),ifScratch2,S('z')]
               ],
              [S(':='),ifScratch1,ifScratch2]
              ]
             ]
            ]
        assert x==ifScratch1
        assert self.stmts==expected

    def testVarDot0Expr(self):
        x=self.r([S('.'),S('x')],
                 False)

        assert x==S('x')
        assert not self.stmts

    def testVarDot1Expr(self):
        x=self.r([S('.'),S('x'),S('y')],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('.'),S('x'),S('y')]]
            ]

    def testVarDot2Expr(self):
        x=self.r([S('.'),S('x'),S('y'),S('z')],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('.'),S('x'),S('y'),S('z')]]
            ]

    # F. Dot Fitzgerald
    def testFDot0Expr(self):
        x=self.r([S('.'),[S('f'),7]],
                 False)
        scratch=gensym('scratch')

        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,
             [S('call'),S('f'),[7],[]]],
            ]

    def testFDot1Expr(self):
        x=self.r([S('.'),[S('f'),7],S('y')],
                 False)
        scratch1=gensym('scratch')
        scratch2=gensym('scratch')

        assert x==scratch2
        assert self.stmts==[
            [S(':='),scratch1,
             [S('call'),S('f'),[7],[]]],
            [S(':='),scratch2,
             [S('.'),scratch1,S('y')]]
            ]

    def testFDot2Expr(self):
        x=self.r([S('.'),[S('f'),7],S('y'),S('z')],
                 False)
        scratch1=gensym('scratch')
        scratch2=gensym('scratch')

        assert x==scratch2
        assert self.stmts==[
            [S(':='),scratch1,
             [S('call'),S('f'),[7],[]]],
            [S(':='),scratch2,
             [S('.'),scratch1,S('y'),S('z')]]
            ]

    def testVarDot0Stmt(self):
        x=self.r([S('.'),S('x')],
                 True)

        assert x is None
        assert not self.stmts

    def testVarDot1Stmt(self):
        x=self.r([S('.'),S('x'),S('y')],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert not self.stmts

    def testVarDot2Stmt(self):
        x=self.r([S('.'),S('x'),S('y'),S('z')],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert not self.stmts

    # F. Dot Fitzgerald
    def testFDot0Stmt(self):
        x=self.r([S('.'),[S('f'),7]],
                 True)
        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S('call'),S('f'),[7],[]]
            ]

    def testFDot1Stmt(self):
        x=self.r([S('.'),[S('f'),7],S('y')],
                 True)
        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('call'),S('f'),[7],[]]]
            ]

    def testFDot2Stmt(self):
        x=self.r([S('.'),[S('f'),7],S('y'),S('z')],
                 True)
        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('call'),S('f'),[7],[]]]
            ]

    def testRaise(self):
        x=self.r([S('raise'),[S('f'),7]],
                 True)
        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('call'),S('f'),[7],[]]],
            [S('raise'),scratch]
            ]

    def testReraise(self):
        x=self.r([S('raise')],
                 True)

        assert x is None
        assert self.stmts==[
            [S('reraise')]
            ]

    def testPrint0Stmt(self):
        x=self.r([S('print')],
                 True)

        assert x is None
        assert self.stmts==[
            [S('call'),S('print'),[],[]]
            ]

    def testPrint1Stmt(self):
        x=self.r([S('print'),5],
                 True)

        assert x is None
        assert self.stmts==[
            [S('call'),S('print'),[5],[]]
            ]

    def testPrint2Stmt(self):
        x=self.r([S('print'),5,[S('x'),12]],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('call'),S('x'),[12],[]]],
            [S('call'),S('print'),[5,scratch],[]]
            ]

    def testPrint0Expr(self):
        x=self.r([S('print')],
                 False)

        assert x is None
        assert self.stmts==[
            [S('call'),S('print'),[],[]]
            ]

    def testPrint1Expr(self):
        x=self.r([S('print'),5],
                 False)

        assert x==5
        assert self.stmts==[
            [S('call'),S('print'),[5],[]]
            ]

    def testPrint2Expr(self):
        x=self.r([S('print'),5,[S('x'),12]],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('call'),S('x'),[12],[]]],
            [S('call'),S('print'),[5,scratch],[]]
            ]

    def testPlus0Expr(self):
        x=self.r([S('+')],
                 False)

        assert x==0
        assert not self.stmts

    def testPlus1VarExpr(self):
        x=self.r([S('+'),5],
                 False)

        assert x==5
        assert not self.stmts

    def testPlus1FExpr(self):
        x=self.r([S('+'),[S('f'),7]],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('call'),S('f'),[7],[]]],
            ]

    def testPlus2Expr(self):
        x=self.r([S('+'),5,[S('f'),7]],
                 False)

        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        assert x==scratch2
        assert self.stmts==[
            [S(':='),scratch1,[S('call'),S('f'),[7],[]]],
            [S(':='),scratch2,[S('binop'),S('+'),5,scratch1]],
            ]

    def testPlus3Expr(self):
        x=self.r([S('+'),5,[S('f'),7],9],
                 False)

        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        scratch3=gensym('scratch')
        assert x==scratch3
        assert self.stmts==[
            [S(':='),scratch1,[S('call'),S('f'),[7],[]]],
            [S(':='),scratch2,[S('binop'),S('+'),scratch1,9]],
            [S(':='),scratch3,[S('binop'),S('+'),5,scratch2]],
            ]

    def testTimes0Expr(self):
        x=self.r([S('*')],
                 False)

        assert x==1
        assert not self.stmts

    def testTimes1VarExpr(self):
        x=self.r([S('*'),5],
                 False)

        assert x==5
        assert not self.stmts

    def testTimes1FExpr(self):
        x=self.r([S('*'),[S('f'),7]],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('call'),S('f'),[7],[]]],
            ]

    def testTimes2Expr(self):
        x=self.r([S('*'),5,[S('f'),7]],
                 False)

        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        assert x==scratch2
        assert self.stmts==[
            [S(':='),scratch1,[S('call'),S('f'),[7],[]]],
            [S(':='),scratch2,[S('binop'),S('*'),5,scratch1]],
            ]

    def testTimes3Expr(self):
        x=self.r([S('*'),5,[S('f'),7],9],
                 False)

        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        scratch3=gensym('scratch')
        assert x==scratch3
        assert self.stmts==[
            [S(':='),scratch1,[S('call'),S('f'),[7],[]]],
            [S(':='),scratch2,[S('binop'),S('*'),scratch1,9]],
            [S(':='),scratch3,[S('binop'),S('*'),5,scratch2]],
            ]

    def testMinus0Expr(self):
        x=self.r([S('-')],
                 False)

        assert x==0
        assert not self.stmts

    def testMinus1VarExpr(self):
        x=self.r([S('-'),5],
                 False)

        assert x==-5
        assert not self.stmts

    def testMinus1FExpr(self):
        x=self.r([S('-'),[S('f'),7]],
                 False)

        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        assert x==scratch2
        assert self.stmts==[
            [S(':='),scratch1,[S('call'),S('f'),[7],[]]],
            [S(':='),scratch2,[S('binop'),S('-'),0,scratch1]],
            ]

    def testMinus2Expr(self):
        x=self.r([S('-'),5,[S('f'),7]],
                 False)

        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        assert x==scratch2
        assert self.stmts==[
            [S(':='),scratch1,[S('call'),S('f'),[7],[]]],
            [S(':='),scratch2,[S('binop'),S('-'),5,scratch1]],
            ]

    def testMinus3Expr(self):
        x=self.r([S('-'),5,[S('f'),7],9],
                 False)

        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        scratch3=gensym('scratch')
        assert x==scratch3
        assert self.stmts==[
            [S(':='),scratch1,[S('call'),S('f'),[7],[]]],
            [S(':='),scratch2,[S('binop'),S('-'),5,scratch1]],
            [S(':='),scratch3,[S('binop'),S('-'),scratch2,9]],
            ]

    def testFdiv0Expr(self):
        x=self.r([S('/')],
                 False)

        assert x==1
        assert not self.stmts

    def testFdiv1VarExpr(self):
        x=self.r([S('/'),5],
                 False)

        assert x==1/5
        assert not self.stmts

    def testFdiv1FExpr(self):
        x=self.r([S('/'),[S('f'),7]],
                 False)

        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        assert x==scratch2
        assert self.stmts==[
            [S(':='),scratch1,[S('call'),S('f'),[7],[]]],
            [S(':='),scratch2,[S('binop'),S('/'),1,scratch1]],
            ]

    def testFdiv2Expr(self):
        x=self.r([S('/'),5,[S('f'),7]],
                 False)

        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        assert x==scratch2
        assert self.stmts==[
            [S(':='),scratch1,[S('call'),S('f'),[7],[]]],
            [S(':='),scratch2,[S('binop'),S('/'),5,scratch1]],
            ]

    def testFdiv3Expr(self):
        x=self.r([S('/'),5,[S('f'),7],9],
                 False)

        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        scratch3=gensym('scratch')
        assert x==scratch3
        assert self.stmts==[
            [S(':='),scratch1,[S('call'),S('f'),[7],[]]],
            [S(':='),scratch2,[S('binop'),S('/'),5,scratch1]],
            [S(':='),scratch3,[S('binop'),S('/'),scratch2,9]],
            ]

    def testIdiv0Expr(self):
        x=self.r([S('//')],
                 False)

        assert x==1
        assert not self.stmts

    def testIdiv1VarExpr(self):
        x=self.r([S('//'),5],
                 False)

        assert x==0
        assert not self.stmts

    def testIdiv1FExpr(self):
        x=self.r([S('//'),[S('f'),7]],
                 False)

        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        assert x==scratch2
        assert self.stmts==[
            [S(':='),scratch1,[S('call'),S('f'),[7],[]]],
            [S(':='),scratch2,[S('binop'),S('//'),1,scratch1]],
            ]

    def testIdiv2Expr(self):
        x=self.r([S('//'),5,[S('f'),7]],
                 False)

        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        assert x==scratch2
        assert self.stmts==[
            [S(':='),scratch1,[S('call'),S('f'),[7],[]]],
            [S(':='),scratch2,[S('binop'),S('//'),5,scratch1]],
            ]

    def testIdiv3Expr(self):
        x=self.r([S('//'),5,[S('f'),7],9],
                 False)

        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        scratch3=gensym('scratch')
        assert x==scratch3
        assert self.stmts==[
            [S(':='),scratch1,[S('call'),S('f'),[7],[]]],
            [S(':='),scratch2,[S('binop'),S('//'),5,scratch1]],
            [S(':='),scratch3,[S('binop'),S('//'),scratch2,9]],
            ]

    def testEquals0Expr(self):
        x=self.r([S('==')],
                 False)

        assert x is True
        assert not self.stmts

    def testEquals1Expr(self):
        x=self.r([S('=='),5],
                 False)

        assert x is True
        assert not self.stmts

    def testEquals2Expr(self):
        x=self.r([S('=='),5,7],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('binop'),S('=='),5,7]]
            ]

    def testEquals3Expr(self):
        x=self.r([S('=='),5,7,9],
                 False)

        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        scratchIf=gensym('if')
        assert x==scratchIf
        assert self.stmts==[
            [S(':='),scratch1,[S('binop'),S('=='),5,7]],
            [S('if'),
             scratch1,
             [S('begin'),
              [S(':='),scratch2,[S('binop'),S('=='),7,9]],
              [S(':='),scratchIf,scratch2]
              ],
             [S(':='),scratchIf,scratch1],
             ]
            ]

    def testInExpr(self):
        x=self.r([S('in'),5,S('l')],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('binop'),S('in'),5,S('l')]]
            ]

    def testInExpr2(self):
        x=self.r([S('in'),[S('+'),5,7],S('l')],
                 False)

        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        assert x==scratch2
        assert self.stmts==[
            [S(':='),scratch1,[S('binop'),S('+'),5,7]],
            [S(':='),scratch2,[S('binop'),S('in'),scratch1,S('l')]]
            ]

    def testSubscriptExpr(self):
        x=self.r([S('[]'),S('l'),5],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('[]'),S('l'),5]]
            ]

    def testSubscriptStmt(self):
        x=self.r([S('[]'),S('l'),5],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert not self.stmts

    def testSubscriptNestingStmt(self):
        x=self.r([S('[]'),S('l'),[S('+'),5,7]],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('binop'),S('+'),5,7]]
            ]

    def testSliceLExpr(self):
        x=self.r([S('slice'),S('l'),5],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('slice'),S('l'),5,None]]
            ]

    def testSliceLRExpr(self):
        x=self.r([S('slice'),S('l'),5,7],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('slice'),S('l'),5,7]]
            ]

    def testSliceLStmt(self):
        x=self.r([S('slice'),S('l'),5],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert not self.stmts

    def testSliceLRStmt(self):
        x=self.r([S('slice'),S('l'),5,7],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert not self.stmts

    def testToListStmt(self):
        x=self.r([S('to-list'),S('l')],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert not self.stmts

    def testToListExpr(self):
        x=self.r([S('to-list'),S('l')],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('call'),S('python.list'),[S('l')],[]]]
            ]

    def testToTupleStmt(self):
        x=self.r([S('to-tuple'),S('l')],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert not self.stmts

    def testToTupleExpr(self):
        x=self.r([S('to-tuple'),S('l')],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('call'),S('python.tuple'),[S('l')],[]]]
            ]

    def testToSetStmt(self):
        x=self.r([S('to-set'),S('l')],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert not self.stmts

    def testToSetExpr(self):
        x=self.r([S('to-set'),S('l')],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('call'),S('python.set'),[S('l')],[]]]
            ]

    def testToDictStmt(self):
        x=self.r([S('to-dict'),S('l')],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert not self.stmts

    def testToDictExpr(self):
        x=self.r([S('to-dict'),S('l')],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('call'),S('python.dict'),[S('l')],[]]]
            ]

    def testIsinstanceStmt(self):
        x=self.r([S('isinstance'),S('l'),S('list')],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert not self.stmts

    def testIsinstanceExpr(self):
        x=self.r([S('isinstance'),S('l'),S('list')],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('call'),
                              S('python.isinstance'),
                              [S('l'),S('list')],
                              []
                              ]
             ]
            ]

    def testMkListStmt(self):
        x=self.r([S('mk-list'),S('l'),9,7],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert not self.stmts

    def testMkListExpr(self):
        x=self.r([S('mk-list'),S('l'),9,7],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('mk-list'),S('l'),9,7]]
            ]

    def testMkTupleStmt(self):
        x=self.r([S('mk-tuple'),S('l'),9,7],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert not self.stmts

    def testMkTupleExpr(self):
        x=self.r([S('mk-tuple'),S('l'),9,7],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('mk-tuple'),S('l'),9,7]]
            ]

    def testMkSetStmt(self):
        x=self.r([S('mk-set'),S('l'),9,7],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert not self.stmts

    def testMkSetExpr(self):
        x=self.r([S('mk-set'),S('l'),9,7],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('mk-set'),S('l'),9,7]]
            ]

    def testMkDictStmt(self):
        x=self.r([S('mk-dict'),S(':x'),9,S(':y'),7],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert not self.stmts

    def testMkDictExpr(self):
        x=self.r([S('mk-dict'),S(':x'),9,S(':y'),7],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('mk-dict'),[S('x'),9],[S('y'),7]]]
            ]

    def testApplyPos(self):
        scratch=gensym('scratch')
        gensym.nextId=1
        assert self.r([S('apply'),S('fred'),S('posArgs')],
                      False)==scratch
        assert self.stmts==[[S(':='),scratch,[S('call'),
                                              S('fred'),
                                              S('posArgs'),
                                              []
                                              ]
                             ]
                            ]

    def testApplyKw(self):
        scratch=gensym('scratch')
        gensym.nextId=1
        assert self.r([S('apply'),
                       S('fred'),
                       [S('quote'),[]],
                       S('kwArgs')
                       ],
                      False)==scratch
        assert self.stmts==[[S(':='),scratch,[S('call'),
                                              S('fred'),
                                              [],
                                              S('kwArgs')
                                              ]
                             ]
                            ]

    def testApplyPosKw(self):
        scratch=gensym('scratch')
        gensym.nextId=1
        assert self.r([S('apply'),
                       S('fred'),
                       S('posArgs'),
                       S('kwArgs')
                       ],
                      False)==scratch
        assert self.stmts==[[S(':='),scratch,[S('call'),
                                              S('fred'),
                                              S('posArgs'),
                                              S('kwArgs')
                                              ]
                             ]
                            ]

    def testTry1ExnStmt(self):
        x=self.r([S('try'),
                  [S('f'),9,7],
                  [S('z'),12],
                  [S(':Exception'),S('e'),
                   [S('print'),S('e')],
                   [S('y'),S('e')]]
                  ],
                 True)
        assert x is None
        assert self.stmts==[
            [S('try'),
             [S('begin'),
              [S('call'),S('f'),[9,7],[]],
              [S('call'),S('z'),[12],[]]
              ],
             [S(':Exception'),S('e'),
              [S('begin'),
               [S('call'),S('print'),[S('e')],[]],
               [S('call'),S('y'),[S('e')],[]]
               ]
              ]
             ]
            ]

    def testTry1ExnExpr(self):
        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        scratch3=gensym('scratch')
        gensym.nextId=1
        x=self.r([S('try'),
                  [S('f'),9,7],
                  [S('z'),12],
                  [S(':Exception'),S('e'),
                   [S('print'),S('e')],
                   [S('y'),S('e')]]
                  ],
                 False)
        assert x is scratch1
        assert self.stmts==[
            [S('try'),
             [S('begin'),
              [S('call'),S('f'),[9,7],[]],
              [S(':='),scratch3,[S('call'),S('z'),[12],[]]],
              [S(':='),scratch1,scratch3]
              ],
             [S(':Exception'),S('e'),
              [S('begin'),
               [S('call'),S('print'),[S('e')],[]],
               [S(':='),scratch2,[S('call'),S('y'),[S('e')],[]]],
              [S(':='),scratch1,scratch2]
               ]
              ]
             ]
            ]

    def testTry2ExnStmt(self):
        x=self.r([S('try'),
                  [S('f'),9,7],
                  [S('z'),12],
                  [S(':KeyError'),S('dd'),
                   [S('fiddle'),S('dd')],
                   [S('flangle'),S('bloober')]],
                  [S(':Exception'),S('e'),
                   [S('print'),S('e')],
                   [S('y'),S('e')]]
                  ],
                 True)
        assert x is None
        assert self.stmts==[
            [S('try'),
             [S('begin'),
              [S('call'),S('f'),[9,7],[]],
              [S('call'),S('z'),[12],[]]
              ],
             [S(':KeyError'),S('dd'),
              [S('begin'),
               [S('call'),S('fiddle'),[S('dd')],[]],
               [S('call'),S('flangle'),[S('bloober')],[]]
               ]
              ],
             [S(':Exception'),S('e'),
              [S('begin'),
               [S('call'),S('print'),[S('e')],[]],
               [S('call'),S('y'),[S('e')],[]]
               ]
              ]
             ]
            ]

    def testTry2ExnExpr(self):
        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        scratch3=gensym('scratch')
        scratch4=gensym('scratch')
        gensym.nextId=1
        x=self.r([S('try'),
                  [S('f'),9,7],
                  [S('z'),12],
                  [S(':KeyError'),S('dd'),
                   [S('fiddle'),S('dd')],
                   [S('flangle'),S('bloober')]],
                  [S(':Exception'),S('e'),
                   [S('print'),S('e')],
                   [S('y'),S('e')]]
                  ],
                 False)
        assert x is scratch1
        assert self.stmts==[
            [S('try'),
             [S('begin'),
              [S('call'),S('f'),[9,7],[]],
              [S(':='),scratch4,[S('call'),S('z'),[12],[]]],
              [S(':='),scratch1,scratch4]
              ],
             [S(':KeyError'),S('dd'),
              [S('begin'),
               [S('call'),S('fiddle'),[S('dd')],[]],
               [S(':='),scratch2,[S('call'),S('flangle'),[S('bloober')],[]]],
              [S(':='),scratch1,scratch2]
               ]
              ],
             [S(':Exception'),S('e'),
              [S('begin'),
               [S('call'),S('print'),[S('e')],[]],
               [S(':='),scratch3,[S('call'),S('y'),[S('e')],[]]],
              [S(':='),scratch1,scratch3]
               ]
              ]
             ]
            ]

    def testTry2ExnFinallyStmt(self):
        x=self.r([S('try'),
                  [S('f'),9,7],
                  [S('z'),12],
                  [S(':KeyError'),S('dd'),
                   [S('fiddle'),S('dd')],
                   [S('flangle'),S('bloober')]],
                  [S(':Exception'),S('e'),
                   [S('print'),S('e')],
                   [S('y'),S('e')]],
                  [S(':finally'),
                   [S('print'),"gibbon"]]
                  ],
                 True)
        assert x is None
        assert self.stmts==[
            [S('try'),
             [S('begin'),
              [S('call'),S('f'),[9,7],[]],
              [S('call'),S('z'),[12],[]]
              ],
             [S(':KeyError'),S('dd'),
              [S('begin'),
               [S('call'),S('fiddle'),[S('dd')],[]],
               [S('call'),S('flangle'),[S('bloober')],[]]
               ]
              ],
             [S(':Exception'),S('e'),
              [S('begin'),
               [S('call'),S('print'),[S('e')],[]],
               [S('call'),S('y'),[S('e')],[]]
               ]
              ],
             [S(':finally'),
              [S('call'),S('print'),["gibbon"],[]]
              ]
             ]
            ]

    def testTry2ExnFinallyExpr(self):
        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        scratch3=gensym('scratch')
        scratch4=gensym('scratch')
        gensym.nextId=1
        x=self.r([S('try'),
                  [S('f'),9,7],
                  [S('z'),12],
                  [S(':KeyError'),S('dd'),
                   [S('fiddle'),S('dd')],
                   [S('flangle'),S('bloober')]],
                  [S(':Exception'),S('e'),
                   [S('print'),S('e')],
                   [S('y'),S('e')]],
                  [S(':finally'),
                   [S('print'),"gibbon"]
                   ]
                  ],
                 False)
        assert x is scratch1
        assert self.stmts==[
            [S('try'),
             [S('begin'),
              [S('call'),S('f'),[9,7],[]],
              [S(':='),scratch4,[S('call'),S('z'),[12],[]]],
              [S(':='),scratch1,scratch4]
              ],
             [S(':KeyError'),S('dd'),
              [S('begin'),
               [S('call'),S('fiddle'),[S('dd')],[]],
               [S(':='),scratch2,[S('call'),S('flangle'),[S('bloober')],[]]],
              [S(':='),scratch1,scratch2]
               ]
              ],
             [S(':Exception'),S('e'),
              [S('begin'),
               [S('call'),S('print'),[S('e')],[]],
               [S(':='),scratch3,[S('call'),S('y'),[S('e')],[]]],
              [S(':='),scratch1,scratch3]
               ]
              ],
             [S(':finally'),
              [S('call'),S('print'),["gibbon"],[]]
              ]
             ]
            ]

class ToPythonTestCase(unittest.TestCase):
    def setUp(self):
        gensym.nextId=1
        self.stmts=[]
        self.v=False

    def tearDown(self):
        self.stmts=None

    def r(self,gomer,isStmt):
        gensym.nextId=1
        res=reduce(gomer,isStmt,self.stmts.append)
        gensym.nextId=1
        return res

    def toP(self,gomer,isStmt,*,v=False):
        pyleExpr=self.r(gomer,isStmt)
        stmtTrees=[]
        flat=""
        for pyleStmt in self.stmts:
            il=adder.pyle.build(pyleStmt)
            stmtTree=il.toPythonTree()
            stmtTrees.append(stmtTree)
        stmtFlat=flatten(tuple(stmtTrees))
        if not isStmt:
            il=adder.pyle.build(pyleExpr)
            exprTree=il.toPythonTree()
        else:
            exprTree=None

        if v:
            print()
            print(stmtTrees)
            print(stmtFlat)
            print(exprTree)
        return (stmtTrees,stmtFlat,exprTree)

    def testIntExpr(self):
        assert self.toP(7,False)==([],"","7")

    def testIntStmt(self):
        assert self.toP(7,True)==([],"",None)

    def testSymbolExpr(self):
        assert self.toP(S('fred'),False)==([],"","fred")

    def testSymbolStmt(self):
        assert self.toP(S('fred'),True)==([],"",None)

    def testSimpleFuncExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1
        assert self.toP([S('fred'),7,8],False)==(
            ["%s=fred(7,8)" % scratchP],
            "%s=fred(7,8)\n" % scratchP,
            scratchP
            )

    def testSimpleFuncExprKw(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1
        assert self.toP([S('fred'),7,8,
                         S(':barney'),17,
                         S(':wilma'),19,
                         ],False)==(
            ["%s=fred(7,8,barney=17,wilma=19)" % scratchP],
            "%s=fred(7,8,barney=17,wilma=19)\n" % scratchP,
            scratchP
            )

    def testSimpleFuncExprKw2(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1
        assert self.toP([S('fred'),7,8,
                         S(':barney'),17,
                         12,
                         S(':wilma'),19,
                         ],False)==(
            ["%s=fred(7,8,12,barney=17,wilma=19)" % scratchP],
            "%s=fred(7,8,12,barney=17,wilma=19)\n" % scratchP,
            scratchP
            )

    def testNestedFuncExpr(self):
        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2P=scratch2.toPython()

        gensym.nextId=1
        assert self.toP([S('fred'),7,[S('barney'),9,S('pebbles')]],
                        False)==(
            ["%s=barney(9,pebbles)" % scratch1P,
             "%s=fred(7,%s)" % (scratch2P,scratch1P)],
            """%s=barney(9,pebbles)
%s=fred(7,%s)
""" % (scratch1P,scratch2P,scratch1P),
            scratch2P
            )

    def testSimpleFuncStmt(self):
        assert self.toP([S('fred'),7,8],True)==(
            ["fred(7,8)"],"fred(7,8)\n",
            None
            )

    def testNestedFuncStmt(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()

        gensym.nextId=1
        assert self.toP([S('fred'),7,[S('barney'),9,S('pebbles')]],
                        True)==(
            ["%s=barney(9,pebbles)" % scratch1P,
             "fred(7,%s)" % scratch1P],
            """%s=barney(9,pebbles)
fred(7,%s)
""" % (scratch1P,scratch1P),
            None
            )

    def testIfWithElseExpr(self):
        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        ifScratch=gensym('if')
        scratch4=gensym('scratch')

        scratch1P=scratch1.toPython()
        scratch2P=scratch2.toPython()
        scratch4P=scratch4.toPython()
        ifScratchP=ifScratch.toPython()

        gensym.nextId=1
        assert self.toP([S('if'),
                         [S('<'),S('n'),10],
                         [S('barney'),9,S('bam-bam')],
                         [S('fred'),7,S('pebbles')],
                         ],
                        False)==(
            ["%s=n<10" % scratch1P,
             ("if %s:" % scratch1P,
              [("%s=barney(9,%s)" % (scratch2P,S('bam-bam').toPython()),
                "%s=%s" % (ifScratchP,scratch2P)
                )],
              "else:",
              [("%s=fred(7,pebbles)" % scratch4P,
                "%s=%s" % (ifScratchP,scratch4P)
                )]
              )],
            """%s=n<10
if %s:
    %s=barney(9,%s)
    %s=%s
else:
    %s=fred(7,pebbles)
    %s=%s
""" % (scratch1P,
       scratch1P,
       scratch2P,S('bam-bam').toPython(),
       ifScratchP,scratch2P,
       scratch4P,
       ifScratchP,scratch4P),
            ifScratchP
            )

    def testIfWithElseStmt(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()

        gensym.nextId=1
        assert self.toP([S('if'),
                         [S('<'),S('n'),10],
                         [S('barney'),9,S('bam-bam')],
                         [S('fred'),7,S('pebbles')],
                         ],
                        True)==(
            ["%s=n<10" % scratch1P,
             ("if %s:" % scratch1P,
              ["barney(9,%s)" % S('bam-bam').toPython()],
              "else:",
              ["fred(7,pebbles)"]
              )],
            """%s=n<10
if %s:
    barney(9,%s)
else:
    fred(7,pebbles)
""" % (scratch1P,
       scratch1P,
       S('bam-bam').toPython()),
            None
            )

    def testWhileExpr(self):
        whileScratch=gensym('while')
        condScratch=gensym('scratch')
        whileScratchP=whileScratch.toPython()
        condScratchP=condScratch.toPython()

        gensym.nextId=1
        assert self.toP([S('while'),
                         [S('<'),S('n'),10],
                         [S(':='),S('n'),[S('+'),S('n'),1]]
                         ],
                        False)==(
            ["%s=None" % whileScratchP,
             "%s=n<10" % condScratchP,
             ("while %s:" % condScratchP,
              [("n=n+1",
               "%s=n" % whileScratchP,
               "%s=n<10" % condScratchP)
               ])],"""%s=None
%s=n<10
while %s:
    n=n+1
    %s=n
    %s=n<10
""" % (whileScratchP,
       condScratchP,
       condScratchP,
       whileScratchP,
       condScratchP),
            whileScratchP)

    def testWhileStmt(self):
        condScratch=gensym('scratch')
        condScratchP=condScratch.toPython()
        gensym.nextId=1

        assert self.toP([S('while'),
                         [S('<'),S('n'),10],
                         [S(':='),S('n'),[S('+'),S('n'),1]]
                         ],
                        True)==(
            ["%s=n<10" % condScratchP,
             ("while %s:" % condScratchP,
              [("n=n+1",
               "%s=n<10" % condScratchP)
               ])],"""%s=n<10
while %s:
    n=n+1
    %s=n<10
""" % (condScratchP,
       condScratchP,
       condScratchP),
            None)

    def testWhileStmtWithBreak(self):
        whileCondScratch=gensym('scratch')
        ifCondScratch=gensym('scratch')
        whileCondScratchP=whileCondScratch.toPython()
        ifCondScratchP=ifCondScratch.toPython()
        gensym.nextId=1

        assert self.toP([S('while'),
                         [S('<'),S('n'),10],
                         [S(':='),S('n'),[S('+'),S('n'),1]],
                         [S('if'),[S('=='),S('n'),7],
                          [S('break')]
                          ]
                         ],
                        True)==(
            ["%s=n<10" % whileCondScratchP,
             ("while %s:" % whileCondScratchP,
              [("n=n+1",
                "%s=n==7" % ifCondScratchP,
                ("if %s:" % ifCondScratchP,
                 ["break"]),
                "%s=n<10" % whileCondScratchP
                )])],"""%s=n<10
while %s:
    n=n+1
    %s=n==7
    if %s:
        break
    %s=n<10
""" % (whileCondScratchP,
       whileCondScratchP,
       ifCondScratchP,
       ifCondScratchP,
       whileCondScratchP),
            None
            )

    def testWhileStmtWithContinue(self):
        whileCondScratch=gensym('scratch')
        ifCondScratch=gensym('scratch')
        whileCondScratchP=whileCondScratch.toPython()
        ifCondScratchP=ifCondScratch.toPython()
        gensym.nextId=1

        assert self.toP([S('while'),
                         [S('<'),S('n'),10],
                         [S(':='),S('n'),[S('+'),S('n'),1]],
                         [S('if'),[S('=='),S('n'),7],
                          [S('continue')]
                          ]
                         ],
                        True)==(
            ["%s=n<10" % whileCondScratchP,
             ("while %s:" % whileCondScratchP,
              [("n=n+1",
                "%s=n==7" % ifCondScratchP,
                ("if %s:" % ifCondScratchP,
                 ["continue"]),
                "%s=n<10" % whileCondScratchP
                )])],"""%s=n<10
while %s:
    n=n+1
    %s=n==7
    if %s:
        continue
    %s=n<10
""" % (whileCondScratchP,
       whileCondScratchP,
       ifCondScratchP,
       ifCondScratchP,
       whileCondScratchP),
            None
            )

    def testDefunStmt(self):
        condScratch=gensym('scratch')
        ifScratch=gensym('if')
        scratch3=gensym('scratch')
        scratch4=gensym('scratch')
        scratch5=gensym('scratch')
        condScratchP=condScratch.toPython()
        ifScratchP=ifScratch.toPython()
        scratch3P=scratch3.toPython()
        scratch4P=scratch4.toPython()
        scratch5P=scratch5.toPython()

        gensym.nextId=1
        assert self.toP([S('defun'),S('fact'),[S('n')],
                         [S('if'),
                          [S('<'),S('n'),2],
                          1,
                          [S('*'),S('n'),[S('fact'),[S('-'),S('n'),1]]]
                          ]
                         ],
                        True)==(
            [("def fact(n):",
              [("%s=n<2" % condScratchP,
                ("if %s:" % condScratchP,
                 ["%s=1" % ifScratchP],
                 "else:",
                 [("%s=n-1" % scratch3P,
                   "%s=fact(%s)" % (scratch4P,scratch3P),
                   "%s=n*%s" % (scratch5P,scratch4P),
                   "%s=%s" % (ifScratchP,scratch5P))]
                 ),
                "return %s" % ifScratchP
                )]
              )],"""def fact(n):
    %s=n<2
    if %s:
        %s=1
    else:
        %s=n-1
        %s=fact(%s)
        %s=n*%s
        %s=%s
    return %s
""" % (condScratchP,
       condScratchP,
       ifScratchP,
       scratch3P,
       scratch4P,scratch3P,
       scratch5P,scratch4P,
       ifScratchP,scratch5P,
       ifScratchP),
            None
            )

    def testDefunExpr(self):
        condScratch=gensym('scratch')
        ifScratch=gensym('if')
        scratch3=gensym('scratch')
        scratch4=gensym('scratch')
        scratch5=gensym('scratch')
        condScratchP=condScratch.toPython()
        ifScratchP=ifScratch.toPython()
        scratch3P=scratch3.toPython()
        scratch4P=scratch4.toPython()
        scratch5P=scratch5.toPython()

        gensym.nextId=1
        assert self.toP([S('defun'),S('fact'),[S('n')],
                         [S('if'),
                          [S('<'),S('n'),2],
                          1,
                          [S('*'),S('n'),[S('fact'),[S('-'),S('n'),1]]]
                          ]
                         ],
                        False)==(
            [("def fact(n):",
              [("%s=n<2" % condScratchP,
                ("if %s:" % condScratchP,
                 ["%s=1" % ifScratchP],
                 "else:",
                 [("%s=n-1" % scratch3P,
                   "%s=fact(%s)" % (scratch4P,scratch3P),
                   "%s=n*%s" % (scratch5P,scratch4P),
                   "%s=%s" % (ifScratchP,scratch5P))]
                 ),
                "return %s" % ifScratchP
                )]
              )],"""def fact(n):
    %s=n<2
    if %s:
        %s=1
    else:
        %s=n-1
        %s=fact(%s)
        %s=n*%s
        %s=%s
    return %s
""" % (condScratchP,
       condScratchP,
       ifScratchP,
       scratch3P,
       scratch4P,scratch3P,
       scratch5P,scratch4P,
       ifScratchP,scratch5P,
       ifScratchP),
            'fact'
            )

    def testDefunStmtRest(self):
        condScratch=gensym('scratch')
        ifScratch=gensym('if')
        scratch3=gensym('scratch')
        scratch4=gensym('scratch')
        scratch5=gensym('scratch')
        condScratchP=condScratch.toPython()
        ifScratchP=ifScratch.toPython()
        scratch3P=scratch3.toPython()
        scratch4P=scratch4.toPython()
        scratch5P=scratch5.toPython()

        gensym.nextId=1
        assert self.toP([S('defun'),S('fact'),[S('n'),S('&rest'),S('r')],
                         [S('if'),
                          [S('<'),S('n'),2],
                          1,
                          [S('*'),S('n'),[S('fact'),[S('-'),S('n'),1]]]
                          ]
                         ],
                        True)==(
            [("def fact(n,*r):",
              [("%s=n<2" % condScratchP,
                ("if %s:" % condScratchP,
                 ["%s=1" % ifScratchP],
                 "else:",
                 [("%s=n-1" % scratch3P,
                   "%s=fact(%s)" % (scratch4P,scratch3P),
                   "%s=n*%s" % (scratch5P,scratch4P),
                   "%s=%s" % (ifScratchP,scratch5P))]
                 ),
                "return %s" % ifScratchP
                )]
              )],"""def fact(n,*r):
    %s=n<2
    if %s:
        %s=1
    else:
        %s=n-1
        %s=fact(%s)
        %s=n*%s
        %s=%s
    return %s
""" % (condScratchP,
       condScratchP,
       ifScratchP,
       scratch3P,
       scratch4P,scratch3P,
       scratch5P,scratch4P,
       ifScratchP,scratch5P,
       ifScratchP),
            None
            )

    def testLambdaExpr(self):
        lambdaScratch=gensym('lambda')
        condScratch=gensym('scratch')
        ifScratch=gensym('if')
        scratch3=gensym('scratch')
        scratch4=gensym('scratch')
        scratch5=gensym('scratch')
        lambdaScratchP=lambdaScratch.toPython()
        condScratchP=condScratch.toPython()
        ifScratchP=ifScratch.toPython()
        scratch3P=scratch3.toPython()
        scratch4P=scratch4.toPython()
        scratch5P=scratch5.toPython()

        gensym.nextId=1
        assert self.toP([S('lambda'),[S('n')],
                         [S('if'),
                          [S('<'),S('n'),2],
                          1,
                          [S('*'),S('n'),[S('fact'),[S('-'),S('n'),1]]]
                          ]
                         ],
                        False)==(
            [("def %s(n):" % lambdaScratchP,
              [("%s=n<2" % condScratchP,
                ("if %s:" % condScratchP,
                 ["%s=1" % ifScratchP],
                 "else:",
                 [("%s=n-1" % scratch3P,
                   "%s=fact(%s)" % (scratch4P,scratch3P),
                   "%s=n*%s" % (scratch5P,scratch4P),
                   "%s=%s" % (ifScratchP,scratch5P))]
                 ),
                "return %s" % ifScratchP
                )]
              )],"""def %s(n):
    %s=n<2
    if %s:
        %s=1
    else:
        %s=n-1
        %s=fact(%s)
        %s=n*%s
        %s=%s
    return %s
""" % (lambdaScratchP,
       condScratchP,
       condScratchP,
       ifScratchP,
       scratch3P,
       scratch4P,scratch3P,
       scratch5P,scratch4P,
       ifScratchP,scratch5P,
       ifScratchP),
            lambdaScratchP
            )

    def testLambdaExprRest(self):
        lambdaScratch=gensym('lambda')
        condScratch=gensym('scratch')
        ifScratch=gensym('if')
        scratch3=gensym('scratch')
        scratch4=gensym('scratch')
        scratch5=gensym('scratch')
        lambdaScratchP=lambdaScratch.toPython()
        condScratchP=condScratch.toPython()
        ifScratchP=ifScratch.toPython()
        scratch3P=scratch3.toPython()
        scratch4P=scratch4.toPython()
        scratch5P=scratch5.toPython()

        gensym.nextId=1
        assert self.toP([S('lambda'),[S('n'),S('&rest'),S('r')],
                         [S('if'),
                          [S('<'),S('n'),2],
                          1,
                          [S('*'),S('n'),[S('fact'),[S('-'),S('n'),1]]]
                          ]
                         ],
                        False)==(
            [("def %s(n,*r):" % lambdaScratchP,
              [("%s=n<2" % condScratchP,
                ("if %s:" % condScratchP,
                 ["%s=1" % ifScratchP],
                 "else:",
                 [("%s=n-1" % scratch3P,
                   "%s=fact(%s)" % (scratch4P,scratch3P),
                   "%s=n*%s" % (scratch5P,scratch4P),
                   "%s=%s" % (ifScratchP,scratch5P))]
                 ),
                "return %s" % ifScratchP
                )]
              )],"""def %s(n,*r):
    %s=n<2
    if %s:
        %s=1
    else:
        %s=n-1
        %s=fact(%s)
        %s=n*%s
        %s=%s
    return %s
""" % (lambdaScratchP,
       condScratchP,
       condScratchP,
       ifScratchP,
       scratch3P,
       scratch4P,scratch3P,
       scratch5P,scratch4P,
       ifScratchP,scratch5P,
       ifScratchP),
            lambdaScratchP
            )

    def testLambdaStmt(self):
        assert self.toP([S('lambda'),[S('n')],
                         [S('if'),
                          [S('<'),S('n'),2],
                          1,
                          [S('*'),S('n'),[S('fact'),[S('-'),S('n'),1]]]
                          ]
                         ],
                        True)==([],"",None)

    def testBeginStmt(self):
        assert self.toP([S('begin'),
                         [S(':='),S('x'),9],
                         [S(':='),S('y'),7],
                         [S(':='),S('z'),[S('*'),S('x'),S('y')]],
                         ],
                        True)==(
            ["x=9",
             "y=7",
             "z=x*y"
             ],"""x=9
y=7
z=x*y
""",
            None
            )

    def testBeginExpr(self):
        assert self.toP([S('begin'),
                         [S(':='),S('x'),9],
                         [S(':='),S('y'),7],
                         [S(':='),S('z'),[S('*'),S('x'),S('y')]],
                         ],
                        False)==(
            ["x=9",
             "y=7",
             "z=x*y"
             ],"""x=9
y=7
z=x*y
""",
            'z'
            )

    def testAssignStmt(self):
        assert self.toP([S(':='),S('z'),[S('*'),9,7]],
                        True)==(
            ["z=9*7"],"z=9*7\n",
            None
            )

    def testAssignCallStmt(self):
        assert self.toP([S(':='),S('z'),[S('f'),9,7]],
                        True)==(
            ["z=f(9,7)"],"z=f(9,7)\n",
            None
            )

    def testAssignExpr(self):
        assert self.toP([S(':='),S('z'),[S('*'),9,7]],
                        False)==(
            ["z=9*7"],"z=9*7\n",
            "z"
            )

    def testAssignDotStmt(self):
        assert self.toP([S(':='),
                         [S('.'),S('z'),S('x'),S('y')],
                         [S('*'),9,7]],
                        True)==(
            ["z.x.y=9*7"],"z.x.y=9*7\n",
            None
            )

    def testAssignDotExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1
        assert self.toP([S(':='),
                         [S('.'),S('z'),S('x'),S('y')],
                         [S('*'),9,7]],
                        False)==(
            ["z.x.y=9*7","%s=z.x.y" % scratchP],
            """z.x.y=9*7
%s=z.x.y
""" % scratchP,
            scratchP
            )


    def testAssignSubscriptStmt(self):
        assert self.toP([S(':='),
                         [S('[]'),S('z'),3],
                         [S('*'),9,7]],
                        True)==(
            ["z[3]=9*7"],"z[3]=9*7\n",
            None
            )

    def testAssignSubscriptExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1
        assert self.toP([S(':='),
                         [S('[]'),S('z'),3],
                         [S('*'),9,7]],
                        False)==(
            ["z[3]=9*7","%s=z[3]" % scratchP],
            """z[3]=9*7
%s=z[3]
""" % scratchP,
            scratchP
            )

    def testImportStmt(self):
        assert self.toP([S('import'),S('re'),S('adder.runtime')],
                        True)==(
            ["import re","import adder.runtime"],
            """import re
import adder.runtime
""",
            None
            )

    def testImportExpr(self):
        assert self.toP([S('import'),S('re'),S('adder.runtime')],
                        False)==(
            ["import re","import adder.runtime"],
            """import re
import adder.runtime
""",
            "adder.runtime"
            )

    def testQuoteIntExpr(self):
        assert self.toP([S('quote'),9],
                        False)==([],"","9")

    def testQuoteNoneExpr(self):
        assert self.toP([S('quote'),None],
                        False)==([],"","None")

    def testQuoteListExpr(self):
        actual=self.toP([S('quote'),[1,2,3]],
                        False)

        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        expected=(["%s=[1, 2, 3]" % scratchP],
                  "%s=[1, 2, 3]\n" % scratchP,
                  scratchP)
        assert actual==expected

    def testQuoteIntStmt(self):
        assert self.toP([S('quote'),9],
                        True)==([],"",None)

    def testQuoteNoneStmt(self):
        assert self.toP([S('quote'),None],
                        True)==([],"",None)

    def testQuoteListStmt(self):
        assert self.toP([S('quote'),[1,2,3]],
                        True)==([],"",None)

    def testReturnStmt(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        assert self.toP([S('return'),[S('*'),9,7]],
                        True)==(
            ["%s=9*7" % scratchP,
             "return %s" % scratchP],
            """%s=9*7
return %s
""" % (scratchP,scratchP),
            None
            )

    def testReturnExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        assert self.toP([S('return'),[S('*'),9,7]],
                        False)==(
            ["%s=9*7" % scratchP,
             "return %s" % scratchP],
            """%s=9*7
return %s
""" % (scratchP,scratchP),
            "None"
            )

    def testYieldStmt(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        assert self.toP([S('yield'),[S('*'),9,7]],
                        True)==(
            ["%s=9*7" % scratchP,
             "yield %s" % scratchP],
            """%s=9*7
yield %s
""" % (scratchP,scratchP),
            None)

    def testYieldExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        assert self.toP([S('yield'),[S('*'),9,7]],
                        False)==(
            ["%s=9*7" % scratchP,
             "yield %s" % scratchP],
            """%s=9*7
yield %s
""" % (scratchP,scratchP),
            scratchP)

    def testAnd0Expr(self):
        assert self.toP([S('and')],
                        False)==([],"","True")

    def testAnd1Expr(self):
        assert self.toP([S('and'),S('x')],
                        False)==([],"","x")

    def testAnd2Expr(self):
        ifScratch=gensym('if')
        ifScratchP=ifScratch.toPython()

        assert self.toP([S('and'),S('x'),S('y')],
                        False)==(
            [("if x:",
              ["%s=y" % ifScratchP],
              "else:",
              ["%s=x" % ifScratchP]
              )],
            """if x:
    %s=y
else:
    %s=x
""" % (ifScratchP,ifScratchP),
            ifScratchP
            )

    def testAnd2Stmt(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()

        assert self.toP([S('and'),[S('f'),1],[S('f'),2]],
                        True)==(
            ["%s=f(1)" % scratchP,
             ("if %s:" % scratchP,
              ["f(2)"]
              )
             ],"""%s=f(1)
if %s:
    f(2)
""" % (scratchP,scratchP),
            None
            )

    def testAnd3Expr(self):
        ifScratch1=gensym('if')
        ifScratch1P=ifScratch1.toPython()
        ifScratch2=gensym('if')
        ifScratch2P=ifScratch2.toPython()

        assert self.toP([S('and'),S('x'),S('y'),S('z')],
                        False)==(
            [("if x:",
              [(("if y:",
                 ["%s=z" % ifScratch1P],
                 "else:",
                 ["%s=y" % ifScratch1P]
                 ),
                "%s=%s" % (ifScratch2P,ifScratch1P)
                )
               ],
              "else:",
              [("%s=x" % ifScratch2P)]
              )],"""if x:
    if y:
        %s=z
    else:
        %s=y
    %s=%s
else:
    %s=x
""" % (ifScratch1P,
       ifScratch1P,
       ifScratch2P,ifScratch1P,
       ifScratch2P),
            ifScratch2P
            )

    def testOr0Expr(self):
        assert self.toP([S('or')],
                        False)==([],"","False")

    def testOr1Expr(self):
        assert self.toP([S('or'),S('x')],
                        False)==([],"","x")

    def testOr2Expr(self):
        ifScratch=gensym('if')
        ifScratchP=ifScratch.toPython()

        assert self.toP([S('or'),S('x'),S('y')],
                        False)==(
            [("if x:",
              ["%s=x" % ifScratchP],
              "else:",
              ["%s=y" % ifScratchP]
              )],
            """if x:
    %s=x
else:
    %s=y
""" % (ifScratchP,ifScratchP),
            ifScratchP
            )

    def testOr2Stmt(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()

        assert self.toP([S('or'),[S('f'),1],[S('f'),2]],
                        True)==(
            ["%s=f(1)" % scratchP,
             ("if %s:" % scratchP,
              ["pass"],
              "else:",
              ["f(2)"])
             ],"""%s=f(1)
if %s:
    pass
else:
    f(2)
""" % (scratchP,scratchP),
            None
            )

    def testOr3Expr(self):
        ifScratch1=gensym('if')
        ifScratch1P=ifScratch1.toPython()
        ifScratch2=gensym('if')
        ifScratch2P=ifScratch2.toPython()

        assert self.toP([S('or'),S('x'),S('y'),S('z')],
                        False)==(
            [("if x:",
              ["%s=x" % ifScratch1P],
              "else:",
              [(("if y:",
                 ["%s=y" % ifScratch2P],
                 "else:",
                 ["%s=z" % ifScratch2P]
                 ),
               "%s=%s" % (ifScratch1P,ifScratch2P))
               ])],
            """if x:
    %s=x
else:
    if y:
        %s=y
    else:
        %s=z
    %s=%s
""" % (ifScratch1P,
       ifScratch2P,
       ifScratch2P,
       ifScratch1P,
       ifScratch2P),
            ifScratch1P
            )

    def testVarDot0Expr(self):
        assert self.toP([S('.'),S('x')],
                        False)==([],"","x")

    def testVarDot1Expr(self):
        x=self.toP([S('.'),S('x'),S('y')],
                   False)==([],"","x.y")

    def testVarDot2Expr(self):
        x=self.toP([S('.'),S('x'),S('y'),S('z')],
                   False)==([],"","x.y.z")

    # F. Dot Fitzgerald
    def testFDot0Expr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        assert self.toP([S('.'),[S('f'),7]],
                        False)==(["%s=f(7)" % scratchP],
                                 "%s=f(7)\n" % scratchP,
                                 scratchP)

    def testFDot1Expr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()

        assert self.toP([S('.'),[S('f'),7],S('y')],
                        False)==(
            ["%s=f(7)" % scratch1P,
             "%s=%s.y"% (scratch2P,scratch1P)
             ],
            """%s=f(7)
%s=%s.y
""" % (scratch1P,scratch2P,scratch1P),
            scratch2P)

    def testFDot2Expr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()

        assert self.toP([S('.'),[S('f'),7],S('y'),S('z')],
                        False)==(
            ["%s=f(7)" % scratch1P,
             "%s=%s.y.z"% (scratch2P,scratch1P)
             ],
            """%s=f(7)
%s=%s.y.z
""" % (scratch1P,scratch2P,scratch1P),
            scratch2P)

    def testVarDot0Stmt(self):
        assert self.toP([S('.'),S('x')],
                        True)==([],"",None)

    def testVarDot1Stmt(self):
        assert self.toP([S('.'),S('x'),S('y')],
                        True)==([],"",None)

    def testVarDot2Stmt(self):
        assert self.toP([S('.'),S('x'),S('y'),S('z')],
                        True)==([],"",None)

    # F. Dot Fitzgerald
    def testFDot0Stmt(self):
        assert self.toP([S('.'),[S('f'),7]],
                        True)==(["f(7)"],
                                 "f(7)\n",
                                 None)

    def testFDot1Stmt(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        assert self.toP([S('.'),[S('f'),7],S('y')],
                        True)==(["%s=f(7)" % scratchP],
                                 "%s=f(7)\n" % scratchP,
                                 None)

    def testFDot2Stmt(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        assert self.toP([S('.'),[S('f'),7],S('y'),S('z')],
                        True)==(["%s=f(7)" % scratchP],
                                 "%s=f(7)\n" % scratchP,
                                 None)

    def testRaise(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        assert self.toP([S('raise'),[S('f'),7]],
                        True)==(
            ["%s=f(7)" % scratchP,
             "raise %s" % scratchP
             ],
            """%s=f(7)
raise %s
"""  % (scratchP,scratchP),
            None
            )

    def testReraise(self):
        assert self.toP([S('raise')],
                        True)==(["raise"],"raise\n",None)

    def testPrint0Stmt(self):
        assert self.toP([S('print')],
                        True)==(["print()"],"print()\n",None)

    def testPrint1Stmt(self):
        assert self.toP([S('print'),5],
                        True)==(["print(5)"],"print(5)\n",None)

    def testPrint2Stmt(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        assert self.toP([S('print'),5,[S('x'),12]],
                        True)==(
            ["%s=x(12)" % scratchP,
             "print(5,%s)" % scratchP,],
            "%s=x(12)\nprint(5,%s)\n" % (scratchP,scratchP),
            None)

    def testPrint0Expr(self):
        assert self.toP([S('print')],
                        False)==(["print()"],"print()\n","None")

    def testPrint1Expr(self):
        assert self.toP([S('print'),5],
                        False)==(["print(5)"],"print(5)\n","5")

    def testPrint2Expr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        assert self.toP([S('print'),5,[S('x'),12]],
                        False)==(
            ["%s=x(12)" % scratchP,
             "print(5,%s)" % scratchP,],
            "%s=x(12)\nprint(5,%s)\n" % (scratchP,scratchP),
            scratchP)

    def testPlus0Expr(self):
        assert self.toP([S('+')],
                        False)==([],"","0")

    def testPlus1VarExpr(self):
        assert self.toP([S('+'),5],
                        False)==([],"","5")

    def testPlus1FExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        assert self.toP([S('+'),[S('f'),7]],
                        False)==(
            ["%s=f(7)" % scratchP],
            "%s=f(7)\n" % scratchP,
            scratchP
            )

    def testPlus2Expr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()

        assert self.toP([S('+'),5,[S('f'),7]],
                        False)==(
            ["%s=f(7)" % scratch1P,
             "%s=5+%s" % (scratch2P,scratch1P)
             ],"""%s=f(7)
%s=5+%s
""" % (scratch1P,scratch2P,scratch1P),
            scratch2P
            )

    def testPlus3Expr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()
        scratch3=gensym('scratch')
        scratch3P=scratch3.toPython()

        assert self.toP([S('+'),5,[S('f'),7],9],
                        False)[0]==(
            ["%s=f(7)" % scratch1P,
             "%s=%s+9" % (scratch2P,scratch1P),
             "%s=5+%s" % (scratch3P,scratch2P),
             ],"""%s=f(7)
%s=5+%s
%s=%s+9
""" % (scratch1P,
       scratch2P,scratch1P,
       scratch3P,scratch2P),
            scratch3P
            )[0]

    def testTimes0Expr(self):
        assert self.toP([S('*')],
                        False)==([],"","1")

    def testTimes1VarExpr(self):
        assert self.toP([S('*'),5],
                        False)==([],"","5")

    def testTimes1FExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        assert self.toP([S('*'),[S('f'),7]],
                        False)==(
            ["%s=f(7)" % scratchP],
            "%s=f(7)\n" % scratchP,
            scratchP
            )

    def testTimes2Expr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()

        assert self.toP([S('*'),5,[S('f'),7]],
                        False)==(
            ["%s=f(7)" % scratch1P,
             "%s=5*%s" % (scratch2P,scratch1P)
             ],"""%s=f(7)
%s=5*%s
""" % (scratch1P,scratch2P,scratch1P),
            scratch2P
            )

    def testTimes3Expr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()
        scratch3=gensym('scratch')
        scratch3P=scratch3.toPython()

        assert self.toP([S('*'),5,[S('f'),7],9],
                        False)[0]==(
            ["%s=f(7)" % scratch1P,
             "%s=%s*9" % (scratch2P,scratch1P),
             "%s=5*%s" % (scratch3P,scratch2P),
             ],"""%s=f(7)
%s=5*%s
%s=%s*9
""" % (scratch1P,
       scratch2P,scratch1P,
       scratch3P,scratch2P),
            scratch3P
            )[0]

    def testMinus0Expr(self):
        assert self.toP([S('-')],
                        False)==([],"","0")

    def testMinus1VarExpr(self):
        assert self.toP([S('-'),5],
                        False)==([],"","-5")

    def testMinus1FExpr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()

        assert self.toP([S('-'),[S('f'),7]],
                        False)==(
            ["%s=f(7)" % scratch1P,
             "%s=0-%s" % (scratch2P,scratch1P)
             ],
            """%s=f(7)
%s=0-%s
""" % (scratch1P,scratch2P,scratch1P),
            scratch2P
            )

    def testMinus2Expr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()

        assert self.toP([S('-'),5,[S('f'),7]],
                        False)==(
            ["%s=f(7)" % scratch1P,
             "%s=5-%s" % (scratch2P,scratch1P)
             ],
            """%s=f(7)
%s=5-%s
""" % (scratch1P,scratch2P,scratch1P),
            scratch2P
            )

    def testMinus3Expr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()
        scratch3=gensym('scratch')
        scratch3P=scratch3.toPython()

        assert self.toP([S('-'),5,[S('f'),7],9],
                        False)==(
            ["%s=f(7)" % scratch1P,
             "%s=5-%s" % (scratch2P,scratch1P),
             "%s=%s-9" % (scratch3P,scratch2P)
             ],
            """%s=f(7)
%s=5-%s
%s=%s-9
""" % (scratch1P,scratch2P,scratch1P,scratch3P,scratch2P),
            scratch3P
            )

    def testFDiv0Expr(self):
        assert self.toP([S('/')],
                        False)==([],"","1")

    def testFDiv1VarExpr(self):
        (tree,flat,expr)=self.toP([S('/'),5],
                                  False)
        assert (tree,flat)==([],"")
        assert float(expr)==1/5

    def testFDiv1FExpr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()

        assert self.toP([S('/'),[S('f'),7]],
                        False)==(
            ["%s=f(7)" % scratch1P,
             "%s=1/%s" % (scratch2P,scratch1P)
             ],
            """%s=f(7)
%s=1/%s
""" % (scratch1P,scratch2P,scratch1P),
            scratch2P
            )

    def testFDiv2Expr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()

        assert self.toP([S('/'),5,[S('f'),7]],
                        False)==(
            ["%s=f(7)" % scratch1P,
             "%s=5/%s" % (scratch2P,scratch1P)
             ],
            """%s=f(7)
%s=5/%s
""" % (scratch1P,scratch2P,scratch1P),
            scratch2P
            )

    def testFDiv3Expr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()
        scratch3=gensym('scratch')
        scratch3P=scratch3.toPython()

        assert self.toP([S('/'),5,[S('f'),7],9],
                        False)==(
            ["%s=f(7)" % scratch1P,
             "%s=5/%s" % (scratch2P,scratch1P),
             "%s=%s/9" % (scratch3P,scratch2P)
             ],
            """%s=f(7)
%s=5/%s
%s=%s/9
""" % (scratch1P,scratch2P,scratch1P,scratch3P,scratch2P),
            scratch3P
            )

    def testIDiv0Expr(self):
        assert self.toP([S('//')],
                        False)==([],"","1")

    def testIDiv1VarExpr(self):
        assert self.toP([S('//'),5],
                        False)==([],"","0")

    def testIDiv1FExpr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()

        assert self.toP([S('//'),[S('f'),7]],
                        False)==(
            ["%s=f(7)" % scratch1P,
             "%s=1//%s" % (scratch2P,scratch1P)
             ],
            """%s=f(7)
%s=1//%s
""" % (scratch1P,scratch2P,scratch1P),
            scratch2P
            )

    def testIDiv2Expr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()

        assert self.toP([S('//'),5,[S('f'),7]],
                        False)==(
            ["%s=f(7)" % scratch1P,
             "%s=5//%s" % (scratch2P,scratch1P)
             ],
            """%s=f(7)
%s=5//%s
""" % (scratch1P,scratch2P,scratch1P),
            scratch2P
            )

    def testIDiv3Expr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()
        scratch3=gensym('scratch')
        scratch3P=scratch3.toPython()

        assert self.toP([S('//'),5,[S('f'),7],9],
                        False)==(
            ["%s=f(7)" % scratch1P,
             "%s=5//%s" % (scratch2P,scratch1P),
             "%s=%s//9" % (scratch3P,scratch2P)
             ],
            """%s=f(7)
%s=5//%s
%s=%s//9
""" % (scratch1P,scratch2P,scratch1P,scratch3P,scratch2P),
            scratch3P
            )

    def testEquals0Expr(self):
        assert self.toP([S('==')],
                        False)==([],"","True")

    def testEquals1Expr(self):
        assert self.toP([S('=='),5],
                        False)==([],"","True")

    def testEquals2ConstExpr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        assert self.toP([S('=='),5,7],
                        False)==(
            ["%s=5==7" % scratch1P],"%s=5==7\n" % scratch1P,
            scratch1P
            )

    def testEquals3Expr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()
        ifScratch3=gensym('if')
        ifScratch3P=ifScratch3.toPython()
        assert self.toP([S('=='),5,7,9],
                        False)==(
            ["%s=5==7" % scratch1P,
             ("if %s:" % scratch1P,
              [("%s=7==9" % scratch2P,
                "%s=%s" % (ifScratch3P,scratch2P))],
              "else:",
               ["%s=%s" % (ifScratch3P,scratch1P)]
              )
             ],"""%s=5==7
if %s:
    %s=7==9
    %s=%s
else:
    %s=%s
""" % (scratch1P,
     scratch1P,
     scratch2P,
     ifScratch3P,scratch2P,
     ifScratch3P,scratch1P),
            ifScratch3P
            )

    def testInExpr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        assert self.toP([S('in'),5,S('l')],
                        False)==(["%s=5 in l" % scratch1P],
                                 "%s=5 in l\n" % scratch1P,
                                 scratch1P)

    def testInExpr2(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()
        assert self.toP([S('in'),[S('+'),5,7],S('l')],
                        False)==(["%s=5+7" % scratch1P,
                                  "%s=%s in l" % (scratch2P,scratch1P)
                                  ],
                                 """%s=5+7
%s=%s in l
""" % (scratch1P,scratch2P,scratch1P),
                                 scratch2P)

    def testSubscriptExpr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        assert self.toP([S('[]'),S('l'),5],
                        False)==(["%s=l[5]" % scratch1P],
                                 "%s=l[5]\n" % scratch1P,
                                 scratch1P)

    def testSubscriptStmt(self):
        assert self.toP([S('[]'),S('l'),5],
                        True)==([],"",None)

    def testSubscriptNestingStmt(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        assert self.toP([S('[]'),S('l'),[S('+'),5,7]],
                        True)==(["%s=5+7" % scratch1P],
                                "%s=5+7\n" % scratch1P,
                                None)

    def testSliceLExpr(self):
        actual=self.toP([S('slice'),S('l'),5],
                        False)

        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        expected=(
            ["%s=l[5:]" % scratchP],
            "%s=l[5:]\n" % scratchP,
            scratchP
            )
        assert actual==expected

    def testSliceLRExpr(self):
        actual=self.toP([S('slice'),S('l'),5,7],
                        False)

        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        expected=(
            ["%s=l[5:7]" % scratchP],
            "%s=l[5:7]\n" % scratchP,
            scratchP
            )
        assert actual==expected

    def testSliceLStmt(self):
        assert self.toP([S('slice'),S('l'),5],
                        True)==([],"",None)

    def testSliceLRStmt(self):
        assert self.toP([S('slice'),S('l'),5,7],
                        True)==([],"",None)

    def testToListStmt(self):
        assert self.toP([S('to-list'),S('l')],
                        True)==(
            [],"",
            None
            )

    def testToListExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('to-list'),S('l')],
                        False)==(
            ["%s=python.list(l)" % scratchP],
            "%s=python.list(l)\n" % scratchP,
            scratchP
            )

    def testToTupleStmt(self):
        assert self.toP([S('to-tuple'),S('l')],
                        True)==(
            [],"",
            None
            )

    def testToTupleExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('to-tuple'),S('l')],
                        False)==(
            ["%s=python.tuple(l)" % scratchP],
            "%s=python.tuple(l)\n" % scratchP,
            scratchP
            )

    def testToSetStmt(self):
        assert self.toP([S('to-set'),S('l')],
                        True)==(
            [],"",
            None
            )

    def testToSetExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('to-set'),S('l')],
                        False)==(
            ["%s=python.set(l)" % scratchP],
            "%s=python.set(l)\n" % scratchP,
            scratchP
            )

    def testToDictStmt(self):
        assert self.toP([S('to-dict'),S('l')],
                        True)==(
            [],"",
            None
            )

    def testToDictExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('to-dict'),S('l')],
                        False)==(
            ["%s=python.dict(l)" % scratchP],
            "%s=python.dict(l)\n" % scratchP,
            scratchP
            )

    def testIsinstanceStmt(self):
        assert self.toP([S('isinstance'),S('l'),S('list')],
                        True)==(
            [],"",
            None
            )

    def testIsinstanceExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('isinstance'),S('l'),S('list')],
                        False)==(
            ["%s=python.isinstance(l,list)" % scratchP],
            "%s=python.isinstance(l,list)\n" % scratchP,
            scratchP
            )

    def testMkListStmt(self):
        assert self.toP([S('mk-list'),S('l'),9,7],
                        True)==(
            [],"",
            None
            )

    def testMkListExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('mk-list'),S('l'),9,7],
                        False)==(
            ["%s=[l, 9, 7]" % scratchP],
            "%s=[l, 9, 7]\n" % scratchP,
            scratchP
            )

    def testMkTupleStmt(self):
        assert self.toP([S('mk-tuple'),S('l'),9,7],
                        True)==(
            [],"",
            None
            )

    def testMkTupleExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('mk-tuple'),S('l'),9,7],
                        False)==(
            ["%s=(l, 9, 7)" % scratchP],
            "%s=(l, 9, 7)\n" % scratchP,
            scratchP
            )

    def testMkSetStmt(self):
        assert self.toP([S('mk-set'),S('l'),9,7],
                        True)==(
            [],"",
            None
            )

    def testMkSetExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('mk-set'),S('l'),9,7],
                        False)==(
            ["%s={l, 9, 7}" % scratchP],
            "%s={l, 9, 7}\n" % scratchP,
            scratchP
            )

    def testMkDictStmt(self):
        assert self.toP([S('mk-dict'),S(':x'),9,S(':y'),7],
                        True)==(
            [],"",
            None
            )

    def testMkDictExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('mk-dict'),S(':x'),9,S(':y'),7],
                        False)==(
            ["%s={'x': 9, 'y': 7}" % scratchP],
            "%s={'x': 9, 'y': 7}\n" % scratchP,
            scratchP
            )

    def testMkSymbolStmt(self):
        assert self.toP([S('mk-symbol'),'l'],
                        True)==(
            [],"",
            None
            )

    def testMkSymbolExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('mk-symbol'),'l'],
                        False)==(
            ["%s=adder.common.Symbol('l')" % scratchP],
            "%s=adder.common.Symbol('l')\n" % scratchP,
            scratchP
            )

    def testReverseExpr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()
        gensym.nextId=1

        assert self.toP([S('reverse'),S('l')],
                        False)==(
            ["%s=python.list(l)" % scratch1P,
             "%s=%s.reverse" % (scratch2P,scratch1P),
             "%s()" % scratch2P,
             ],
            """%s=python.list(l)
%s=%s.reverse
%s()
""" % (scratch1P,scratch2P,scratch1P,scratch2P),
            scratch1P
            )

    def testTry1ExnStmt(self):
        assert self.toP([S('try'),
                         [S('f'),9,7],
                         [S('z'),12],
                         [S(':Exception'),S('e'),
                          [S('print'),S('e')],
                          [S('y'),S('e')]]
                         ],
                        True)==(
            [("try:",
              [("f(9,7)",
                "z(12)")],
              "except Exception as e:",
              [("print(e)",
                "y(e)")]
              )
             ],
            """try:
    f(9,7)
    z(12)
except Exception as e:
    print(e)
    y(e)
""",
            None)

    def testTry1ExnExpr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()
        scratch3=gensym('scratch')
        scratch3P=scratch3.toPython()
        gensym.nextId=1
        actual=self.toP([S('try'),
                         [S('f'),9,7],
                         [S('z'),12],
                         [S(':Exception'),S('e'),
                          [S('print'),S('e')],
                          [S('y'),S('e')]]
                         ],
                        False)
        expected=(
            [("try:",
              [("f(9,7)",
                "%s=z(12)" % scratch3P,
                "%s=%s" % (scratch1P,scratch3P)
                )],
              "except Exception as e:",
              [("print(e)",
                "%s=y(e)" % scratch2P,
                "%s=%s" % (scratch1P,scratch2P)
                )]
              )
             ],"""try:
    f(9,7)
    %s=z(12)
    %s=%s
except Exception as e:
    print(e)
    %s=y(e)
    %s=%s
""" % (scratch3P,scratch1P,scratch3P,scratch2P,scratch1P,scratch2P),
            scratch1P)
        assert actual==expected

    def testTry2ExnStmt(self):
        assert self.toP([S('try'),
                         [S('f'),9,7],
                         [S('z'),12],
                         [S(':KeyError'),S('dd'),
                          [S('fiddle'),S('dd')],
                          [S('flangle'),S('bloober')]],
                         [S(':Exception'),S('e'),
                          [S('print'),S('e')],
                          [S('y'),S('e')]]
                         ],
                        True)==(
            [("try:",
              [("f(9,7)",
                "z(12)")],
              "except KeyError as dd:",
              [("fiddle(dd)",
                "flangle(bloober)")],
              "except Exception as e:",
              [("print(e)",
                "y(e)")]
              )
             ],
            """try:
    f(9,7)
    z(12)
except KeyError as dd:
    fiddle(dd)
    flangle(bloober)
except Exception as e:
    print(e)
    y(e)
""",
            None)

    def testTry2ExnExpr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()
        scratch3=gensym('scratch')
        scratch3P=scratch3.toPython()
        scratch4=gensym('scratch')
        scratch4P=scratch4.toPython()
        gensym.nextId=1
        actual=self.toP([S('try'),
                         [S('f'),9,7],
                         [S('z'),12],
                         [S(':KeyError'),S('dd'),
                          [S('fiddle'),S('dd')],
                          [S('flangle'),S('bloober')]],
                         [S(':Exception'),S('e'),
                          [S('print'),S('e')],
                          [S('y'),S('e')]]
                         ],
                        False)
        expected=(
            [("try:",
              [("f(9,7)",
                "%s=z(12)" % scratch4P,
                "%s=%s" % (scratch1P,scratch4P)
                )],
              "except KeyError as dd:",
              [("fiddle(dd)",
                "%s=flangle(bloober)" % scratch2P,
                "%s=%s" % (scratch1P,scratch2P)
                )],
              "except Exception as e:",
              [("print(e)",
                "%s=y(e)" % scratch3P,
                "%s=%s" % (scratch1P,scratch3P)
                )]
              )
             ],"""try:
    f(9,7)
    %s=z(12)
    %s=%s
except KeyError as dd:
    fiddle(dd)
    %s=flangle(bloober)
    %s=%s
except Exception as e:
    print(e)
    %s=y(e)
    %s=%s
""" % (scratch4P,scratch1P,scratch4P,
       scratch2P,scratch1P,scratch2P,
       scratch3P,scratch1P,scratch3P),
            scratch1P)
        assert actual==expected

    def testTry2ExnFinallyStmt(self):
        actual=self.toP([S('try'),
                         [S('f'),9,7],
                         [S('z'),12],
                         [S(':KeyError'),S('dd'),
                          [S('fiddle'),S('dd')],
                          [S('flangle'),S('bloober')]],
                         [S(':Exception'),S('e'),
                          [S('print'),S('e')],
                          [S('y'),S('e')]],
                         [S(':finally'),
                          [S('print'),"gibbon"]]
                         ],
                        True)
        expected=(
            [("try:",
              [("f(9,7)",
                "z(12)")],
              "except KeyError as dd:",
              [("fiddle(dd)",
                "flangle(bloober)")],
              "except Exception as e:",
              [("print(e)",
                "y(e)")],
              "finally:",
              ["print('gibbon')"]
              )
             ],
            """try:
    f(9,7)
    z(12)
except KeyError as dd:
    fiddle(dd)
    flangle(bloober)
except Exception as e:
    print(e)
    y(e)
finally:
    print('gibbon')
""",
            None)
        assert actual==expected

    def testTry2ExnFinallyExpr(self):
        scratch1=gensym('scratch')
        scratch1P=scratch1.toPython()
        scratch2=gensym('scratch')
        scratch2P=scratch2.toPython()
        scratch3=gensym('scratch')
        scratch3P=scratch3.toPython()
        scratch4=gensym('scratch')
        scratch4P=scratch4.toPython()
        gensym.nextId=1
        actual=self.toP([S('try'),
                         [S('f'),9,7],
                         [S('z'),12],
                         [S(':KeyError'),S('dd'),
                          [S('fiddle'),S('dd')],
                          [S('flangle'),S('bloober')]],
                         [S(':Exception'),S('e'),
                          [S('print'),S('e')],
                          [S('y'),S('e')]],
                         [S(':finally'),
                          [S('print'),"gibbon"]
                          ]
                         ],
                        False)
        expected=(
            [("try:",
              [("f(9,7)",
                "%s=z(12)" % scratch4P,
                "%s=%s" % (scratch1P,scratch4P)
                )],
              "except KeyError as dd:",
              [("fiddle(dd)",
                "%s=flangle(bloober)" % scratch2P,
                "%s=%s" % (scratch1P,scratch2P)
                )],
              "except Exception as e:",
              [("print(e)",
                "%s=y(e)" % scratch3P,
                "%s=%s" % (scratch1P,scratch3P)
                )],
              "finally:",
              ["print('gibbon')"]
              )
             ],"""try:
    f(9,7)
    %s=z(12)
    %s=%s
except KeyError as dd:
    fiddle(dd)
    %s=flangle(bloober)
    %s=%s
except Exception as e:
    print(e)
    %s=y(e)
    %s=%s
finally:
    print('gibbon')
""" % (scratch4P,scratch1P,scratch4P,
       scratch2P,scratch1P,scratch2P,
       scratch3P,scratch1P,scratch3P),
            scratch1P)
        assert actual==expected

class EvalTestCase(unittest.TestCase):
    def setUp(self):
        gensym.nextId=1

    def e(self,expr,v=False,**globalsToSet):
        g=mkGlobals()
        g.update(globalsToSet)
        return (geval(expr,globalDict=g,verbose=v),g)

    def testConstInt(self):
        assert geval(1)==1

    def testConstString(self):
        assert geval('foo')=='foo'

    def testConstBool(self):
        assert geval(True)==True

    def testConstFloat(self):
        assert geval(5.7)==5.7

    def testVar(self):
        g=mkGlobals()
        g['x']=17
        assert geval(S('x'),globalDict=g)==17

    def testVarUndefined(self):
        try:
            geval(S('x'))
            assert False
        except NameError:
            pass

    def testCmpEq(self):
        assert geval([S('=='),5,5])==True
        assert geval([S('=='),5,7])==False

    def testCmpNe(self):
        assert geval([S('!='),5,5])==False
        assert geval([S('!='),5,7])==True

    def testCmpLt(self):
        assert geval([S('<'),5,3])==False
        assert geval([S('<'),5,5])==False
        assert geval([S('<'),5,7])==True

    def testCmpLe(self):
        assert geval([S('<='),5,3])==False
        assert geval([S('<='),5,5])==True
        assert geval([S('<='),5,7])==True

    def testCmpGt(self):
        assert geval([S('>'),5,3])==True
        assert geval([S('>'),5,5])==False
        assert geval([S('>'),5,7])==False

    def testCmpGe(self):
        assert geval([S('>='),5,3])==True
        assert geval([S('>='),5,5])==True
        assert geval([S('>='),5,7])==False

    def testCmpPlus(self):
        assert geval([S('+')])==0
        assert geval([S('+'),9])==9
        assert geval([S('+'),9,7])==16
        assert geval([S('+'),9,7,5])==21

    def testCmpMinus(self):
        assert geval([S('-')])==0
        assert geval([S('-'),9])==-9
        assert geval([S('-'),9,7])==2
        assert geval([S('-'),9,7,5])==-3

    def testCmpTimes(self):
        assert geval([S('*')])==1
        assert geval([S('*'),9])==9
        assert geval([S('*'),9,7])==63
        assert geval([S('*'),9,7,5])==315

    def testCmpIDiv(self):
        assert geval([S('//')])==1
        assert geval([S('//'),9])==0
        assert geval([S('//'),9,7])==1
        assert geval([S('//'),9,7,5])==0
        assert geval([S('//'),63,7])==9

    def testCmpFDiv(self):
        assert geval([S('/')])==1
        assert geval([S('/'),9])==1/9
        assert geval([S('/'),9,7])==9/7
        assert geval([S('/'),9,7,5])==(9/7)/5
        assert geval([S('/'),63,7])==9

    def testCmpMod(self):
        assert geval([S('%'),9,7])==2
        assert geval([S('%'),-9,7])==5

    def testCmpIn(self):
        assert geval([S('in'),9,[S('quote'),[17,3,9]]])==True
        assert geval([S('in'),5,[S('quote'),[17,3,9]]])==False

    def testGensym(self):
        fred1=geval([S('gensym'),"fred"])
        gensym.nextId=1
        gensym('skip')
        gensym('skip')
        fred2=gensym('fred')
        assert fred1 is fred2

    def testIndex(self):
        assert geval([S('[]'),[S('quote'),[17,3,9]],1])==3

    def testGetattr(self):
        o=O()
        o.x=17
        g=mkGlobals()
        g['o']=o
        assert geval([S('getattr'),S('o'),"x"],globalDict=g)==17

    def testSlice(self):
        l=[S('quote'),[2,4,8,16,32,64]]
        assert geval([S('slice'),l,3])==[16,32,64]
        assert geval([S('slice'),l,3,5])==[16,32]
        assert geval([S('slice'),l,3,-1])==[16,32]
        assert geval([S('slice'),l,None,3])==[2,4,8]
        assert geval([S('slice'),l,None,-2])==[2,4,8,16]

    def testToList(self):
        g=mkGlobals()
        g['x']=(2,3,5)
        assert geval([S('to-list'),S('x')],globalDict=g)==[2,3,5]

    def testToTuple(self):
        g=mkGlobals()
        g['x']=[2,3,5]
        assert geval([S('to-tuple'),S('x')],globalDict=g)==(2,3,5)

    def testToSet(self):
        g=mkGlobals()
        g['x']=(2,3,5)
        assert geval([S('to-set'),S('x')],globalDict=g)=={2,3,5}

    def testToDict(self):
        g=mkGlobals()
        g['x']=[['a',2],['b',3],['c',5]]
        assert geval([S('to-dict'),S('x')],globalDict=g)=={'a': 2,
                                                           'b': 3,
                                                           'c': 5}
    def testIsInstance(self):
        g=mkGlobals()
        g['x']=(2,3,5)
        assert geval([S('isinstance'),S('x'),S('python.tuple')],
                     globalDict=g)==True
        assert geval([S('isinstance'),S('x'),S('python.list')],
                     globalDict=g)==False

    def testMkList(self):
        assert geval([S('mk-list'),2,3,5])==[2,3,5]

    def testMkTuple(self):
        assert geval([S('mk-tuple'),2,3,5])==(2,3,5)

    def testMkSet(self):
        assert geval([S('mk-set'),2,3,5])=={2,3,5}

    def testMkDict(self):
        assert geval([S('mk-dict'),
                      S(':a'),2,
                      S(':b'),3,
                      S(':c'),5])=={'a': 2, 'b': 3, 'c': 5}

    def testMkSymbol(self):
        assert geval([S('mk-symbol'),"fred"]) is S('fred')

    def testReverse(self):
        g=mkGlobals()
        g['x']=[2,3,5]
        assert geval([S('reverse'),S('x')],globalDict=g)==[5,3,2]
        assert g['x']==[2,3,5]

    def testApply(self):
        def f(a,b,*,c,d):
            return [d,c,b,a]
        g=mkGlobals()
        g['f']=f
        assert geval([S('apply'),S('f'),
                      [S('quote'),[2,3]],
                      [S('mk-dict'),
                       S(':c'), 5,
                       S(':d'), 7]],
                     globalDict=g)==[7,5,3,2]

    def testAssign(self):
        g=mkGlobals()
        g['x']=0
        assert geval([S(':='),S('x'),9],globalDict=g)==9
        assert g['x']==9

    def testAssignDot(self):
        g=mkGlobals()
        g['x']=O()
        assert geval([S(':='),
                      [S('.'),S('x'),S('z')],
                      9],globalDict=g)==9
        assert g['x'].z==9

    def testAssignSubscript(self):
        g=mkGlobals()
        g['x']=[1,2,3]
        assert geval([S(':='),
                      [S('[]'),S('x'),1],
                      9],globalDict=g)==9
        assert g['x']==[1,9,3]

    def testBegin(self):
        g=mkGlobals()
        g['x']=0
        g['y']=1
        g['z']=2
        assert geval([S('begin'),
                      [S(':='),S('x'),9],
                      [S(':='),S('y'),7],
                      [S(':='),S('z'),[S('*'),S('x'),S('y')]],
                      [S('mk-list'),S('x'),S('y'),S('z')],
                      ],globalDict=g)==[9,7,63]

    def testImport(self):
        g=mkGlobals()
        assert geval([S('begin'),
                      [S('import'),S('sys')],
                      [S('.'),S('sys'),S('stdin')]
                      ],globalDict=g) is sys.stdin
        assert g['sys'] is sys

    def testDefun(self):
        (val,g)=self.e([S('defun'),S('f'),[S('a'),S('b')],
                        [S('+'),
                         [S('*'),S('a'),S('a')],
                         [S('*'),S('b'),S('b')]]])
        assert val is g['f']
        assert g['f'](3,4)==25

    def testDefunRecursive(self):
        (val,g)=self.e([S('defun'),S('fact'),[S('n')],
                        [S('if'),
                         [S('<'),S('n'),2],
                         1,
                         [S('*'),S('n'),[S('fact'),[S('-'),S('n'),1]]]
                         ]])
        assert val is g['fact']
        assert g['fact'](7)==5040

    def testIfElseTrue(self):
        (val,g)=self.e([S('if'),
                        [S('<'),5,7],
                        3,4])
        assert val==3

    def testIfElseFalse(self):
        (val,g)=self.e([S('if'),
                        [S('>'),5,7],
                        3,4])
        assert val==4

    def testIfNoElseTrue(self):
        (val,g)=self.e([S('if'),
                        [S('<'),5,7],
                        3])
        assert val==3

    def testIfNoElseFalse(self):
        (val,g)=self.e([S('if'),
                        [S('>'),5,7],
                        3])
        assert val is None

    def testLambda(self):
        (val,g)=self.e([S('lambda'),[S('n')],
                        [S('*'),S('n'),S('n')]])
        assert val(7)==49

    def testLambdaCall(self):
        (val,g)=self.e([[S('lambda'),[S('n')],
                         [S('*'),S('n'),S('n')]],
                        7])
        assert val==49

    def testQuoteInt(self):
        (val,g)=self.e([S('quote'),17])
        assert val==17

    def testQuoteString(self):
        (val,g)=self.e([S('quote'),'fibble'])
        assert val=='fibble'

    def testQuoteSymbol(self):
        (val,g)=self.e([S('quote'),S('fibble')])
        assert val is S('fibble')

    def testQuoteList(self):
        (val,g)=self.e([S('quote'),[S('bubble'),S('squeak')]])
        assert val==[S('bubble'),S('squeak')]

    def testTry1Exn(self):
        def razor(x):
            raise Exception(str(x))

        (val,g)=self.e([S('try'),
                        [S(':='),S('a'),17],
                        [S('razor'),23],
                        [S(':='),S('b'),19],
                        [S(':Exception'),S('e'),
                         [S('mk-tuple'),S('a'),S('e')]]],
                       razor=razor)
        assert g['a']==17
        assert 'b' not in g
        assert isinstance(val,tuple)
        assert val[0]==17
        assert isinstance(val[1],Exception)
        assert val[1].args==('23',)

    def testTry2Exn1(self):
        def razor(x):
            raise KeyError(str(x))

        (val,g)=self.e([S('try'),
                        [S(':='),S('a'),17],
                        [S('razor'),23],
                        [S(':='),S('b'),19],
                        [S(':KeyError'),S('ke'),
                         [S('mk-list'),S('a'),S('ke')]],
                        [S(':Exception'),S('e'),
                         [S('mk-tuple'),S('a'),S('e')]]],
                       razor=razor)
        assert g['a']==17
        assert 'b' not in g
        assert isinstance(val,list)
        assert val[0]==17
        assert isinstance(val[1],KeyError)
        assert val[1].args==('23',)

    def testTry2Exn2(self):
        def razor(x):
            raise Exception(str(x))

        (val,g)=self.e([S('try'),
                        [S(':='),S('a'),17],
                        [S('razor'),23],
                        [S(':='),S('b'),19],
                        [S(':KeyError'),S('ke'),
                         [S('mk-list'),S('a'),S('ke')]],
                        [S(':Exception'),S('e'),
                         [S('mk-tuple'),S('a'),S('e')]]],
                       razor=razor)
        assert g['a']==17
        assert 'b' not in g
        assert isinstance(val,tuple)
        assert val[0]==17
        assert isinstance(val[1],Exception)
        assert val[1].args==('23',)

    def testTry2Exn1Finally(self):
        def razor(x):
            raise KeyError(str(x))
        z=0
        def f(x):
            nonlocal z
            z=x

        (val,g)=self.e([S('try'),
                        [S(':='),S('a'),17],
                        [S('razor'),23],
                        [S(':='),S('b'),19],
                        [S(':KeyError'),S('ke'),
                         [S('mk-list'),S('a'),S('ke')]],
                        [S(':Exception'),S('e'),
                         [S('mk-tuple'),S('a'),S('e')]],
                        [S(':finally'),
                         [S('f'),[S('*'),S('a'),S('a')]]]
                        ],
                       razor=razor,
                       f=f)
        assert g['a']==17
        assert 'b' not in g
        assert isinstance(val,list)
        assert val[0]==17
        assert isinstance(val[1],KeyError)
        assert val[1].args==('23',)
        assert z==289

    def testTry0Exn1Finally(self):
        def razor(x):
            raise KeyError(str(x))
        z=0
        def f(x):
            nonlocal z
            z=x

        try:
            (val,g)=self.e([S('try'),
                            [S(':='),S('a'),17],
                            [S('razor'),23],
                            [S(':='),S('b'),19],
                            [S(':finally'),
                             [S('f'),[S('*'),S('a'),S('a')]]]
                            ],
                           razor=razor,
                           f=f)
            assert False
        except KeyError as ke:
            assert ke.args==('23',)

        assert z==289

    def testWhile(self):
        (val,g)=self.e([S('while'),
                        [S('<='),S('n'),7],
                        [S(':='),S('f'),[S('*'),S('n'),S('f')]],
                        [S(':='),S('n'),[S('+'),S('n'),1]],
                        S('f')],
                       f=1,n=1)
        assert val==5040
        assert g['f']==5040
        assert g['n']==8

    def testBreak(self):
        (val,g)=self.e([S('while'),
                        [S('<='),S('n'),7],
                        [S(':='),S('f'),[S('*'),S('n'),S('f')]],
                        [S(':='),S('n'),[S('+'),S('n'),1]],
                        [S('if'),[S('=='),S('n'),5],[S('break')]],
                        S('f')],
                       f=1,n=1)
        assert val is None
        assert g['f']==24
        assert g['n']==5

    def testContinue(self):
        (val,g)=self.e([S('while'),
                        [S('<='),S('n'),7],
                        [S(':='),S('f'),[S('*'),S('n'),S('f')]],
                        [S(':='),S('n'),[S('+'),S('n'),1]],
                        [S('if'),[S('=='),S('n'),5],[S('continue')]],
                        [[S('.'),S('sidebar'),S('append')],S('n')],
                        S('f')],
                       f=1,n=1,sidebar=[])
        assert val==5040
        assert g['f']==5040
        assert g['n']==8
        assert g['sidebar']==[2,3,4,6,7,8]

    def testYield(self):
        (val,g)=self.e([S('defun'),S('f'),[S('n')],
                        [S(':='),S('i'),1],
                        [S('while'),[S('<='),S('i'),S('n')],
                         [S('yield'),[S('*'),S('i'),S('i')]],
                         [S(':='),S('i'),[S('+'),S('i'),1]]]])
        assert 'f' in g
        assert val is g['f']
        assert list(g['f'](5))==[1,4,9,16,25]

    def testReturn(self):
        (val,g)=self.e([S('defun'),S('f'),[S('a'),S('b')],
                        [S('return'),[S('mk-list'),S('a'),S('b')]],
                        [S('+'),
                         [S('*'),S('a'),S('a')],
                         [S('*'),S('b'),S('b')]]])
        assert val is g['f']
        assert g['f'](3,4)==[3,4]

    def testReturn2(self):
        (val,g)=self.e([
                S('begin'),
                [S('defun'),S('f'),[S('x')],
                 [S('return'),S('x')]],
                [S('f'),9]
                ])
        assert val==9
        assert g['f'](17)==17

    def testAnd1(self):
        (val,g)=self.e([S('and'),5,False,S('nonesuch')])
        assert val is False

    def testAnd2(self):
        try:
            (val,g)=self.e([S('and'),5,True,S('nonesuch')])
        except NameError as ne:
            assert ne.args==("name 'nonesuch' is not defined",)

    def testAnd3(self):
        (val,g)=self.e([S('and'),5,True,S('gensym')])
        assert val is gensym

    def testOr1(self):
        (val,g)=self.e([S('or'),5,False,S('nonesuch')])
        assert val is 5

    def testOr2(self):
        try:
            (val,g)=self.e([S('or'),False,S('nonesuch'),5])
        except NameError as ne:
            assert ne.args==("name 'nonesuch' is not defined",)

    def testOr3(self):
        (val,g)=self.e([S('or'),False,S('gensym'),5])
        assert val is gensym

    def testDot1(self):
        o1=O()
        o2=O()
        o1.x=o2
        o2.y=17
        (val,g)=self.e([S('.'),S('o'),S('x')],o=o1)
        assert val is o2

    def testDot2(self):
        o1=O()
        o2=O()
        o1.x=o2
        o2.y=17
        (val,g)=self.e([S('.'),S('o'),S('x'),S('y')],o=o1)
        assert val==17

suite=unittest.TestSuite(
    ( 
      unittest.makeSuite(ReduceTestCase,'test'),
      unittest.makeSuite(ToPythonTestCase,'test'),
      unittest.makeSuite(EvalTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

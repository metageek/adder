#!/usr/bin/env python3

import unittest,pdb,sys,os
from adder.gomer import *
from adder.pyle import toPythonTree,toPythonFlat,flatten
from adder.common import Symbol as S,gensym
import adder.common

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
             [S('call'),S('f'),[2],[]],
             [S('begin')],
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
        self.verbose=False

    def tearDown(self):
        self.stmts=None

    def r(self,gomer,isStmt):
        res=reduce(gomer,isStmt,self.stmts.append)
        gensym.nextId=1
        return res

    def toP(self,gomer,isStmt):
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
            exprFlat=flatten(exprTree)
        else:
            (exprTree,exprFlat)=(None,None)

        if self.verbose:
            print()
            print(stmtTrees)
            print(stmtFlat)
            print(exprTree)
            print(exprFlat)
        return (stmtTrees,stmtFlat,exprTree,exprFlat)

    def testIntExpr(self):
        assert self.toP(7,False)==([],"","7","7\n")

    def testIntStmt(self):
        assert self.toP(7,True)==([],"",None,None)

    def testSymbolExpr(self):
        assert self.toP(S('fred'),False)==([],"","fred","fred\n")

    def testSymbolStmt(self):
        assert self.toP(S('fred'),True)==([],"",None,None)

    def testSimpleFuncExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1
        assert self.toP([S('fred'),7,8],False)==(
            ["%s=fred(7,8)" % scratchP],
            "%s=fred(7,8)\n" % scratchP,
            scratchP,"%s\n" % scratchP
            )

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

    def testQuoteNoneExpr(self):
        x=self.r([S('quote'),None],
                 False)

        assert x is None

    def testQuoteListExpr(self):
        actual=self.toP([S('quote'),[1,2,3]],
                        False)

        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        expected=(["%s=[1, 2, 3]" % scratchP],
                  "%s=[1, 2, 3]\n" % scratchP,
                  scratchP,"%s\n" % scratchP)
        assert actual==expected

    def testQuoteIntStmt(self):
        x=self.r([S('quote'),9],
                 True)

        assert x is None

    def testQuoteNoneStmt(self):
        x=self.r([S('quote'),None],
                 True)

        assert x is None

    def testQuoteListStmt(self):
        x=self.r([S('quote'),[1,2,3]],
                 True)

        assert x is None

    def testReturnStmt(self):
        x=self.r([S('return'),[S('*'),9,7]],
                 True)

        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('binop'),S('*'),9,7]],
            [S('return'),scratch],
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

    def testAnd1Expr(self):
        x=self.r([S('and'),S('x')],
                 False)

        assert x==S('x')

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
             [S('call'),S('f'),[2],[]],
             [S('begin')],
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

    def testOr1Expr(self):
        x=self.r([S('or'),S('x')],
                 False)

        assert x==S('x')

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

    def testVarDot1Stmt(self):
        x=self.r([S('.'),S('x'),S('y')],
                 True)

        scratch=gensym('scratch')
        assert x is None

    def testVarDot2Stmt(self):
        x=self.r([S('.'),S('x'),S('y'),S('z')],
                 True)

        scratch=gensym('scratch')
        assert x is None

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

    def testPlus1VarExpr(self):
        x=self.r([S('+'),5],
                 False)

        assert x==5

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

    def testTimes1VarExpr(self):
        x=self.r([S('*'),5],
                 False)

        assert x==5

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

    def testMinus1VarExpr(self):
        x=self.r([S('-'),5],
                 False)

        assert x==-5

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

    def testFdiv1VarExpr(self):
        x=self.r([S('/'),5],
                 False)

        assert x==1/5

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

    def testIdiv1VarExpr(self):
        x=self.r([S('//'),5],
                 False)

        assert x==0

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

    def testEquals1Expr(self):
        x=self.r([S('=='),5],
                 False)

        assert x is True

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

    def testSubscriptNestingStmt(self):
        x=self.r([S('[]'),S('l'),[S('+'),5,7]],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('binop'),S('+'),5,7]]
            ]

    def testSliceLExpr(self):
        actual=self.toP([S('slice'),S('l'),5],
                        False)

        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        expected=(
            ["%s=l[5:]" % scratchP],
            "%s=l[5:]\n" % scratchP,
            scratchP,"%s\n" % scratchP
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
            scratchP,"%s\n" % scratchP
            )
        assert actual==expected

    def testSliceLStmt(self):
        x=self.r([S('slice'),S('l'),5],
                 True)

        scratch=gensym('scratch')
        assert x is None

    def testSliceLRStmt(self):
        x=self.r([S('slice'),S('l'),5,7],
                 True)

        scratch=gensym('scratch')
        assert x is None

    def testToListStmt(self):
        assert self.toP([S('to-list'),S('l')],
                        True)==(
            [],"",
            None,None
            )

    def testToListExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('to-list'),S('l')],
                        False)==(
            ["%s=python.list(l)" % scratchP],
            "%s=python.list(l)\n" % scratchP,
            scratchP,"%s\n" % scratchP
            )

    def testToTupleStmt(self):
        assert self.toP([S('to-tuple'),S('l')],
                        True)==(
            [],"",
            None,None
            )

    def testToTupleExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('to-tuple'),S('l')],
                        False)==(
            ["%s=python.tuple(l)" % scratchP],
            "%s=python.tuple(l)\n" % scratchP,
            scratchP,"%s\n" % scratchP
            )

    def testToSetStmt(self):
        assert self.toP([S('to-set'),S('l')],
                        True)==(
            [],"",
            None,None
            )

    def testToSetExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('to-set'),S('l')],
                        False)==(
            ["%s=python.set(l)" % scratchP],
            "%s=python.set(l)\n" % scratchP,
            scratchP,"%s\n" % scratchP
            )

    def testToDictStmt(self):
        assert self.toP([S('to-dict'),S('l')],
                        True)==(
            [],"",
            None,None
            )

    def testToDictExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('to-dict'),S('l')],
                        False)==(
            ["%s=python.dict(l)" % scratchP],
            "%s=python.dict(l)\n" % scratchP,
            scratchP,"%s\n" % scratchP
            )

    def testIsinstanceStmt(self):
        assert self.toP([S('isinstance'),S('l'),S('list')],
                        True)==(
            [],"",
            None,None
            )

    def testIsinstanceExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('isinstance'),S('l'),S('list')],
                        False)==(
            ["%s=python.isinstance(l,list)" % scratchP],
            "%s=python.isinstance(l,list)\n" % scratchP,
            scratchP,"%s\n" % scratchP
            )

    def testMkListStmt(self):
        assert self.toP([S('mk-list'),S('l'),9,7],
                        True)==(
            [],"",
            None,None
            )

    def testMkListExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('mk-list'),S('l'),9,7],
                        False)==(
            ["%s=[l, 9, 7]" % scratchP],
            "%s=[l, 9, 7]\n" % scratchP,
            scratchP,"%s\n" % scratchP
            )

    def testMkTupleStmt(self):
        assert self.toP([S('mk-tuple'),S('l'),9,7],
                        True)==(
            [],"",
            None,None
            )

    def testMkTupleExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('mk-tuple'),S('l'),9,7],
                        False)==(
            ["%s=(l, 9, 7)" % scratchP],
            "%s=(l, 9, 7)\n" % scratchP,
            scratchP,"%s\n" % scratchP
            )

    def testMkSetStmt(self):
        assert self.toP([S('mk-set'),S('l'),9,7],
                        True)==(
            [],"",
            None,None
            )

    def testMkSetExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('mk-set'),S('l'),9,7],
                        False)==(
            ["%s={l, 9, 7}" % scratchP],
            "%s={l, 9, 7}\n" % scratchP,
            scratchP,"%s\n" % scratchP
            )

    def testMkDictStmt(self):
        assert self.toP([S('mk-dict'),S(':x'),9,S(':y'),7],
                        True)==(
            [],"",
            None,None
            )

    def testMkDictExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('mk-dict'),S(':x'),9,S(':y'),7],
                        False)==(
            ["%s={'x': 9, 'y': 7}" % scratchP],
            "%s={'x': 9, 'y': 7}\n" % scratchP,
            scratchP,"%s\n" % scratchP
            )

    def testMkSymbolStmt(self):
        assert self.toP([S('mk-symbol'),'l'],
                        True)==(
            [],"",
            None,None
            )

    def testMkSymbolExpr(self):
        scratch=gensym('scratch')
        scratchP=scratch.toPython()
        gensym.nextId=1

        assert self.toP([S('mk-symbol'),'l'],
                        False)==(
            ["%s=adder.common.Symbol('l')" % scratchP],
            "%s=adder.common.Symbol('l')\n" % scratchP,
            scratchP,"%s\n" % scratchP
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
            scratch1P,"%s\n" % scratch1P
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
            None,None)

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
            scratch1P,"%s\n" % scratch1P)
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
            None,None)

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
            scratch1P,"%s\n" % scratch1P)
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
            None,None)
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
            scratch1P,"%s\n" % scratch1P)
        assert actual==expected

class EvalTestCase(unittest.TestCase):
    def setUp(self):
        gensym.nextId=1

    def e(self,expr,verbose=False,**globalsToSet):
        g=mkGlobals()
        g.update(globalsToSet)
        return (geval(expr,globalDict=g,verbose=verbose),g)

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
        fred2=gensym('fred')
        assert fred1 is fred2

    def testIndex(self):
        assert geval([S('[]'),[S('quote'),[17,3,9]],1])==3

    def testGetattr(self):
        class O:
            pass
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
        class O:
            pass
        o1=O()
        o2=O()
        o1.x=o2
        o2.y=17
        (val,g)=self.e([S('.'),S('o'),S('x')],o=o1)
        assert val is o2

    def testDot2(self):
        class O:
            pass
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

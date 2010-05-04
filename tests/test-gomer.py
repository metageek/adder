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
            [S('print')]
            ]

    def testPrint1Stmt(self):
        x=self.r([S('print'),5],
                 True)

        assert x is None
        assert self.stmts==[
            [S('print'),5]
            ]

    def testPrint2Stmt(self):
        x=self.r([S('print'),5,[S('x'),12]],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('call'),S('x'),[12],[]]],
            [S('print'),5,scratch]
            ]

    def testPrint0Expr(self):
        x=self.r([S('print')],
                 False)

        assert x is None
        assert self.stmts==[
            [S('print')]
            ]

    def testPrint1Expr(self):
        x=self.r([S('print'),5],
                 False)

        assert x==5
        assert self.stmts==[
            [S('print'),5]
            ]

    def testPrint2Expr(self):
        x=self.r([S('print'),5,[S('x'),12]],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('call'),S('x'),[12],[]]],
            [S('print'),5,scratch]
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
            [S('print')]
            ]

    def testPrint1Stmt(self):
        x=self.r([S('print'),5],
                 True)

        assert x is None
        assert self.stmts==[
            [S('print'),5]
            ]

    def testPrint2Stmt(self):
        x=self.r([S('print'),5,[S('x'),12]],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('call'),S('x'),[12],[]]],
            [S('print'),5,scratch]
            ]

    def testPrint0Expr(self):
        x=self.r([S('print')],
                 False)

        assert x is None
        assert self.stmts==[
            [S('print')]
            ]

    def testPrint1Expr(self):
        x=self.r([S('print'),5],
                 False)

        assert x==5
        assert self.stmts==[
            [S('print'),5]
            ]

    def testPrint2Expr(self):
        x=self.r([S('print'),5,[S('x'),12]],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('call'),S('x'),[12],[]]],
            [S('print'),5,scratch]
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

suite=unittest.TestSuite(
    ( 
      unittest.makeSuite(ReduceTestCase,'test'),
      unittest.makeSuite(ToPythonTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

#!/usr/bin/env python3

import unittest,pdb,sys,os
from adder.compiler2 import Scope,annotate,stripAnnotations
from adder.common import Symbol as S, gensym
from adder.gomer import mkGlobals,geval
import adder.parser

def scopesToIds(scoped):
    scopes={}
    def walk(scoped):
        try:
            (expr,line,scope)=scoped
        except ValueError as ve:
            print(ve,scoped)
            raise

        if scope is not None:
            if isinstance(scope,tuple):
                print('scope tuple:',scope)
            if scope.id in scopes:
                assert scopes[scope.id] is scope
            else:
                scopes[scope.id]=scope
        if isinstance(expr,list):
            expr=list(map(walk,expr))
        return (expr,line,
                None if scope is None else scope.id
                )
    withIds=walk(scoped)
    keys=set(scopes.keys())
    if 0 in keys:
        assert keys==set(range(0,len(scopes)))
    else:
        assert keys==set(range(1,len(scopes)+1))
    return (withIds,scopes)

class AnnotateTestCase(unittest.TestCase):
    def setUp(self):
        Scope.nextId=1

    def annotate(self,exprPE,*,scope=None,verbose=False):
        if scope is None:
            scope=Scope(None)
        annotated=annotate(exprPE,scope)
        if verbose:
            print(annotated)
        return scopesToIds(annotated)

    def testInt(self):
        (scoped,scopes)=self.annotate((17,1))
        assert scoped==(17,1,1)
        assert isinstance(scopes,dict)
        assert len(scopes)==1
        assert len(scopes[1])==0

    def testStr(self):
        (scoped,scopes)=self.annotate(('foo',1))
        assert scoped==('foo',1,1)
        assert isinstance(scopes,dict)
        assert len(scopes)==1
        assert len(scopes[1])==0

    def testFloat(self):
        (scoped,scopes)=self.annotate((1.7,1))
        assert scoped==(1.7,1,1)
        assert isinstance(scopes,dict)
        assert len(scopes)==1
        assert len(scopes[1])==0

    def testBool(self):
        (scoped,scopes)=self.annotate((True,1))
        assert scoped==(True,1,1)
        assert isinstance(scopes,dict)
        assert len(scopes)==1
        assert len(scopes[1])==0

    def testVar(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        (scoped,scopes)=self.annotate((S('foo'),1),scope=scope)
        assert scoped==(S('foo'),1,1)
        assert isinstance(scopes,dict)
        assert len(scopes)==1
        assert scopes[1] is scope
        assert len(scopes[1])==1
        assert list(scopes[1])==[S('foo')]

    def testDefun(self):
        (scoped,scopes)=self.annotate(([(S('defun'),1),
                                        (S('foo'),1),
                                        ([(S('x'),1),
                                          (S('y'),1)
                                          ],1),
                                        ([(S('*'),2),(S('x'),2),(S('y'),2)],
                                         2)
                                        ],
                                       1))
        assert scoped==([(S('defun'),1,0),
                         (S('foo'),1,1),
                         ([(S('x'),1,2),
                           (S('y'),1,2)
                           ],1,1),
                         ([(S('*'),2,0),(S('x'),2,2),(S('y'),2,2)],2,2)
                         ],
                        1,1)
        assert isinstance(scopes,dict)
        assert len(scopes)==3
        assert scopes[0] is Scope.root
        assert list(scopes[1])==[S('foo')]
        assert sorted(scopes[2])==[S('x'),S('y')]
        assert scopes[2].parent is scopes[1]

    def testLambda(self):
        (scoped,scopes)=self.annotate(([(S('lambda'),1),
                                        ([(S('x'),1),
                                          (S('y'),1)
                                          ],1),
                                        ([(S('*'),2),(S('x'),2),(S('y'),2)],
                                         2)
                                        ],
                                       1))
        assert scoped==([(S('lambda'),1,0),
                         ([(S('x'),1,2),
                           (S('y'),1,2)
                           ],1,1),
                         ([(S('*'),2,0),(S('x'),2,2),(S('y'),2,2)],2,2)
                         ],
                        1,1)
        assert isinstance(scopes,dict)
        assert len(scopes)==3
        assert scopes[0] is Scope.root
        assert len(scopes[1])==0
        assert sorted(scopes[2])==[S('x'),S('y')]
        assert scopes[2].parent is scopes[1]

    def testLambdaCall(self):
        (scoped,scopes)=self.annotate(([
                                      ([(S('lambda'),1),
                                        ([(S('x'),1),
                                          (S('y'),1)
                                          ],1),
                                        ([(S('*'),2),(S('x'),2),(S('y'),2)],
                                         2)
                                        ],
                                       1),
                                      (9,3),(7,3)
                                      ],1))
        assert scoped==([
                ([(S('lambda'),1,0),
                  ([(S('x'),1,2),
                    (S('y'),1,2)
                    ],1,1),
                  ([(S('*'),2,0),(S('x'),2,2),(S('y'),2,2)],2,2)
                  ],
                 1,1),
                (9,3,1),(7,3,1)
                ],1,1)
        assert isinstance(scopes,dict)
        assert len(scopes)==3
        assert scopes[0] is Scope.root
        assert len(scopes[1])==0
        assert sorted(scopes[2])==[S('x'),S('y')]
        assert scopes[2].parent is scopes[1]

    def testDefvar(self):
        (scoped,scopes)=self.annotate(([(S('defvar'),1),
                                        (S('x'),1),
                                        (17,1)],
                                       1))
        assert scoped==([(S(':='),1,0),
                         (S('x'),1,1),
                         (17,1,1)
                         ],
                        1,1)
        assert isinstance(scopes,dict)
        assert len(scopes)==2
        assert scopes[0] is Scope.root
        assert sorted(scopes[1])==[S('x')]
        assert scopes[1].parent is scopes[0]
        entry=scopes[1][S('x')]
        assert entry.constValueValid
        assert entry.constValue==17
        assert not entry.asConst

    def testDefconst(self):
        (scoped,scopes)=self.annotate(([(S('defconst'),1),
                                        (S('x'),1),
                                        (17,1)],
                                       1))
        assert scoped==([(S(':='),1,0),
                         (S('x'),1,1),
                         (17,1,1)
                         ],
                        1,1)
        assert isinstance(scopes,dict)
        assert len(scopes)==2
        assert scopes[0] is Scope.root
        assert sorted(scopes[1])==[S('x')]
        assert scopes[1].parent is scopes[0]
        entry=scopes[1][S('x')]
        assert entry.constValueValid
        assert entry.constValue==17
        assert entry.asConst

    def testScopeTrivial(self):
        (scoped,scopes)=self.annotate(([(S('scope'),1),
                                        (17,1)],
                                       1))
        assert scoped==([(S('begin'),1,0),
                         (17,1,2)
                         ],
                        1,1)
        assert isinstance(scopes,dict)
        assert len(scopes)==3
        assert scopes[0] is Scope.root
        assert len(scopes[1])==0
        assert len(scopes[2])==0

    def testScopeOneVar(self):
        (scoped,scopes)=self.annotate(([(S('scope'),1),
                                        ([(S('defvar'),1),
                                          (S('x'),1),
                                          (17,1)],
                                         1)
                                        ],
                                       1))
        assert scoped==([(S('begin'),1,0),
                         ([(S(':='),1,0),
                           (S('x'),1,2),
                           (17,1,2)
                           ],
                          1,2)
                         ],
                        1,1)
        assert isinstance(scopes,dict)
        assert len(scopes)==3
        assert scopes[0] is Scope.root
        assert len(scopes[1])==0
        assert sorted(scopes[2])==[S('x')]
        entry=scopes[2][S('x')]
        assert entry.constValueValid
        assert entry.constValue==17

    def testScopeNested(self):
        (scoped,scopes)=self.annotate(([(S('scope'),1),
                                        ([(S('defvar'),1),
                                          (S('x'),1),
                                          (17,1)],
                                         1),
                                        ([(S('defvar'),1),
                                          (S('y'),1),
                                          (19,1)],
                                         1),
                                        ([(S('scope'),2),
                                          ([(S('defvar'),2),
                                            (S('x'),2),
                                            (23,2)],
                                           2)
                                          ],
                                         2)
                                        ],
                                       1))
        assert scoped==([(S('begin'),1,0),
                         ([(S(':='),1,0),
                           (S('x'),1,2),
                           (17,1,2)
                           ],
                          1,2),
                         ([(S(':='),1,0),
                           (S('y'),1,2),
                           (19,1,2)
                           ],
                          1,2),
                         ([(S('begin'),2,0),
                           ([(S(':='),2,0),
                             (S('x'),2,3),
                             (23,2,3)
                             ],
                            2,3)
                           ],
                          2,2)
                         ],
                        1,1)
        assert isinstance(scopes,dict)
        assert len(scopes)==4
        assert scopes[0] is Scope.root
        assert len(scopes[1])==0
        assert sorted(scopes[2])==[S('x'),S('y')]
        entry=scopes[2][S('x')]
        assert entry.constValueValid
        assert entry.constValue==17
        entry=scopes[2][S('y')]
        assert entry.constValueValid
        assert entry.constValue==19
        assert sorted(scopes[3])==[S('x')]
        entry=scopes[3][S('x')]
        assert entry.constValueValid
        assert entry.constValue==23
        entry=scopes[3][S('y')]
        assert entry.constValueValid
        assert entry.constValue==19

class EmptyStripTestCase(unittest.TestCase):
    def setUp(self):
        Scope.nextId=1

    def clarify(self,parsedExpr,*,scope=None,verbose=False):
        if scope is None:
            scope=Scope(None)
        annotated=annotate(parsedExpr,scope)
        res=stripAnnotations(annotated)
        if verbose:
            print(annotated)
            print(scopesToIds(annotated))
            print(res)
        return res

class StripTestCase(EmptyStripTestCase):
    def testInt(self):
        assert self.clarify((17,1))==17

    def testStr(self):
        assert self.clarify(('foo',1))=='foo'

    def testFloat(self):
        assert self.clarify((1.7,1))==1.7

    def testBool(self):
        assert self.clarify((True,1))==True

    def testVar(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify((S('foo'),1),scope=scope)==S('foo-1')

    def testDefun(self):
        assert self.clarify(([(S('defun'),1),
                              (S('foo'),1),
                              ([(S('x'),1),
                                (S('y'),1)
                                ],1),
                              ([(S('*'),2),(S('x'),2),(S('y'),2)],
                               2)
                              ],
                             1))==[S('defun'),S('foo-1'),
                                   [S('x-2'),S('y-2')],
                                   [S('*'),S('x-2'),S('y-2')]
                                   ]

    def testLambda(self):
        assert self.clarify(([(S('lambda'),1),
                              ([(S('x'),1),
                                (S('y'),1)
                                ],1),
                              ([(S('*'),2),(S('x'),2),(S('y'),2)],
                               2)
                              ],
                             1))==[S('lambda'),
                                   [S('x-2'),S('y-2')],
                                   [S('*'),S('x-2'),S('y-2')]
                                   ]

    def testDefvar(self):
        assert self.clarify(([(S('defvar'),1),
                              (S('x'),1),
                              (17,1)],
                             1))==[S(':='),S('x-1'),17]

    def testDefconst(self):
        assert self.clarify(([(S('defconst'),1),
                              (S('x'),1),
                              (17,1)],
                             1))==[S(':='),S('x-1'),17]

    def testScopeTrivial(self):
        assert self.clarify(([(S('scope'),1),
                              (17,1)],
                             1))==[S('begin'),17]

    def testScopeOneVar(self):
        assert self.clarify(([(S('scope'),1),
                              ([(S('defvar'),1),
                                (S('x'),1),
                                (17,1)],
                               1)
                              ],
                             1))==[S('begin'),
                                   [S(':='),S('x-2'),17]
                                   ]

    def testScopeNested(self):
        assert self.clarify(([(S('scope'),1),
                              ([(S('defvar'),1),
                                (S('x'),1),
                                (17,1)],
                               1),
                              ([(S('defvar'),1),
                                (S('y'),1),
                                (19,1)],
                               1),
                              ([(S('scope'),2),
                                ([(S('defvar'),2),
                                  (S('x'),2),
                                  (23,2)],
                                 2)
                                ],
                               2)
                              ],
                             1))==[S('begin'),
                                   [S(':='),S('x-2'),17],
                                   [S(':='),S('y-2'),19],
                                   [S('begin'),
                                    [S(':='),S('x-3'),23],
                                    ]
                                   ]

    def testQuoteInt(self):
        assert self.clarify(([(S('quote'),1),
                              (17,1)
                              ],1))==[S('quote'),17]

    def testQuoteList(self):
        assert self.clarify(([(S('quote'),1),
                              ([(S('x'),1),
                                (19,2),
                                (23,3)
                                ],
                               1)
                              ],1)
                            )==[S('quote'),[S('x'),19,23]]

    def testImport(self):
        assert self.clarify(([(S('import'),1),
                              (S('re'),1),
                              (S('pdb'),1)],
                             1))==[S('import'),S('re'),S('pdb')]

class ParseAndStripTestCase(EmptyStripTestCase):
    def clarify(self,exprStr,*,scope=None,verbose=False):
        if isinstance(exprStr,tuple):
            parsedExpr=exprStr
        else:
            parsedExpr=next(adder.parser.parse(exprStr))
        return StripTestCase.clarify(self,
                                     parsedExpr,
                                     scope=scope,
                                     verbose=verbose)

    def testInt(self):
        assert self.clarify('17')==17

    def testStr(self):
        assert self.clarify('"foo"')=='foo'

    def testFloat(self):
        assert self.clarify('1.7')==1.7

    def testPredefinedConst(self):
        assert self.clarify("true")==True

    def testVar(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("foo",scope=scope)==S('foo-1')

    def testDefun(self):
        assert self.clarify("""(defun foo (x y)
  (* x y))
""")==[S('defun'),S('foo-1'),
       [S('x-2'),S('y-2')],
       [S('*'),S('x-2'),S('y-2')]
       ]

    def testLambda(self):
        assert self.clarify("""(lambda (x y)
(* x y))
""")==[S('lambda'),
       [S('x-2'),S('y-2')],
       [S('*'),S('x-2'),S('y-2')]
       ]

    def testDefvar(self):
        assert self.clarify("(defvar x 17)")==[S(':='),S('x-1'),17]

    def testScopeTrivial(self):
        assert self.clarify("(scope 17)")==[S('begin'),17]

    def testScopeOneVar(self):
        assert self.clarify("(scope (defvar x 17))")==[
            S('begin'),
            [S(':='),S('x-2'),17]
            ]

    def testScopeNested(self):
        assert self.clarify("""(scope (defvar x 17) (defvar y 19)
(scope (defvar x 23)))
""")==[S('begin'),
       [S(':='),S('x-2'),17],
       [S(':='),S('y-2'),19],
       [S('begin'),
        [S(':='),S('x-3'),23],
        ]
       ]

    def testQuoteInt(self):
        assert self.clarify("(quote 17)")==[S('quote'),17]

    def testQuoteList(self):
        assert self.clarify("""(quote (x
19
23))""")==[S('quote'),[S('x'),19,23]]

    def testQuoteListWithApostrophe(self):
        assert self.clarify("""'(x
19
23)""")==[S('quote'),[S('x'),19,23]]

    def testImport(self):
        assert self.clarify("(import re pdb)")==[
        S('import'),S('re'),S('pdb')
        ]

    def testIf(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(if foo 9 7)",
                            scope=scope)==[S('if'),S('foo-1'),9,7]

    def testWhile(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(while foo (print foo))",
                            scope=scope)==[S('while'),S('foo-1'),
                                           [S('print'),S('foo-1')]
                                           ]

    def testBreak(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(while foo (print foo) (break))",
                            scope=scope)==[S('while'),S('foo-1'),
                                           [S('print'),S('foo-1')],
                                           [S('break')]
                                           ]

    def testContinue(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(while foo (print foo) (continue))",
                            scope=scope)==[S('while'),S('foo-1'),
                                           [S('print'),S('foo-1')],
                                           [S('continue')]
                                           ]

    def testBegin(self):
        assert self.clarify("""(begin
  (print 7)
  (print 9)
  (defvar x (* 9 7))
  (print x)
)
""")==[
            S('begin'),
            [S('print'),7],
            [S('print'),9],
            [S(':='),S('x-1'),[S('*'),9,7]],
            [S('print'),S('x-1')],
            ]

    def testYield(self):
        assert self.clarify("(defun foo (x) (yield x) (yield (* x x)))")==[
            S('defun'),S('foo-1'),[S('x-2')],
            [S('yield'),S('x-2')],
            [S('yield'),[S('*'),S('x-2'),S('x-2')]],
            ]

    def testReturn(self):
        assert self.clarify("(defun foo (x) (return x))")==[
            S('defun'),S('foo-1'),[S('x-2')],
            [S('return'),S('x-2')],
            ]

    def testRaise(self):
        assert self.clarify("(defun foo (x) (raise x))")==[
            S('defun'),S('foo-1'),[S('x-2')],
            [S('raise'),S('x-2')],
            ]

    def testAnd(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(and (>= foo 7) (<= foo 9))",
                            scope=scope)==[
            S('and'),
            [S('>='),S('foo-1'),7],
            [S('<='),S('foo-1'),9],
            ]

    def testOr(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(or (>= foo 7) (<= foo 9))",
                            scope=scope)==[
            S('or'),
            [S('>='),S('foo-1'),7],
            [S('<='),S('foo-1'),9],
            ]

    def testAssign(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(:= foo 9)",
                            scope=scope)==[
            S(':='),S('foo-1'),9
            ]

    def testDot(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(. foo x y)",
                            scope=scope)==[
            S('.'),S('foo-1'),S('x'),S('y')
            ]

    def testEquals(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(== foo 17)",
                            scope=scope)==[
            S('=='),S('foo-1'),17
            ]

    def testNotEquals(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(!= foo 17)",
                            scope=scope)==[
            S('!='),S('foo-1'),17
            ]

    def testLessThanOrEquals(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(<= foo 17)",
                            scope=scope)==[
            S('<='),S('foo-1'),17
            ]

    def testGreaterThanOrEquals(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(>= foo 17)",
                            scope=scope)==[
            S('>='),S('foo-1'),17
            ]

    def testLessThan(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(< foo 17)",
                            scope=scope)==[
            S('<'),S('foo-1'),17
            ]

    def testGreaterThan(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(> foo 17)",
                            scope=scope)==[
            S('>'),S('foo-1'),17
            ]

    def testPlus(self):
        assert self.clarify("(+ 9 7)")==[
            S('+'),9,7
            ]

    def testMinus(self):
        assert self.clarify("(- 9 7)")==[
            S('-'),9,7
            ]

    def testTimes(self):
        assert self.clarify("(* 9 7)")==[
            S('*'),9,7
            ]

    def testFDiv(self):
        assert self.clarify("(/ 9 7)")==[
            S('/'),9,7
            ]

    def testIDiv(self):
        assert self.clarify("(// 9 7)")==[
            S('//'),9,7
            ]

    def testMod(self):
        assert self.clarify("(% 9 7)")==[
            S('%'),9,7
            ]

    def testIn(self):
        assert self.clarify("(in 9 '(1 2 3))")==[
            S('in'),9,[S('quote'),[1,2,3]]
            ]

    def testPrint(self):
        assert self.clarify("(print 9 7)")==[
            S('print'),9,7
            ]

    def testGensym0(self):
        assert self.clarify('(gensym)')==[S('gensym')]

    def testGensym1(self):
        assert self.clarify('(gensym "foo")')==[
            S('gensym'),'foo'
            ]

    def testIndex(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify('([] foo 3)',
                            scope=scope)==[
            S('[]'),S('foo-1'),3
            ]

    def testGetattr(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify('(getattr foo "fred")',
                            scope=scope)==[
            S('getattr'),S('foo-1'),"fred"
            ]

    def testSlice1(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify('(slice foo 2)',
                            scope=scope)==[
            S('slice'),S('foo-1'),2
            ]

    def testSlice2(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify('(slice foo 2 3)',
                            scope=scope)==[
            S('slice'),S('foo-1'),2,3
            ]

    def testIsinstance(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        scope.addDef(S('str'),str,1)
        assert self.clarify('(isinstance foo str)',
                            scope=scope)==[
            S('isinstance'),S('foo-1'),S('str-1')
            ]

    def testList(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify('(list foo)',
                            scope=scope)==[
            S('list'),S('foo-1')
            ]

    def testTuple(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify('(tuple foo)',
                            scope=scope)==[
            S('tuple'),S('foo-1')
            ]

    def testSet(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify('(set foo)',
                            scope=scope)==[
            S('set'),S('foo-1')
            ]

    def testDict(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify('(dict foo)',
                            scope=scope)==[
            S('dict'),S('foo-1')
            ]

    def testMkList(self):
        assert self.clarify('(mk-list 9 7)')==[
            S('mk-list'),9,7
            ]

    def testMkTuple(self):
        assert self.clarify('(mk-tuple 9 7)')==[
            S('mk-tuple'),9,7
            ]

    def testMkSet(self):
        assert self.clarify('(mk-set 9 7)')==[
            S('mk-set'),9,7
            ]

    def testMkDict(self):
        assert self.clarify('(mk-dict :foo 9 :bar 7)')==[
            S('mk-dict'),S(':foo'),9,S(':bar'),7
            ]

    def testMkSymbol(self):
        assert self.clarify('(mk-symbol "fred")')==[
            S('mk-symbol'),"fred"
            ]

    def testReverse(self):
        assert self.clarify("(reverse '(1 2 3))")==[
            S('reverse'),[S('quote'),[1,2,3]]
            ]

    def testStdenv(self):
        assert self.clarify('(stdenv)')==[S('stdenv')]

    def testApply(self):
        scope=Scope(None)
        scope.addDef(S('f'),lambda a: a*a,1)
        assert self.clarify("(apply f '(2))",
                            scope=scope)==[
            S('apply'),S('f-1'),[S('quote'),[2]]
            ]

    def testApplyWithKwArgs(self):
        scope=Scope(None)
        scope.addDef(S('f'),lambda a,*,x,y: a*x*y,1)
        assert self.clarify("""
(apply f
       '(2)
       (mk-dict :x 9 :y 7))
""",
                            scope=scope)==[
            S('apply'),
            S('f-1'),
            [S('quote'),[2]],
            [S('mk-dict'),S(':x'),9,S(':y'),7]
            ]

    def testEval1(self):
        assert self.clarify("(eval '(* 9 7))")==[
            S('eval'),[S('quote'),[S('*'),9,7]]
            ]

    def testEval2(self):
        assert self.clarify("(eval '(* 9 7) (stdenv))")==[
            S('eval'),
            [S('quote'),[S('*'),9,7]],
            [S('stdenv')]
            ]

    def testExecPy(self):
        assert self.clarify('(exec-py "print(7)")')==[
            S('exec-py'),"print(7)"
            ]

    def testLoad(self):
        assert self.clarify('(load "prelude.+")')==[
            S('load'),"prelude.+"
            ]

class EvalTestCase(EmptyStripTestCase):
    def clarify(self,exprStr,*,scope=None,verbose=False):
        if isinstance(exprStr,tuple):
            parsedExpr=exprStr
        else:
            parsedExpr=next(adder.parser.parse(exprStr))
        return StripTestCase.clarify(self,
                                     parsedExpr,
                                     scope=scope,
                                     verbose=verbose)

    def evalAdder(self,exprStr,*,scope=None,verbose=False,**globalsToSet):
        if scope is None:
            scope=Scope(None)
        g=mkGlobals()
        for (k,v) in globalsToSet.items():
            scope.addDef(S(k),v,0)
            g[S("%s-1" % k).toPython()]=v
        gomer=self.clarify(exprStr,scope=scope,verbose=verbose)
        return geval(gomer,globalDict=g,verbose=verbose)

    def testInt(self):
        assert self.evalAdder('17')==17

    def testStr(self):
        assert self.evalAdder('"foo"')=='foo'

    def testFloat(self):
        assert self.evalAdder('1.7')==1.7

    def testPredefinedConst(self):
        assert self.evalAdder("true")==True

    def testVar(self):
        assert self.evalAdder("foo",foo=17)==17

    def testDefun(self):
        assert self.evalAdder("""(begin
(defun foo (x y)
  (* x y))
(foo 9 7)
)
""")==63

    def testLambda(self):
        assert self.evalAdder("""((lambda (x y)
(* x y)) 9 7)
""")==63

    def testDefvar(self):
        assert self.evalAdder("(begin (defvar x 17) x)")==17

    def testScopeTrivial(self):
        assert self.evalAdder("(scope 17)")==17

    def testScopeOneVar(self):
        assert self.evalAdder("(scope (defvar x 17) x)")==17

    def testScopeNested(self):
        assert self.evalAdder("""(scope (defvar x 17) (defvar y 19)
(scope (defvar x 23) x))
""")==23

    def testQuoteInt(self):
        assert self.evalAdder("(quote 17)")==17

    def testQuoteList(self):
        assert self.evalAdder("""(quote (x
19
23))""")==[S('x'),19,23]

    def testQuoteListWithApostrophe(self):
        assert self.evalAdder("""'(x
19
23)""")==[S('x'),19,23]

    def testImport(self):
        assert self.evalAdder("""
(begin
 (import adder.common)
 (. adder common Symbol)
)""") is S

    def testIfTrue(self):
        assert self.evalAdder("(if foo 9 7)",foo=True)==9

    def testIfFalse(self):
        assert self.evalAdder("(if foo 9 7)",foo=False)==7

    def testWhile(self):
        assert self.evalAdder("""
(begin
  (defvar fact 1)
  (defvar n 1)
  (while (<= n 7)
    (:= fact (* n fact))
    (:= n (+ n 1)))
  fact
  )
""")==5040

    def testBreak(self):
        assert self.evalAdder("""
(begin
  (defvar fact 1)
  (defvar n 2)
  (while (<= n 7)
    (:= fact (* n fact))
    (:= n (+ n 1))
    (break))
  fact
  )
""")==2

    def testContinue(self):
        assert self.evalAdder("""
(begin
  (defvar fact 1)
  (defvar n 1)
  (while (<= n 6)
    (:= n (+ n 1))
    (if (== n 5) (continue))
    (:= fact (* n fact)))
  fact
  )
""")==1008

    def testBegin(self):
        assert self.evalAdder("""(begin
  (defvar x (* 9 7))
  (:= x (* x 8))
)
""")==504

    def testYield(self):
        assert self.evalAdder("""
(begin
 (defun foo (x) (yield x) (yield (* x x)))
 (list (foo 7))
 )""")==[7,49]

    def testReturn(self):
        assert self.evalAdder("""
(begin
  (defun foo (x) (return x))
  (foo 9)
  )""")==9

    def testRaise(self):
        e=Exception('dummy')
        try:
            self.evalAdder("(raise e)",e=e)
            assert False
        except Exception as e2:
            assert e2 is e

    def testAnd1(self):
        assert self.evalAdder("(and (>= foo 7) (<= foo 9))",
                              foo=5)==False

    def testAnd2(self):
        assert self.evalAdder("(and (>= foo 7) (<= foo 9))",
                              foo=8)==True

    def testAnd3(self):
        assert self.evalAdder("(and (>= foo 7) (<= foo 9))",
                              foo=12)==False

    def testOr(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(or (>= foo 7) (<= foo 9))",
                            scope=scope)==[
            S('or'),
            [S('>='),S('foo-1'),7],
            [S('<='),S('foo-1'),9],
            ]

    def testAssign(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(:= foo 9)",
                            scope=scope)==[
            S(':='),S('foo-1'),9
            ]

    def testDot(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(. foo x y)",
                            scope=scope)==[
            S('.'),S('foo-1'),S('x'),S('y')
            ]

    def testEquals(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(== foo 17)",
                            scope=scope)==[
            S('=='),S('foo-1'),17
            ]

    def testNotEquals(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(!= foo 17)",
                            scope=scope)==[
            S('!='),S('foo-1'),17
            ]

    def testLessThanOrEquals(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(<= foo 17)",
                            scope=scope)==[
            S('<='),S('foo-1'),17
            ]

    def testGreaterThanOrEquals(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(>= foo 17)",
                            scope=scope)==[
            S('>='),S('foo-1'),17
            ]

    def testLessThan(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(< foo 17)",
                            scope=scope)==[
            S('<'),S('foo-1'),17
            ]

    def testGreaterThan(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify("(> foo 17)",
                            scope=scope)==[
            S('>'),S('foo-1'),17
            ]

    def testPlus(self):
        assert self.clarify("(+ 9 7)")==[
            S('+'),9,7
            ]

    def testMinus(self):
        assert self.clarify("(- 9 7)")==[
            S('-'),9,7
            ]

    def testTimes(self):
        assert self.clarify("(* 9 7)")==[
            S('*'),9,7
            ]

    def testFDiv(self):
        assert self.clarify("(/ 9 7)")==[
            S('/'),9,7
            ]

    def testIDiv(self):
        assert self.clarify("(// 9 7)")==[
            S('//'),9,7
            ]

    def testMod(self):
        assert self.clarify("(% 9 7)")==[
            S('%'),9,7
            ]

    def testIn(self):
        assert self.clarify("(in 9 '(1 2 3))")==[
            S('in'),9,[S('quote'),[1,2,3]]
            ]

    def testPrint(self):
        assert self.clarify("(print 9 7)")==[
            S('print'),9,7
            ]

    def testGensym0(self):
        assert self.clarify('(gensym)')==[S('gensym')]

    def testGensym1(self):
        assert self.clarify('(gensym "foo")')==[
            S('gensym'),'foo'
            ]

    def testIndex(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify('([] foo 3)',
                            scope=scope)==[
            S('[]'),S('foo-1'),3
            ]

    def testGetattr(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify('(getattr foo "fred")',
                            scope=scope)==[
            S('getattr'),S('foo-1'),"fred"
            ]

    def testSlice1(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify('(slice foo 2)',
                            scope=scope)==[
            S('slice'),S('foo-1'),2
            ]

    def testSlice2(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify('(slice foo 2 3)',
                            scope=scope)==[
            S('slice'),S('foo-1'),2,3
            ]

    def testIsinstance(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        scope.addDef(S('str'),str,1)
        assert self.clarify('(isinstance foo str)',
                            scope=scope)==[
            S('isinstance'),S('foo-1'),S('str-1')
            ]

    def testList(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify('(list foo)',
                            scope=scope)==[
            S('list'),S('foo-1')
            ]

    def testTuple(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify('(tuple foo)',
                            scope=scope)==[
            S('tuple'),S('foo-1')
            ]

    def testSet(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify('(set foo)',
                            scope=scope)==[
            S('set'),S('foo-1')
            ]

    def testDict(self):
        scope=Scope(None)
        scope.addDef(S('foo'),None,1)
        assert self.clarify('(dict foo)',
                            scope=scope)==[
            S('dict'),S('foo-1')
            ]

    def testMkList(self):
        assert self.clarify('(mk-list 9 7)')==[
            S('mk-list'),9,7
            ]

    def testMkTuple(self):
        assert self.clarify('(mk-tuple 9 7)')==[
            S('mk-tuple'),9,7
            ]

    def testMkSet(self):
        assert self.clarify('(mk-set 9 7)')==[
            S('mk-set'),9,7
            ]

    def testMkDict(self):
        assert self.clarify('(mk-dict :foo 9 :bar 7)')==[
            S('mk-dict'),S(':foo'),9,S(':bar'),7
            ]

    def testMkSymbol(self):
        assert self.clarify('(mk-symbol "fred")')==[
            S('mk-symbol'),"fred"
            ]

    def testReverse(self):
        assert self.clarify("(reverse '(1 2 3))")==[
            S('reverse'),[S('quote'),[1,2,3]]
            ]

    def testStdenv(self):
        assert self.clarify('(stdenv)')==[S('stdenv')]

    def testApply(self):
        scope=Scope(None)
        scope.addDef(S('f'),lambda a: a*a,1)
        assert self.clarify("(apply f '(2))",
                            scope=scope)==[
            S('apply'),S('f-1'),[S('quote'),[2]]
            ]

    def testApplyWithKwArgs(self):
        scope=Scope(None)
        scope.addDef(S('f'),lambda a,*,x,y: a*x*y,1)
        assert self.clarify("""
(apply f
       '(2)
       (mk-dict :x 9 :y 7))
""",
                            scope=scope)==[
            S('apply'),
            S('f-1'),
            [S('quote'),[2]],
            [S('mk-dict'),S(':x'),9,S(':y'),7]
            ]

    def testEval1(self):
        assert self.clarify("(eval '(* 9 7))")==[
            S('eval'),[S('quote'),[S('*'),9,7]]
            ]

    def testEval2(self):
        assert self.clarify("(eval '(* 9 7) (stdenv))")==[
            S('eval'),
            [S('quote'),[S('*'),9,7]],
            [S('stdenv')]
            ]

    def testExecPy(self):
        assert self.clarify('(exec-py "print(7)")')==[
            S('exec-py'),"print(7)"
            ]

    def testLoad(self):
        assert self.clarify('(load "prelude.+")')==[
            S('load'),"prelude.+"
            ]

suite=unittest.TestSuite(
    ( 
      unittest.makeSuite(AnnotateTestCase,'test'),
      unittest.makeSuite(StripTestCase,'test'),
      unittest.makeSuite(ParseAndStripTestCase,'test'),
      unittest.makeSuite(EvalTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

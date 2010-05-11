#!/usr/bin/env python3

import unittest,pdb,sys,os
import adder.compiler2
from adder.common import Symbol as S, gensym

class AnnotateTestCase(unittest.TestCase):
    def setUp(self):
        adder.compiler2.Scope.nextId=1

    def scopesToIds(self,scoped):
        scopes={}
        def walk(scoped):
            try:
                (expr,line,scope)=scoped
            except ValueError as ve:
                print(ve,scoped)
                raise
            if scope.id in scopes:
                assert scopes[scope.id] is scope
            else:
                scopes[scope.id]=scope
            if isinstance(expr,list):
                expr=list(map(walk,expr))
            return (expr,line,scope.id)
        withIds=walk(scoped)
        assert sorted(list(scopes.keys()))==list(range(1,len(scopes)+1))
        return (withIds,scopes)

    def annotate(self,exprPE):
        scope=adder.compiler2.Scope(None)
        annotated=adder.compiler2.annotate(exprPE,scope)
        return self.scopesToIds(annotated)

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
        (scoped,scopes)=self.annotate((S('foo'),1))
        assert scoped==(S('foo'),1,1)
        assert isinstance(scopes,dict)
        assert len(scopes)==1
        assert len(scopes[1])==0

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
        assert scoped==([(S('defun'),1,1),
                         (S('foo'),1,1),
                         ([(S('x'),1,2),
                           (S('y'),1,2)
                           ],1,1),
                         ([(S('*'),2,2),(S('x'),2,2),(S('y'),2,2)],2,2)
                         ],
                        1,1)
        assert isinstance(scopes,dict)
        assert len(scopes)==2
        assert list(scopes[1])==[S('foo')]
        assert sorted(scopes[2])==[S('x'),S('y')]
        assert scopes[2].parent is scopes[1]

suite=unittest.TestSuite(
    ( 
      unittest.makeSuite(AnnotateTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

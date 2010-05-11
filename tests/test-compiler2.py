#!/usr/bin/env python3

import unittest,pdb,sys,os
import adder.compiler2

class AnnotateTestCase(unittest.TestCase):
    def setUp(self):
        adder.compiler2.Scope.nextId=1

    def scopesToIds(self,scoped):
        scopes={}
        def walk(scoped):
            (expr,line,scope)=scoped
            if scope.id in scopes:
                assert scopes[scope.id] is scope
            else:
                scopes[scope.id]=scope
            if isinstance(expr,list):
                expr=list(map(walk,expr))
            return (expr,line,scope.id)
        return (walk(scoped),scopes)

    def annotate(self,exprPE):
        scope=adder.compiler2.Scope(None)
        annotated=adder.compiler2.annotate(exprPE,scope)
        return self.scopesToIds(annotated)

    def testInt(self):
        (scoped,scopes)=self.annotate((17,1))
        assert scoped==(17,1,1)
        assert isinstance(scopes,dict)
        assert len(scopes)==1
        assert 1 in scopes
        assert len(scopes[1])==0

suite=unittest.TestSuite(
    ( 
      unittest.makeSuite(AnnotateTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

#!/usr/bin/env python3

# Testing Gomer/Pyle integration.

import unittest,pdb,sys,os
from adder.common import Symbol as S
import adder.stdenv,adder.common,adder.gomer,adder.pyle

class GomerToPythonTestCase(unittest.TestCase):
    def setUp(self):
        self.pyleStmtLists=[]
        self.pythonTrees=[]
        self.pythonFlat=''
        adder.common.gensym.nextId=1

    def tearDown(self):
        self.pyleStmtLists=None
        self.pythonTrees=None
        self.pythonFlat=None

    def compile(self,gomerList):
        gomerAST=adder.gomer.build(adder.gomer.Scope(None),
                                   gomerList)
        exprPyleList=gomerAST.compyle(self.pyleStmtLists.append)
        exprPyleAST=adder.pyle.buildExpr(exprPyleList)
        exprPython=exprPyleAST.toPython(False)
        for pyleList in self.pyleStmtLists:
            pyleAST=adder.pyle.buildStmt(pyleList)
            pythonTree=pyleAST.toPythonTree()
            self.pythonTrees.append(pythonTree)
            self.pythonFlat+=adder.pyle.flatten(pythonTree)
        return exprPython

    def testConstInt(self):
        assert self.compile(1)=='1'
        assert self.pythonFlat==''

    def testCallPlus(self):
        assert self.compile([S('+'),2,2])=='2+2'
        assert self.pythonFlat==''

suite=unittest.TestSuite(
    ( unittest.makeSuite(GomerToPythonTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

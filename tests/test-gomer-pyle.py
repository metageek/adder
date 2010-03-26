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
        self.exprPython=None
        adder.common.gensym.nextId=1

    def tearDown(self):
        self.pyleStmtLists=None
        self.pythonTrees=None
        self.pythonFlat=None
        self.exprPython=None

    def compile(self,gomerList):
        gomerAST=adder.gomer.build(adder.gomer.Scope(None),
                                   gomerList)
        exprPyleList=gomerAST.compyle(self.pyleStmtLists.append)
        exprPyleAST=adder.pyle.buildExpr(exprPyleList)
        self.exprPython=exprPyleAST.toPython(False)
        for pyleList in self.pyleStmtLists:
            pyleAST=adder.pyle.buildStmt(pyleList)
            pythonTree=pyleAST.toPythonTree()
            self.pythonTrees.append(pythonTree)
            self.pythonFlat+=adder.pyle.flatten(pythonTree)
        return self.exprPython

    def testConstInt(self):
        assert self.compile(1)=='1'
        assert self.pythonFlat==''

    def testCallEq(self):
        assert self.compile([S('=='),2,3])=='2==3'
        assert self.pythonFlat==''

    def testCallNe(self):
        assert self.compile([S('!='),2,3])=='2!=3'
        assert self.pythonFlat==''

    def testCallLt(self):
        assert self.compile([S('<'),2,3])=='2<3'
        assert self.pythonFlat==''

    def testCallLe(self):
        assert self.compile([S('<='),2,3])=='2<=3'
        assert self.pythonFlat==''

    def testCallGt(self):
        assert self.compile([S('>'),2,3])=='2>3'
        assert self.pythonFlat==''

    def testCallGe(self):
        assert self.compile([S('>='),2,3])=='2>=3'
        assert self.pythonFlat==''

    def testCallPlus(self):
        assert self.compile([S('+'),2,3])=='2+3'
        assert self.pythonFlat==''

    def testCallMinus(self):
        assert self.compile([S('-'),2,3])=='2-3'
        assert self.pythonFlat==''

    def testCallTimes(self):
        pdb.set_trace()
        assert self.compile([S('*'),2,3])=='2*3'
        assert self.pythonFlat==''

    def testCallFDiv(self):
        assert self.compile([S('/'),2,3])=='2/3'
        assert self.pythonFlat==''

    def testCallIDiv(self):
        assert self.compile([S('//'),2,3])=='2//3'
        assert self.pythonFlat==''

    def testCallMod(self):
        assert self.compile([S('%'),2,3])=='2%3'
        assert self.pythonFlat==''

    def testCallIn(self):
        assert self.compile([S('in'),2,3])=='2 in 3'
        assert self.pythonFlat==''

    def testCallRaise(self):
        assert self.compile([S('raise'),[S('Exception')]])==''
        assert self.pythonFlat=='raise Exception()\n'

suite=unittest.TestSuite(
    ( unittest.makeSuite(GomerToPythonTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

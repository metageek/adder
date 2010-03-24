#!/usr/bin/env python3

import unittest,pdb,sys,os
from adder.pyle import *

class ExprTestCase(unittest.TestCase):
    def testInt(self):
        expr=Constant(17)
        assert expr.toPython(False)=='17'
        assert expr.toPython(True)=='17'

    def testStr(self):
        expr=Constant('fred')
        assert expr.toPython(False)=="'fred'"
        assert expr.toPython(True)=="'fred'"

    def testPlusExpr(self):
        expr=BinaryOperator('*',Constant(9),Constant(7))
        assert expr.toPython(False)=="9 * 7"
        assert expr.toPython(True)=="(9 * 7)"

suite=unittest.TestSuite(
    ( unittest.makeSuite(ExprTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

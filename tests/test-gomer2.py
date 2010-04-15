#!/usr/bin/env python3

import unittest,pdb,sys,os
from adder.gomer2 import *
from adder.common import Symbol as S
import adder.common

class StrTestCase(unittest.TestCase):
    def testVar(self):
        assert str(Var(S('fred')))=='fred'

    def testLiteralInt(self):
        assert str(Literal(9))=='9'

    def testLiteralSym(self):
        assert str(Literal(S('fred')))=="adder.common.Symbol('fred')"

    def testCallBare(self):
        print(str(Call(Var(S('fred')),Var(S('barney')),
                        [],[])))
        assert str(Call(Var(S('fred')),Var(S('barney')),
                        [],[]))=='fred=barney()'

suite=unittest.TestSuite(
    ( 
      unittest.makeSuite(StrTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

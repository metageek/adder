#!/usr/bin/env python3

import unittest,pdb,sys,os
from adder.pyle import *

class ExprTestCase(unittest.TestCase):
    def testInt(self):
        expr=Constant(17)
        assert expr.toPython(False)=='17'
        assert expr.toPython(True)=='17'

suite=unittest.TestSuite(
    ( unittest.makeSuite(ExprTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

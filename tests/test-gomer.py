#!/usr/bin/env python3

import unittest,pdb,sys,os
from adder.gomer import *
from adder.common import Symbol as S

class ScopeTestCase(unittest.TestCase):
    def testSimple(self):
        pass

suite=unittest.TestSuite(
    ( unittest.makeSuite(ScopeTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

#!/usr/bin/env python3

import unittest,pdb,sys,os
from adder.common import Symbol as S
import adder.common

class SymbolTestCase(unittest.TestCase):
    def testBasic(self):
        foo=S('foo')
        assert str(foo)=='foo'

    def testSingleton(self):
        foo1=S('foo')
        foo2=S('foo')
        assert foo1 is foo2
        assert foo1==foo2

    def testEq(self):
        foo=S('foo')
        bar=S('bar')
        assert foo!=bar
        assert foo is not bar

suite=unittest.TestSuite(
    ( 
      unittest.makeSuite(SymbolTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

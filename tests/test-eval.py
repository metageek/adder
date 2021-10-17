#!/usr/bin/env python3

import unittest

from adder.env import Env
from adder.symbol import intern
from adder.eval import evaluate

def total(*args):
    return sum(args)

def prod(*args):
    res=1
    for a in args:
        res *= a
    return res

class SimpleTestCase(unittest.TestCase):
    def __init__(self, arg):
        unittest.TestCase.__init__(self, arg)
        self.root={'+': total, '*': prod}

    def testSimpleSums(self):
        assert evaluate([intern('+')], self.root) == 0
        assert evaluate([intern('+'), 1], self.root) == 1
        assert evaluate([intern('+'), 1, 2], self.root) == 3
        assert evaluate([intern('+'), 1, 2, 3], self.root) == 6
        assert evaluate([intern('+'), 1, 2, 3, 4], self.root) == 10

    def testSimpleProds(self):
        assert evaluate([intern('*')], self.root) == 1
        assert evaluate([intern('*'), 1], self.root) == 1
        assert evaluate([intern('*'), 1, 2], self.root) == 2
        assert evaluate([intern('*'), 1, 2, 3], self.root) == 6
        assert evaluate([intern('*'), 1, 2, 3, 4], self.root) == 24

    def testNested(self):
        assert evaluate([intern('*'),
                         [intern('+'), 4, 5],
                         [intern('+'), 3, 4]], self.root) == 63

suite=unittest.TestSuite(
    ( unittest.makeSuite(SimpleTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

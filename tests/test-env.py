#!/usr/bin/env python3

import unittest

from adder.env import Env

class RootTestCase(unittest.TestCase):
    def testEmpty(self):
        root=Env()
        assert len(root) == 0
        assert len(list(root.values())) == 0
        assert len(list(root.keys())) == 0
        assert len(list(root.items())) == 0

        thrown=False
        
        try:
            assert root['fred'] == None
        except KeyError as e:
            assert e.args==('fred',)

    def testNonempty(self):
        root=Env()

        assert root.bind('fred', 35) == 35
        assert root['fred'] == 35
        
        assert len(root) == 1
        assert len(list(root.values())) == 1
        assert len(list(root.keys())) == 1
        assert len(list(root.items())) == 1

        assert root.bind('barney', 34) == 34
        assert root['barney'] == 34

        assert root['barney'] == 34
        assert root['fred'] == 35
        
        assert len(root) == 2
        assert len(list(root.values())) == 2
        assert len(list(root.keys())) == 2
        assert len(list(root.items())) == 2

        assert sorted(root.keys()) == ['barney', 'fred']
        assert sorted(root.values()) == [34, 35]
        assert sorted(root.items()) == [('barney', 34), ('fred', 35)]

        thrown=False
        
        try:
            assert root['wilma'] == None
        except KeyError as e:
            assert e.args==('wilma',)

    def testSet(self):
        root=Env()

        assert root.bind('fred', 35) == 35
        assert root['fred'] == 35
        root['fred'] = 37
        assert root['fred'] == 37
        
        assert len(root) == 1
        assert len(list(root.values())) == 1
        assert len(list(root.keys())) == 1
        assert len(list(root.items())) == 1

class ChildTestCase(unittest.TestCase):
    def testRootEmpty(self):
        root=Env()
        child=Env(root)

        assert child.bind('fred', 35) == 35

        assert len(root) == 0
        assert len(child) == 1

    def testRootNonemptyBind(self):
        root=Env()
        assert root.bind('fred', 37) == 37
        child = Env(root)

        assert child.bind('fred', 23) == 23

        assert root['fred'] == 37
        assert child['fred'] == 23

        assert len(root) == 1
        assert len(child) == 1

        assert sorted(root.items()) == [('fred', 37)]
        assert sorted(child.items()) == [('fred', 23)]

    def testRootNonemptySet(self):
        root=Env()
        assert root.bind('fred', 37) == 37
        child = Env(root)

        assert root['fred'] == 37
        assert child['fred'] == 37

        assert sorted(root.items()) == [('fred', 37)]
        assert sorted(child.items()) == [('fred', 37)]

        child['fred'] = 23

        assert root['fred'] == 23
        assert child['fred'] == 23

        assert len(root) == 1
        assert len(child) == 1

        assert sorted(root.items()) == [('fred', 23)]
        assert sorted(child.items()) == [('fred', 23)]

    def testRootNonemptyOverlapping(self):
        root=Env()
        assert root.bind('fred', 37) == 37
        assert root.bind('wilma', 33) == 33
        assert root.bind('pebbles', 1) == 1

        child1 = Env(root)
        assert child1.bind('fred', 23) == 23
        assert child1.bind('barney', 22) == 22

        child2 = Env(root)
        assert child2.bind('fred', 19) == 19
        assert child2.bind('betty', 15) == 15

        assert len(root) == 3
        assert len(child1) == 4
        assert len(child2) == 4

        assert sorted(root.items()) == [('fred', 37), ('pebbles', 1), ('wilma', 33)]
        assert sorted(child1.items()) == [('barney', 22), ('fred', 23), ('pebbles', 1), ('wilma', 33)]
        assert sorted(child2.items()) == [('betty', 15), ('fred', 19), ('pebbles', 1), ('wilma', 33)]

    def testRootNonemptyDict(self):
        root={'fred': 37, 'wilma': 33, 'pebbles': 1}
        child=Env(root)

        assert child.bind('fred', 23) == 23
        assert child.bind('barney', 22) == 22
        assert sorted(root.items()) == [('fred', 37), ('pebbles', 1), ('wilma', 33)]
        assert sorted(child.items()) == [('barney', 22), ('fred', 23), ('pebbles', 1), ('wilma', 33)]

        child['pebbles'] = 12
        assert sorted(root.items()) == [('fred', 37), ('pebbles', 12), ('wilma', 33)]
        assert sorted(child.items()) == [('barney', 22), ('fred', 23), ('pebbles', 12), ('wilma', 33)]
        

suite=unittest.TestSuite(
    ( unittest.makeSuite(RootTestCase,'test'),
      unittest.makeSuite(ChildTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

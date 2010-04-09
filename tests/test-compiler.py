#!/usr/bin/env python3

import unittest,pdb,sys,os
from adder.common import Symbol as S
import adder.compiler

class CompilingTestCase(unittest.TestCase):
    def loadPrelude(self):
        return False

    def setUp(self):
        adder.common.gensym.nextId=1
        adder.gomer.Scope.nextId=1
        self.context=adder.compiler.Context(loadPrelude=self.loadPrelude())

    def tearDown(self):
        self.context=None

class EvalTestCase(CompilingTestCase):
    def tearDown(self):
        CompilingTestCase.tearDown(self)
        self.runResult=None

    def runAdder(self,expr,*,verbose=False):
        self.runResult=self.context.eval(expr,verbose=verbose)
        return self.runResult

    def addDefs(self,*names):
        for name in names:
            if isinstance(name,tuple):
                (name,value)=name
            else:
                value=None
            self.context.addDef(name,value)

class WithoutPreludeTestCase(EvalTestCase):
    def testConstInt(self):
        assert self.runAdder(1)==1

    def testCallQuoteInt(self):
        assert self.runAdder([S('quote'),2])==2

    def testCallQuoteFloat(self):
        assert self.runAdder([S('quote'),2.7])==2.7

    def testCallQuoteStr(self):
        assert self.runAdder([S('quote'),"fred"])=="fred"

    def testCallQuoteSym(self):
        assert self.runAdder([S('quote'),S("fred")])==S("fred")
        assert isinstance(self.runResult,S)

    def testCallQuoteList(self):
        assert self.runAdder([S('quote'),[S("fred"),17]])==[S("fred"),17]
        assert isinstance(self.runResult[0],S)

    def testCallWhile(self):
        self.addDefs(('n',1),('l',[]))
        self.runAdder([S('while'),
                       [S('<'),S('n'),7],
                       [[S('.'),S('l'),S('append')],S('n')],
                       [S(':='),S('n'),[S('*'),S('n'),2]]
                       ])
        assert self.context['n']==8
        assert self.context['l']==[1,2,4]

    def testCallWhileBreak(self):
        self.addDefs(('n',1),('l',[]))
        self.runAdder([S('while'),
                       [S('<'),S('n'),7],
                       [[S('.'),S('l'),S('append')],S('n')],
                       [S('break')]
                       ])
        assert self.context['n']==1
        assert self.context['l']==[1]

    def testDot0(self):
        class O:
            pass

        o=O()

        self.addDefs(('o',o))
        assert self.runAdder([S('.'),S('o')]) is o

    def testDot1(self):
        class O:
            pass

        o=O()
        o.x=9

        self.addDefs(('o',o))
        assert self.runAdder([S('.'),S('o'),S('x')])==9

    def testDot3(self):
        class O:
            pass

        o=O()
        o.x=O()
        o.x.y=O()
        o.x.y.z=7

        self.addDefs(('o',o))
        assert self.runAdder([S('.'),S('o'),S('x'),S('y'),S('z')])==7

    def testCallBegin(self):
        self.addDefs('x')
        assert self.runAdder([S('begin'),
                              [S(':='),S('x'),7],
                              [S('*'),9,S('x')]])==63

    def testCallImport(self):
        self.runAdder([S('begin'),
                       [S('import'),S('os')]
                       ])
        assert self.context['os'] is os

    def testCallDefvar(self):
        assert self.runAdder([S('defvar'),S('x'),7])==7

    def testCallDefvarInScope(self):
        assert self.runAdder([S('begin'),
                              [S('defvar'),S('x'),7],
                              [S('scope'),
                               [S('defvar'),S('x'),9]
                               ]
                              ])==9

    def testCallEq(self):
        assert self.runAdder([S('=='),2,3])==False

    def testCallIf(self):
        assert self.runAdder([S('if'),[S('<'),5,7],2,3])==2

    def testCallNe(self):
        assert self.runAdder([S('!='),2,3])==True

    def testCallLt(self):
        assert self.runAdder([S('<'),2,3])==True

    def testCallLe(self):
        assert self.runAdder([S('<='),2,3])==True

    def testCallGt(self):
        assert self.runAdder([S('>'),2,3])==False

    def testCallGe(self):
        assert self.runAdder([S('>='),2,3])==False

    def testCallPlus(self):
        assert self.runAdder([S('+'),2,3])==5

    def testCallMinus(self):
        assert self.runAdder([S('-'),2,3])==-1

    def testCallTimes(self):
        assert self.runAdder([S('*'),2,3])==6

    def testCallFDiv(self):
        assert self.runAdder([S('/'),2,3])==2/3

    def testCallIDiv(self):
        assert self.runAdder([S('//'),2,3])==0

    def testCallMod(self):
        assert self.runAdder([S('%'),2,3])==2

    def testCallIn(self):
        self.addDefs(('l',[1,2,3]))
        assert self.runAdder([S('in'),2,S('l')])==True

    def testCallRaise(self):
        class X(Exception):
            pass

        self.context.addFuncDef('Exception',X)
        try:
            self.runAdder([S('raise'),[S('Exception'),17]])
        except X as e:
            assert e.args==(17,)

    def testCallReturn(self):
        assert self.runAdder([S('begin'),
                              [S('defun'),S('f'),[S('x')],
                               [S('return'),[S('*'),S('x'),7]],
                               12],
                              [S('f'),9]])==63

    def testCallYield(self):
        assert self.runAdder([S('begin'),
                              [S('defun'),S('f'),[S('x')],
                               [S('yield'),[S('*'),S('x'),7]],
                               [S('yield'),[S('+'),S('x'),7]]],
                              [S('list'),[S('f'),9]]])==[63,16]

    def testLambda(self):
        self.addDefs(('x',7))
        f=self.runAdder([S('lambda'),[S('n')],
                         [S('defvar'),S('res'),[S('*'),S('n'),S('x')]],
                         [S(':='),S('x'),[S('+'),S('x'),1]],
                         S('res')])
        assert self.context['x']==7
        assert f(9)==63
        assert self.context['x']==8
        assert f(9)==72
        assert self.context['x']==9

    def testCallGensym(self):
        adder.common.gensym.nextId=1
        self.runAdder([S('gensym'),[S('quote'),S('fred')]])
        adder.common.gensym.nextId=1
        assert self.runResult==adder.common.gensym(adder.common.Symbol('fred'))

    def testCallGetitem(self):
        self.addDefs(('l',[2,3,5,7]))
        assert self.runAdder([S('[]'),S('l'),3])==7

    def testCallGetattr(self):
        class O:
            def __init__(self):
                self.x=23

        o=O()

        self.addDefs(('o',o))
        assert self.runAdder([S('getattr'),S('o'),'x'])==23

    def testCallSlice1(self):
        self.addDefs(('l',[2,3,5,7]))
        assert self.runAdder([S('slice'),S('l'),1])==[3,5,7]

    def testCallSlice2(self):
        self.addDefs(('l',[2,3,5,7]))
        assert self.runAdder([S('slice'),S('l'),1,2])==[3]

    def testCallList(self):
        self.addDefs(('x',(2,3,5,7)))
        assert self.runAdder([S('list'),S('x')])==[2,3,5,7]

    def testCallTuple(self):
        self.addDefs(('x',[2,3,5,7]))
        assert self.runAdder([S('tuple'),S('x')])==(2,3,5,7)

    def testCallSet(self):
        self.addDefs(('x',[2,3,5,7]))
        assert self.runAdder([S('set'),S('x')])=={2,3,5,7}

    def testCallDict(self):
        assert self.runAdder([S('dict'),
                              [S('quote'),[[S('x'),17],[S('a'),23]]]
                              ])=={S('x'): 17, S('a'): 23}

    def testCallDictNoQuote(self):
        self.addDefs(('x',"fred"),('a',127))
        assert self.runAdder([S('dict'),
                              [S('mk-list'),
                               [S('mk-list'),S('x'),17],
                               [S('mk-list'),S('a'),23]
                               ]
                              ])=={'fred': 17, 127: 23}

    def testCallIsinstance(self):
        self.addDefs(('x',17),('str',str))
        assert self.runAdder([S('isinstance'),S('x'),S('str')])==False

    def testCallMkList(self):
        self.addDefs(('a',(5,7)))
        assert self.runAdder([S('mk-list'),S('a'),1,2,3])==[(5,7), 1, 2, 3]

    def testCallMkTuple(self):
        self.addDefs(('a',(5,7)))
        assert self.runAdder([S('mk-tuple'),S('a'),1,2,3])==((5,7), 1, 2, 3)

    def testCallMkSet(self):
        self.addDefs(('a',(5,7)))
        assert self.runAdder([S('mk-set'),S('a'),1,2,3])=={(5,7), 1, 2, 3}

    def testCallMkDict1(self):
        assert self.runAdder([S('mk-dict'),S(':a'),1,S(':b'),3])=={'a': 1, 'b': 3}

    def testCallMkDict2(self):
        assert self.runAdder([S('mk-dict'),
                              S(':b'),3,S(':a'),1
                              ])=={'a': 1, 'b': 3}
        
        
    def testCallMkSymbol(self):
        self.addDefs(('a',"fred"))
        assert self.runAdder([S('mk-symbol'),S('a')])==S('fred')

    def testCallReverse(self):
        self.addDefs(('l',[2,3,5,7]))
        assert self.runAdder([S('reverse'),S('l')])==[7,5,3,2]
        
    def testCallStdenv(self):
        self.runAdder([S('stdenv')])
        assert isinstance(self.runResult,adder.gomer.Env)
        assert self.runResult.parent is None
        assert self.runResult.scope.parent is None
        
    def testCallEvalPy(self):
        self.addDefs(('x',"23"))
        assert self.runAdder([S('eval-py'),S('x')])==23
        
    def testCallExecPy(self):
        self.addDefs(('x',"y=17"))
        assert self.runAdder([S('begin'),
                              [S('exec-py'),S('x')]
                              ]) is None
        assert self.context['y']==17
        
    def testCallApplyNoKw(self):
        self.context.addFuncDef('f',lambda a,b,c: a+b+c)
        assert self.runAdder([S('apply'),
                              S('f'),
                              [S('mk-list'),1,2,3]
                              ])==6
        
    def testCallApplyWithKw(self):
        def f(a,b,c,*,aWeight=1,bWeight=1,cWeight=1):
            return a*aWeight+b*bWeight+c*cWeight

        self.context.addFuncDef('f',f)
        self.runAdder([S('apply'),
                       S('f'),
                       [S('mk-list'),1,2,3],
                       [S('mk-dict'),S(':bWeight'),3,S(':bWeight'),5]
                       ])==14
        
    def testCallTryNoFinally(self):
        class XF(Exception):
            pass
        class XG(Exception):
            pass
        def f(x):
            raise XF(x)
        def g(x):
            raise XG(x)
        self.context.addFuncDef('f',f)
        self.context.addFuncDef('g',g)
        self.context.addFuncDef('XF',XF)
        self.context.addFuncDef('XG',XG)

        self.addDefs('xf','xg')

        self.runAdder([S('begin'),
                       [S('-gomer-try'),
                        [S('f'),7],
                        [S('g'),19],
                        S(':XF'),[S('ef'),[S(':='),S('xf'),S('ef')]],
                        S(':XG'),[S('eg'),[S(':='),S('xg'),S('eg')]],
                        ]
                       ]
                      )
        assert 'xf' in self.context
        assert isinstance(self.context['xf'],XF)
        assert self.context['xf'].args==(7,)

    def testSimpleMacro(self):
        def and2Transformer(args,kwArgs):
            assert len(args)==2
            assert not kwArgs
            return [S('if'),args[0],args[1],False]

        def stop():
            raise Exception('stop')

        self.context.addMacroDef('and2',and2Transformer)
        self.context.addFuncDef('stop',stop)

        assert not self.runAdder([S('and2'),False,False])
        assert not self.runAdder([S('and2'),False,True])
        assert not self.runAdder([S('and2'),False,[S('stop')]])
        assert not self.runAdder([S('and2'),True,False])
        assert self.runAdder([S('and2'),True,True])

    def testDefmacro(self):
        assert self.runAdder([S('defmacro'),
                              S('and2'),[S('a'),S('b')],
                              [S('if'),S('a'),S('b'),False]
                              ]) is None
        assert not self.runAdder([S('and2'),False,False])
        assert not self.runAdder([S('and2'),False,True])
        assert not self.runAdder([S('and2'),False,[S('stop')]])
        assert not self.runAdder([S('and2'),True,False])
        assert self.runAdder([S('and2'),True,True])

class PreludeTestCase(EvalTestCase):
    def loadPrelude(self):
        return True

    def testCallReverseBang(self):
        l=[2,3,5,7]
        self.addDefs(('l',l))
        assert self.runAdder([S('reverse!'),S('l')]) is l
        assert l==[7,5,3,2]
        
    def testCallHead(self):
        self.addDefs(('l',[2,3,5,7]))
        assert self.runAdder([S('head'),S('l')])==2

    def testCallTail(self):
        self.addDefs(('l',[2,3,5,7]))
        assert self.runAdder([S('tail'),S('l')])==[3,5,7]

    def testCallCond(self):
        assert self.runAdder([S('cond'),
                              [[S('<'),5,7],9],
                              [True,12]
                              ])==9

    def testConstantStdin(self):
        assert self.runAdder(S('stdin')) is sys.stdin

    def testConstantStdout(self):
        assert self.runAdder(S('stdout')) is sys.stdout

    def testConstantStderr(self):
        assert self.runAdder(S('stderr')) is sys.stderr

    def testConstantTypeList(self):
        assert self.runAdder([S('.'),S('type-list')]) is list

    def testConstantTypeTuple(self):
        assert self.runAdder([S('.'),S('type-tuple')]) is tuple

    def testConstantTypeSet(self):
        assert self.runAdder([S('.'),S('type-set')]) is set

    def testConstantTypeDict(self):
        assert self.runAdder([S('.'),S('type-dict')]) is dict

    def testDotDot(self):
        class O:
            pass

        o=O()
        o.foo=O()
        o.foo.bar=17

        f=self.runAdder([S('..'),S('foo'),S('bar')])
        assert f(o)==17

    def testLetStar(self):
        return
        assert self.runAdder([S('let*'),
                              [[S('x'),9],
                               [S('y'),7],
                               [S('z'),[S('*'),S('x'),S('y')]]
                               ],
                              [S('mk-list'),S('z'),S('z')]],
                             verbose=True)==[63,63]

suite=unittest.TestSuite(
    ( 
        unittest.makeSuite(WithoutPreludeTestCase,"test"),
        unittest.makeSuite(PreludeTestCase,"test"),
     )
    )

unittest.TextTestRunner().run(suite)

#!/usr/bin/env python3

# Testing Gomer/Pyle integration.

import unittest,pdb,sys,os
from adder.common import Symbol as S
import adder.common,adder.gomer,adder.pyle,adder.runtime

class CompilingTestCase(unittest.TestCase):
    def setUp(self):
        self.pyleStmtLists=[]
        self.pythonTrees=[]
        self.pythonFlat=''
        self.exprPython=None
        adder.common.gensym.nextId=1
        adder.gomer.Scope.nextId=1
        self.verbose=False
        self.scope=adder.gomer.Scope(None)
        self.globals={'adder': adder,
                      'gensym': adder.common.gensym}

    def tearDown(self):
        self.pyleStmtLists=None
        self.pythonTrees=None
        self.pythonFlat=None
        self.exprPython=None
        self.verbose=None
        self.scope=None
        self.globals=None

    def addFuncDef(self,name,f):
        self.addDefs(name,
                     adder.gomer.Constant(self.scope,
                                          adder.gomer.PyleExpr(self.scope,
                                                               name)
                                          )
                     )
        self.globals[name]=f

    def addDefs(self,*names):
        for name in names:
            if isinstance(name,tuple):
                (name,value)=name
            else:
                value=None
            self.scope.addDef(S(name),
                              (None if (value is None)
                               else adder.gomer.Constant(self.scope,value)
                               )
                              )
            self.globals[name]=value

    def compile(self,gomerList):
        gomerAST=adder.gomer.build(self.scope,gomerList)
        self.exprPyleList=gomerAST.compyle(self.pyleStmtLists.append)
        if self.verbose:
            print(self.exprPyleList)
        if self.exprPyleList:
            self.exprPyleAST=adder.pyle.buildExpr(self.exprPyleList)
            self.exprPython=self.exprPyleAST.toPython(False)
        else:
            self.exprPython=None
        if self.verbose:
            print(repr(self.exprPython))
            print(repr(self.pyleStmtLists))
        for pyleList in self.pyleStmtLists:
            pyleAST=adder.pyle.buildStmt(pyleList)
            pythonTree=pyleAST.toPythonTree()
            self.pythonTrees.append(pythonTree)
            self.pythonFlat+=adder.pyle.flatten(pythonTree)
        if self.verbose:
            print(repr(self.pythonTrees))
        return self.exprPython

class GomerToPythonTestCase(CompilingTestCase):
    def testConstInt(self):
        assert self.compile(1)=='1'
        assert self.pythonFlat==''

    def testCallQuoteInt(self):
        self.compile([S('quote'),2])
        assert self.exprPython=='2'
        assert self.pythonFlat==''

    def testCallQuoteFloat(self):
        self.compile([S('quote'),2.7])
        # Not an exact string match on x86-64.
        assert float(self.exprPython)==2.7
        assert self.pythonFlat==''

    def testCallQuoteStr(self):
        self.compile([S('quote'),"fred"])
        assert self.exprPython=="'fred'"
        assert self.pythonFlat==''

    def testCallQuoteSym(self):
        self.compile([S('quote'),S("fred")])
        assert self.exprPython=="adder.common.Symbol('fred')"
        assert self.pythonFlat==''

    def testCallQuoteList(self):
        self.compile([S('quote'),[S("fred"),17]])
        assert self.exprPython=="[adder.common.Symbol('fred'), 17]"
        assert self.pythonFlat==''

    def testCallIf(self):
        assert self.compile([S('if'),[S('<'),5,7],2,3])=='2 if (5<7) else 3'
        assert self.pythonFlat==''

    def testCallWhile(self):
        self.addDefs(('n',0))
        assert self.compile([S('while'),
                             [S('<'),S('n'),7],
                             [S('print'),S('n')],
                             [S(':='),S('n'),[S('+'),S('n'),1]]
                             ])==None
        assert self.pythonFlat=="""while n<7:
    print(n)
    n=n+1
"""

    def testCallWhileBreak(self):
        self.addDefs(('n',0))
        assert self.compile([S('while'),
                             [S('<'),S('n'),7],
                             [S('print'),S('n')],
                             [S('break')]
                             ])==None
        assert self.pythonFlat=="""while n<7:
    print(n)
    break
"""

    def testCallWhileContinue(self):
        self.addDefs(('n',0))
        assert self.compile([S('while'),
                             [S('<'),S('n'),7],
                             [S('print'),S('n')],
                             [S('continue')]
                             ])==None
        assert self.pythonFlat=="""while n<7:
    print(n)
    continue
"""

    def testDot0(self):
        self.addDefs('o')
        assert self.compile([S('.'),S('o')])=='o'
        assert not self.pythonFlat

    def testDot1(self):
        self.addDefs('o')
        assert self.compile([S('.'),S('o'),S('x')])=='o.x'
        assert not self.pythonFlat

    def testDot3(self):
        self.addDefs('o')
        assert self.compile([S('.'),S('o'),S('x'),S('y'),S('z')])=='o.x.y.z'
        assert not self.pythonFlat

    def testCallBegin(self):
        self.addDefs('x')
        self.compile([S('begin'),
                      [S(':='),S('x'),7],
                      [S('*'),9,S('x')]])
        scratch=S('#<gensym-scratch #1>').toPython()
        assert self.exprPython==scratch
        assert self.pythonFlat=="""x=7
%s=9*x
""" % scratch

    def testCallImport(self):
        self.compile([S('import'),S('os')])
        assert self.exprPython=='os'
        assert self.pythonFlat=="""import os
"""

    def testCallDefvar(self):
        self.compile([S('defvar'),S('x'),7])
        assert self.exprPython=='x'
        assert self.pythonFlat=="""x=7
"""

    def testCallDefvarInScope(self):
        self.compile([S('begin'),
                      [S('defvar'),S('x'),7],
                      [S('scope'),
                       [S('defvar'),S('x'),9]
                       ]
                      ])
        scratch1=S('#<gensym-scratch #1>').toPython()
        scratch2=S('#<gensym-scratch #2>').toPython()
        assert self.exprPython==scratch1
        assert self.pythonFlat=="""x=7
x_2=9
%s=x_2
%s=%s
""" % (scratch2,scratch1,scratch2)

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
        self.addDefs('Exception')
        assert self.compile([S('raise'),[S('Exception')]])==None
        assert self.pythonFlat=='raise Exception()\n'

    def testCallReturn(self):
        assert self.compile([S('return'),17])==None
        assert self.pythonFlat=='return 17\n'

    def testCallYield(self):
        assert self.compile([S('yield'),17])==None
        assert self.pythonFlat=='yield 17\n'

    def testCallPrint(self):
        assert self.compile([S('print'),17,19])=='print(17, 19)'
        assert self.pythonFlat==''

    def testCallGensym(self):
        self.compile([S('gensym'),[S('quote'),S('fred')]])
        assert self.exprPython=="gensym(adder.common.Symbol('fred'))"
        assert self.pythonFlat==''

    def testCallGetitem(self):
        self.addDefs('l')
        self.compile([S('[]'),S('l'),17])
        assert self.exprPython=="l[17]"
        assert self.pythonFlat==''

    def testCallGetattr(self):
        self.addDefs('o')
        self.compile([S('getattr'),S('o'),'x'])
        assert self.exprPython=="getattr(o, 'x')"
        assert self.pythonFlat==''

    def testCallSlice1(self):
        self.addDefs('l')
        self.compile([S('slice'),S('l'),17])
        assert self.exprPython=="l[17:]"
        assert self.pythonFlat==''

    def testCallSlice2(self):
        self.addDefs('l')
        self.compile([S('slice'),S('l'),17,23])
        assert self.exprPython=="l[17:23]"
        assert self.pythonFlat==''

    def testCallList(self):
        self.addDefs('x')
        self.compile([S('list'),S('x')])
        assert self.exprPython=="list(x)"
        assert self.pythonFlat==''

    def testCallTuple(self):
        self.addDefs('x')
        self.compile([S('tuple'),S('x')])
        assert self.exprPython=="tuple(x)"
        assert self.pythonFlat==''

    def testCallSet(self):
        self.addDefs('x')
        self.compile([S('set'),S('x')])
        assert self.exprPython=="set(x)"
        assert self.pythonFlat==''

    def testCallDict(self):
        self.compile([S('dict'),
                      [S('quote'),[[S('x'),17],[S('a'),23]]]
                      ])
        assert self.exprPython=="dict([[adder.common.Symbol('x'), 17], [adder.common.Symbol('a'), 23]])"
        assert self.pythonFlat==''

    def testCallIsinstance(self):
        self.addDefs('x','str')
        self.compile([S('isinstance'),S('x'),S('str')])
        assert self.exprPython=="isinstance(x, str)"
        assert self.pythonFlat==''

    def testCallMkList(self):
        self.addDefs('a')
        self.compile([S('mk-list'),S('a'),1,2,3])
        assert self.exprPython=="[a, 1, 2, 3]"
        assert self.pythonFlat==''

    def testCallMkTuple(self):
        self.addDefs('a')
        self.compile([S('mk-tuple'),S('a'),1,2,3])
        assert self.exprPython=="(a, 1, 2, 3)"
        assert self.pythonFlat==''

    def testCallMkSet(self):
        self.addDefs('a')
        self.compile([S('mk-set'),S('a'),1,2,3])
        assert self.exprPython=="{a, 1, 2, 3}"
        assert self.pythonFlat==''

    def testCallMkDict1(self):
        self.compile([S('mk-dict'),S(':a'),1,S(':b'),3])
        assert self.exprPython=="{'a': 1, 'b': 3}"
        assert self.pythonFlat==''

    def testCallMkDict2(self):
        self.compile([S('mk-dict'),S(':b'),3,S(':a'),1])
        assert self.exprPython=="{'a': 1, 'b': 3}"
        assert self.pythonFlat==''
        
    def testCallMkSymbol(self):
        self.addDefs('a')
        self.compile([S('mk-symbol'),S('a')])
        assert self.exprPython=="adder.common.Symbol(a)"
        assert self.pythonFlat==''

    def testCallReverse(self):
        self.addDefs('l')
        self.compile([S('reverse'),S('l')])
        assert self.exprPython=="adder.runtime.reverse(l)"
        assert self.pythonFlat==''
        
    def testCallReverseBang(self):
        self.addDefs('l')
        self.compile([S('reverse!'),S('l')])
        scratch=S('#<gensym-scratch #1>').toPython()
        assert self.exprPython==scratch
        assert self.pythonFlat==("""%s=l
%s.reverse()
""" % (scratch,scratch))
        
    def testCallStdenv(self):
        self.compile([S('stdenv')])
        assert self.exprPython=="adder.runtime.stdenv()"
        assert self.pythonFlat==''
        
    def testCallEvalPy(self):
        self.addDefs('x')
        self.compile([S('eval-py'),S('x')])
        assert self.exprPython=="eval(x)"
        assert self.pythonFlat==''
        
    def testCallExecPy(self):
        self.addDefs('x')
        self.compile([S('exec-py'),S('x')])
        assert self.exprPython==None
        assert self.pythonFlat=='exec(x)\n'
        
    def testCallApplyNoKw(self):
        self.addDefs('f')
        self.compile([S('apply'),
                      S('f'),
                      [S('mk-list'),1,2,3]
                      ])
        assert self.exprPython=='f(*[1, 2, 3])'
        assert self.pythonFlat==''
        
    def testCallApplyWithKw(self):
        self.addDefs('f')
        self.compile([S('apply'),
                      S('f'),
                      [S('mk-list'),1,2,3],
                      [S('mk-dict'),S(':b'),3,S(':a'),1]
                      ])
        assert self.exprPython=="f(*[1, 2, 3], **{'a': 1, 'b': 3})"
        assert self.pythonFlat==""
        
    def testCallTryNoFinally(self):
        self.addDefs('f','g','foo','flip','bar','h')
        self.compile([S('-gomer-try'),
                      [S('f'),7],
                      [S('g'),19],
                      S(':Foo'),[S('foo'),
                                 [S('begin'),
                                  [S('print'),S('foo')],
                                  [S('flip')]
                                  ]
                                 ],
                      S(':Bar'),[S('bar'),[S('h'),S('bar')]],
                      ])
        scratch1=S('#<gensym-scratch #1>').toPython()
        scratch2=S('#<gensym-scratch #2>').toPython()
        scratch3=S('#<gensym-scratch #3>').toPython()
        assert self.exprPython==scratch1
        assert self.pythonFlat==("""%s=None
try:
    f(7)
    %s=g(19)
    %s=%s
except Foo as foo_2:
    print(foo_2)
    %s=flip()
except Bar as bar_3:
    h(bar_3)
""" % (scratch1,scratch2,scratch1,scratch2,scratch3))

    def testCallTryWithFinally(self):
        self.addDefs('f','g','foo','bar','h','pi')
        self.compile([S('-gomer-try'),
                      [S('f'),7],
                      [S('g'),19],
                      S(':Foo'),[S('foo'),[S('print'),S('foo')]],
                      S(':Bar'),[S('bar'),[S('h'),S('bar')]],
                      S(':finally'),[[S('pi')]],
                      ])
        scratch1=S('#<gensym-scratch #1>').toPython()
        scratch2=S('#<gensym-scratch #2>').toPython()
        assert self.exprPython==scratch1
        assert self.pythonFlat==("""%s=None
try:
    f(7)
    %s=g(19)
    %s=%s
except Foo as foo_2:
    print(foo_2)
except Bar as bar_3:
    h(bar_3)
finally:
    pi()
""" % (scratch1,scratch2,scratch1,scratch2))

class RunGomerTestCase(CompilingTestCase):
    def runGomer(self,gomerList):
        exprPython=self.compile(gomerList)
        if self.verbose:
            print('globals before',self.globals)
            print('self.pythonFlat',self.pythonFlat)
        if self.pythonFlat:
            exec(self.pythonFlat,self.globals)
        if self.verbose:
            print('globals after exec',self.globals)
            print('exprPython',type(exprPython),exprPython)
        if exprPython is not None:
            self.runResult=eval(exprPython,self.globals)
            if self.verbose:
                print(self.runResult)
            return self.runResult

    def testConstInt(self):
        assert self.runGomer(1)==1

    def testCallQuoteInt(self):
        assert self.runGomer([S('quote'),2])==2

    def testCallQuoteFloat(self):
        assert self.runGomer([S('quote'),2.7])==2.7

    def testCallQuoteStr(self):
        assert self.runGomer([S('quote'),"fred"])=="fred"

    def testCallQuoteSym(self):
        assert self.runGomer([S('quote'),S("fred")])==S("fred")
        assert isinstance(self.runResult,S)

    def testCallQuoteList(self):
        assert self.runGomer([S('quote'),[S("fred"),17]])==[S("fred"),17]
        assert isinstance(self.runResult[0],S)

    def testCallWhile(self):
        self.addDefs(('n',1),('l',[]))
        self.runGomer([S('while'),
                       [S('<'),S('n'),7],
                       [[S('.'),S('l'),S('append')],S('n')],
                       [S(':='),S('n'),[S('*'),S('n'),2]]
                       ])
        assert self.globals['n']==8
        assert self.globals['l']==[1,2,4]

    def testCallWhileBreak(self):
        self.addDefs(('n',1),('l',[]))
        self.runGomer([S('while'),
                       [S('<'),S('n'),7],
                       [[S('.'),S('l'),S('append')],S('n')],
                       [S('break')]
                       ])
        assert self.globals['n']==1
        assert self.globals['l']==[1]

    def testDot0(self):
        class O:
            pass

        o=O()

        self.addDefs(('o',o))
        assert self.runGomer([S('.'),S('o')]) is o
        assert not self.pythonFlat

    def testDot1(self):
        class O:
            pass

        o=O()
        o.x=9

        self.addDefs(('o',o))
        assert self.runGomer([S('.'),S('o'),S('x')])==9
        assert not self.pythonFlat

    def testDot3(self):
        class O:
            pass

        o=O()
        o.x=O()
        o.x.y=O()
        o.x.y.z=7

        self.addDefs(('o',o))
        assert self.runGomer([S('.'),S('o'),S('x'),S('y'),S('z')])==7
        assert not self.pythonFlat

    def testCallBegin(self):
        self.addDefs('x')
        assert self.runGomer([S('begin'),
                              [S(':='),S('x'),7],
                              [S('*'),9,S('x')]])==63

    def testCallImport(self):
        assert self.runGomer([S('import'),S('os')]) is os
        assert self.globals['os'] is os

    def testCallDefvar(self):
        assert self.runGomer([S('defvar'),S('x'),7])==7

    def testCallDefvarInScope(self):
        assert self.runGomer([S('begin'),
                              [S('defvar'),S('x'),7],
                              [S('scope'),
                               [S('defvar'),S('x'),9]
                               ]
                              ])==9

    def testCallEq(self):
        assert self.runGomer([S('=='),2,3])==False

    def testCallIf(self):
        assert self.runGomer([S('if'),[S('<'),5,7],2,3])==2

    def testCallNe(self):
        assert self.runGomer([S('!='),2,3])==True

    def testCallLt(self):
        assert self.runGomer([S('<'),2,3])==True

    def testCallLe(self):
        assert self.runGomer([S('<='),2,3])==True

    def testCallGt(self):
        assert self.runGomer([S('>'),2,3])==False

    def testCallGe(self):
        assert self.runGomer([S('>='),2,3])==False

    def testCallPlus(self):
        assert self.runGomer([S('+'),2,3])==5

    def testCallMinus(self):
        assert self.runGomer([S('-'),2,3])==-1

    def testCallTimes(self):
        assert self.runGomer([S('*'),2,3])==6

    def testCallFDiv(self):
        assert self.runGomer([S('/'),2,3])==2/3

    def testCallIDiv(self):
        assert self.runGomer([S('//'),2,3])==0

    def testCallMod(self):
        assert self.runGomer([S('%'),2,3])==2

    def testCallIn(self):
        self.addDefs(('l',[1,2,3]))
        assert self.runGomer([S('in'),2,S('l')])==True

    def testCallRaise(self):
        class X(Exception):
            pass

        self.addFuncDef('Exception',X)
        try:
            self.runGomer([S('raise'),[S('Exception'),17]])
        except X as e:
            assert e.args==(17,)

    def testCallReturn(self):
        assert self.runGomer([S('begin'),
                              [S('defun'),S('f'),[S('x')],
                               [S('return'),[S('*'),S('x'),7]],
                               12],
                              [S('f'),9]])==63

    def testCallYield(self):
        assert self.runGomer([S('begin'),
                              [S('defun'),S('f'),[S('x')],
                               [S('yield'),[S('*'),S('x'),7]],
                               [S('yield'),[S('+'),S('x'),7]]],
                              [S('list'),[S('f'),9]]])==[63,16]

    def testLambda(self):
        self.addDefs(('x',7))
        f=self.runGomer([S('lambda'),[S('n')],
                         [S('defvar'),S('res'),[S('*'),S('n'),S('x')]],
                         [S(':='),S('x'),[S('+'),S('x'),1]],
                         S('res')])
        assert self.globals['x']==7
        assert f(9)==63
        assert self.globals['x']==8
        assert f(9)==72
        assert self.globals['x']==9

    def testLambdaWithKw(self):
        self.addDefs(('x',7))
        f=self.runGomer([S('lambda'),[S('&key'),S('n')],
                         [S('defvar'),S('res'),[S('*'),S('n'),S('x')]],
                         [S(':='),S('x'),[S('+'),S('x'),1]],
                         S('res')])
        assert self.globals['x']==7
        assert f(n=9)==63
        assert self.globals['x']==8
        assert f(n=9)==72
        assert self.globals['x']==9

    def testCallGensym(self):
        self.runGomer([S('gensym'),[S('quote'),S('fred')]])
        adder.common.gensym.nextId=1
        assert self.runResult==adder.common.gensym(adder.common.Symbol('fred'))

    def testCallGetitem(self):
        self.addDefs(('l',[2,3,5,7]))
        assert self.runGomer([S('[]'),S('l'),3])==7

    def testCallGetattr(self):
        class O:
            def __init__(self):
                self.x=23

        o=O()

        self.addDefs(('o',o))
        assert self.runGomer([S('getattr'),S('o'),'x'])==23

    def testCallSlice1(self):
        self.addDefs(('l',[2,3,5,7]))
        assert self.runGomer([S('slice'),S('l'),1])==[3,5,7]

    def testCallSlice2(self):
        self.addDefs(('l',[2,3,5,7]))
        assert self.runGomer([S('slice'),S('l'),1,2])==[3]

    def testCallList(self):
        self.addDefs(('x',(2,3,5,7)))
        assert self.runGomer([S('list'),S('x')])==[2,3,5,7]

    def testCallTuple(self):
        self.addDefs(('x',[2,3,5,7]))
        assert self.runGomer([S('tuple'),S('x')])==(2,3,5,7)

    def testCallSet(self):
        self.addDefs(('x',[2,3,5,7]))
        assert self.runGomer([S('set'),S('x')])=={2,3,5,7}

    def testCallDict(self):
        assert self.runGomer([S('dict'),
                              [S('quote'),[[S('x'),17],[S('a'),23]]]
                              ])=={S('x'): 17, S('a'): 23}

    def testCallDictNoQuote(self):
        self.addDefs(('x',"fred"),('a',127))
        assert self.runGomer([S('dict'),
                              [S('mk-list'),
                               [S('mk-list'),S('x'),17],
                               [S('mk-list'),S('a'),23]
                               ]
                              ])=={'fred': 17, 127: 23}

    def testCallIsinstance(self):
        self.addDefs(('x',17),('str',str))
        assert self.runGomer([S('isinstance'),S('x'),S('str')])==False

    def testCallMkList(self):
        self.addDefs(('a',(5,7)))
        assert self.runGomer([S('mk-list'),S('a'),1,2,3])==[(5,7), 1, 2, 3]

    def testCallMkTuple(self):
        self.addDefs(('a',(5,7)))
        assert self.runGomer([S('mk-tuple'),S('a'),1,2,3])==((5,7), 1, 2, 3)

    def testCallMkSet(self):
        self.addDefs(('a',(5,7)))
        assert self.runGomer([S('mk-set'),S('a'),1,2,3])=={(5,7), 1, 2, 3}

    def testCallMkDict1(self):
        assert self.runGomer([S('mk-dict'),S(':a'),1,S(':b'),3])=={'a': 1, 'b': 3}

    def testCallMkDict2(self):
        assert self.runGomer([S('mk-dict'),
                              S(':b'),3,S(':a'),1
                              ])=={'a': 1, 'b': 3}
        
        
    def testCallMkSymbol(self):
        self.addDefs(('a',"fred"))
        assert self.runGomer([S('mk-symbol'),S('a')])==S('fred')

    def testCallReverse(self):
        self.addDefs(('l',[2,3,5,7]))
        assert self.runGomer([S('reverse'),S('l')])==[7,5,3,2]
        
    def testCallReverseBang(self):
        l=[2,3,5,7]
        self.addDefs(('l',l))
        assert self.runGomer([S('reverse!'),S('l')]) is l
        assert l==[7,5,3,2]
        
    def testCallStdenv(self):
        self.runGomer([S('stdenv')])
        assert isinstance(self.runResult,adder.gomer.Env)
        assert self.runResult.parent is None
        assert self.runResult.scope.parent is None
        
    def testCallEvalPy(self):
        self.addDefs(('x',"23"))
        assert self.runGomer([S('eval-py'),S('x')])==23
        
    def testCallExecPy(self):
        self.addDefs(('x',"y=17"))
        assert self.runGomer([S('exec-py'),S('x')]) is None
        assert self.globals['y']==17
        
    def testCallApplyNoKw(self):
        self.addFuncDef('f',lambda a,b,c: a+b+c)
        assert self.runGomer([S('apply'),
                              S('f'),
                              [S('mk-list'),1,2,3]
                              ])==6
        
    def testCallApplyWithKw(self):
        def f(a,b,c,*,aWeight=1,bWeight=1,cWeight=1):
            return a*aWeight+b*bWeight+c*cWeight

        self.addFuncDef('f',f)
        self.runGomer([S('apply'),
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
        self.addFuncDef('f',f)
        self.addFuncDef('g',g)
        self.addFuncDef('XF',XF)
        self.addFuncDef('XG',XG)

        self.addDefs('xf','xg')

        self.runGomer([S('-gomer-try'),
                       [S('f'),7],
                       [S('g'),19],
                       S(':XF'),[S('ef'),[S(':='),S('xf'),S('ef')]],
                       S(':XG'),[S('eg'),[S(':='),S('xg'),S('eg')]],
                       ])
        assert 'xf' in self.globals
        assert isinstance(self.globals['xf'],XF)
        assert self.globals['xf'].args==(7,)

    def testCallTryWithFinally(self):
        self.addDefs('f','g','foo','bar','h','pi')
        self.compile([S('-gomer-try'),
                      [S('f'),7],
                      [S('g'),19],
                      S(':Foo'),[S('foo'),[S('print'),S('foo')]],
                      S(':Bar'),[S('bar'),[S('h'),S('bar')]],
                      S(':finally'),[[S('pi')]],
                      ])
        scratch1=S('#<gensym-scratch #1>').toPython()
        scratch2=S('#<gensym-scratch #2>').toPython()
        assert self.exprPython==scratch1
        assert self.pythonFlat==("""%s=None
try:
    f(7)
    %s=g(19)
    %s=%s
except Foo as foo_2:
    print(foo_2)
except Bar as bar_3:
    h(bar_3)
finally:
    pi()
""" % (scratch1,scratch2,scratch1,scratch2))

    def testDefun(self):
        assert self.runGomer([S('begin'),
                              [S('defun'),S('fact'),[S('n')],
                               [S('if'),[S('<'),S('n'),2],
                                1,
                                [S('*'),S('n'),
                                 [S('fact'),
                                  [S('-'),S('n'),1]
                                  ]
                                 ]
                                ]
                               ],
                              [S('fact'),7]])==5040

    def testDefunWithKw(self):
        assert self.runGomer([S('begin'),
                              [S('defun'),S('fact'),[S('&key'),S('n')],
                               [S('if'),[S('<'),S('n'),2],
                                1,
                                [S('*'),S('n'),
                                 [S('fact'),
                                  S(':n'),[S('-'),S('n'),1]
                                  ]
                                 ]
                                ]
                               ],
                              [S('fact'),S(':n'),7]])==5040

class EvalTestCase(CompilingTestCase):
    def setUp(self):
        self.scope=adder.gomer.Scope(None)
        self.globals={'adder': adder,
                      'gensym': adder.common.gensym}

    def tearDown(self):
        self.scope=None
        self.globals=None

    def eval(self,expr):
        return adder.gomer.evalTopLevel(expr,self.scope,self.globals)

    def testSimple(self):
        assert self.eval([S('*'),9,7])==63

suite=unittest.TestSuite(
    ( unittest.makeSuite(GomerToPythonTestCase,"test"),
      unittest.makeSuite(RunGomerTestCase,"test"),
      unittest.makeSuite(EvalTestCase,"test"),
     )
    )

unittest.TextTestRunner().run(suite)

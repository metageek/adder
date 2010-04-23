#!/usr/bin/env python3

import unittest,pdb,sys,os
from adder.gomer import *
from adder.common import Symbol as S,gensym
import adder.common

class VarEntryTestCase(unittest.TestCase):
    def testConstValueSuccess(self):
        var=VarEntry('fred',Constant(None,17))
        val=var.constValue()
        assert val==17

    def testConstValueFailure(self):
        var=VarEntry('fred',Constant(None,17))
        var.markModified()
        try:
            val=var.constValue()
            assert False
        except NotConstant:
            pass

class ScopeTestCase(unittest.TestCase):
    def testIsDescendant(self):
        scope1=Scope(None)
        scope2=Scope(None)
        scope1_1=Scope(scope1)
        scope1_1_1=Scope(scope1_1)
        scope2_1=Scope(scope2)
        scope2_2=Scope(scope2)

        assert scope1.isDescendant(scope1)
        assert scope1_1.isDescendant(scope1)
        assert scope1_1_1.isDescendant(scope1)

        assert not scope1.isDescendant(scope1_1)
        assert scope1_1.isDescendant(scope1_1)
        assert scope1_1_1.isDescendant(scope1_1)

        assert not scope1.isDescendant(scope1_1_1)
        assert not scope1_1.isDescendant(scope1_1_1)
        assert scope1_1_1.isDescendant(scope1_1_1)

        assert not scope1.isDescendant(scope2)
        assert not scope1_1.isDescendant(scope2)
        assert not scope1_1_1.isDescendant(scope2)

        assert not scope1.isDescendant(scope2_1)
        assert not scope1_1.isDescendant(scope2_1)
        assert not scope1_1_1.isDescendant(scope2_1)

        assert not scope1.isDescendant(scope2_2)
        assert not scope1_1.isDescendant(scope2_2)
        assert not scope1_1_1.isDescendant(scope2_2)

    def testCommonAncestor(self):
        scope1=Scope(None)
        scope2=Scope(None)
        scope1_1=Scope(scope1)
        scope1_1_1=Scope(scope1_1)
        scope2_1=Scope(scope2)
        scope2_2=Scope(scope2)

        assert scope1.commonAncestor(scope1,errorp=False)==scope1
        assert scope1_1.commonAncestor(scope1,errorp=False)==scope1
        assert scope1_1_1.commonAncestor(scope1,errorp=False)==scope1

        assert scope1.commonAncestor(scope1_1,errorp=False)==scope1
        assert scope1_1.commonAncestor(scope1_1,errorp=False)==scope1_1
        assert scope1_1_1.commonAncestor(scope1_1,errorp=False)==scope1_1

        assert scope1.commonAncestor(scope1_1_1,errorp=False)==scope1
        assert scope1_1.commonAncestor(scope1_1_1,errorp=False)==scope1_1
        assert scope1_1_1.commonAncestor(scope1_1_1,errorp=False)==scope1_1_1

        assert not scope1.commonAncestor(scope2,errorp=False)
        assert not scope1_1.commonAncestor(scope2,errorp=False)
        assert not scope1_1_1.commonAncestor(scope2,errorp=False)

        assert not scope1.commonAncestor(scope2_1,errorp=False)
        assert not scope1_1.commonAncestor(scope2_1,errorp=False)
        assert not scope1_1_1.commonAncestor(scope2_1,errorp=False)

        assert not scope1.commonAncestor(scope2_2,errorp=False)
        assert not scope1_1.commonAncestor(scope2_2,errorp=False)
        assert not scope1_1_1.commonAncestor(scope2_2,errorp=False)

        assert scope2_1.commonAncestor(scope2_2)==scope2

    def testContainsLocal(self):
        scope=Scope(None)
        scope.addDef(S('fred'),Constant(scope,17))
        assert S('fred') in scope
        assert S('barney') not in scope

    def testContainsNonLocal(self):
        scope1=Scope(None)
        scope1_1=Scope(scope1)
        scope1.addDef(S('fred'),Constant(scope1,17))
        scope1_1.addDef(S('wilma'),Constant(scope1_1,13))
        assert S('fred') in scope1
        assert S('fred') in scope1_1
        assert S('wilma') not in scope1
        assert S('wilma') in scope1_1
        assert S('barney') not in scope1
        assert S('barney') not in scope1_1

    def testIsLocal(self):
        scope1=Scope(None)
        scope1_1=Scope(scope1)
        scope1.addDef(S('fred'),Constant(scope1,17))
        scope1_1.addDef(S('wilma'),Constant(scope1_1,13))
        assert scope1.isLocal(S('fred'))
        assert not scope1_1.isLocal(S('fred'))
        assert not scope1.isLocal(S('wilma'))
        assert scope1_1.isLocal(S('wilma'))
        assert not scope1.isLocal(S('barney'))
        assert not scope1_1.isLocal(S('barney'))

    def testGetItemLocal(self):
        scope=Scope(None)
        scope.addDef(S('fred'),Constant(scope,17))

        v=scope[VarRef(scope,S('fred'))]
        assert isinstance(v,VarEntry)
        assert v.name==S('fred')
        assert isinstance(v.initExpr,Constant)
        assert v.initExpr.value==17
        assert v.neverModified

        try:
            scope[VarRef(scope,S('barney'))]
            assert False
        except Undefined:
            pass

    def testGetItemNonLocal(self):
        scope1=Scope(None)
        scope1_1=Scope(scope1)
        scope1.addDef(S('fred'),Constant(scope1,17))
        scope1_1.addDef(S('wilma'),Constant(scope1_1,13))

        v=scope1[VarRef(scope1,S('fred'))]
        assert isinstance(v,VarEntry)
        assert v.name==S('fred')
        assert isinstance(v.initExpr,Constant)
        assert v.initExpr.value==17
        assert v.neverModified

        v=scope1_1[VarRef(scope1_1,S('fred'))]
        assert isinstance(v,VarEntry)
        assert v.name==S('fred')
        assert isinstance(v.initExpr,Constant)
        assert v.initExpr.value==17
        assert v.neverModified

        try:
            scope1[VarRef(scope1,S('wilma'))]
            assert False
        except Undefined:
            pass

        v=scope1_1[VarRef(scope1_1,S('wilma'))]
        assert isinstance(v,VarEntry)
        assert v.name==S('wilma')
        assert isinstance(v.initExpr,Constant)
        assert v.initExpr.value==13
        assert v.neverModified

        try:
            scope1[VarRef(scope1,S('barney'))]
            assert False
        except Undefined:
            pass

        try:
            scope1_1[VarRef(scope1_1,S('barney'))]
            assert False
        except Undefined:
            pass

    def testAddDefAfterUse(self):
        scope=Scope(None)
        fred1=VarRef(scope,S('fred'))
        scope.addRead(fred1)
        try:
            scope.addDef(S('fred'),Constant(scope,17))
            assert False
        except DefinedAfterUse:
            pass

    def testAddDefRedefined(self):
        scope=Scope(None)
        scope.addDef(S('fred'),Constant(scope,17))
        try:
            scope.addDef(S('fred'),Constant(scope,17))
            assert False
        except Redefined:
            pass

    def testAddRead(self):
        scope=Scope(None)
        assert list(scope.varAccesses.keys())==[]

        fred1=VarRef(scope,S('fred'))
        scope.addRead(fred1)

        assert list(scope.varAccesses.keys())==[S('fred')]
        assert len(scope.varAccesses[S('fred')])==1
        assert list(scope.varAccesses[S('fred')])[0] is fred1

    def testAddWrite(self):
        scope=Scope(None)
        fred0=VarRef(scope,S('fred'))
        scope.addDef(S('fred'),Constant(scope,17))
        assert scope[fred0].neverModified

        assert list(scope.varAccesses.keys())==[]

        fred1=VarRef(scope,S('fred'))
        scope.addWrite(fred1)

        assert list(scope.varAccesses.keys())==[S('fred')]
        assert len(scope.varAccesses[S('fred')])==1
        assert list(scope.varAccesses[S('fred')])[0] is fred1

        assert not scope[fred0].neverModified

    def testUndefinedVars(self):
        scope=Scope(None)
        assert list(scope.varAccesses.keys())==[]

        fred1=VarRef(scope,S('fred'))
        scope.addRead(fred1)

        assert list(scope.varAccesses.keys())==[S('fred')]
        assert len(scope.varAccesses[S('fred')])==1
        assert list(scope.varAccesses[S('fred')])[0] is fred1

        uvs=list(scope.undefinedVars())
        assert len(uvs)==1
        (v,accesses)=uvs[0]
        assert isinstance(v,S)
        assert v==S('fred')
        assert isinstance(accesses,set)
        assert len(accesses)==1
        assert list(accesses)[0] is fred1

class ExprTestCase(unittest.TestCase):
    def testConstantInt(self):
        scope=Scope(None)
        c=Constant(scope,5)
        assert c.constValue()==5
        assert c.scopeRequired() is None
        assert c.isPureIn(scope)
        assert list(c.varRefs())==[]

    def testConstantStr(self):
        scope=Scope(None)
        c=Constant(scope,'fred')
        assert c.constValue()=='fred'
        assert c.scopeRequired() is None
        assert c.isPureIn(scope)
        assert list(c.varRefs())==[]

    def testVarUnbound(self):
        scope=Scope(None)
        scope1=Scope(scope)
        v=VarRef(scope,S('fred'))
        assert len(list(v.varRefs()))==1
        assert list(v.varRefs())[0] is v
        assert not v.isPureIn(scope)
        assert not v.isPureIn(scope1)

        try:
            v.constValue()
            assert False
        except Undefined as u:
            assert u.varRef is v

        try:
            v.scopeRequired()
            assert False
        except Undefined as u:
            assert u.varRef is v

    def testVarBound(self):
        scope1=Scope(None)
        scope2=Scope(scope1)
        scope3=Scope(scope2)

        scope2.addDef(S('fred'),Constant(scope2,17))

        v=VarRef(scope2,S('fred'))

        assert len(list(v.varRefs()))==1
        assert list(v.varRefs())[0] is v

        assert v.isPureIn(scope1)
        assert v.isPureIn(scope2)
        assert v.isPureIn(scope3)

        assert v.constValue()==17
        assert v.scopeRequired()==scope2

        scope2[v].markModified()

        try:
            v.constValue()
            assert False
        except NotConstant as nc:
            assert nc.expr is v

        assert not v.isPureIn(scope3)

    def testCallNative(self):
        scope1=Scope(None)
        scope2=Scope(scope1)
        scope3=Scope(scope2)

        scope1.addDef(S('james1'),Constant(scope1,1603))
        scope2.addDef(S('charles1'),Constant(scope2,1625))
        scope3.addDef(S('charles2'),Constant(scope3,1649))

        scope2.addDef(S('l'),Constant(scope2,
                                      NativeFunction((lambda a,b,c:
                                                          [a,b,c]),
                                                     True)))

        call=Call(scope3,False,
                  VarRef(scope3,S('l')),
                  [VarRef(scope3,S('james1')),
                   VarRef(scope3,S('charles1')),
                   VarRef(scope3,S('charles2'))])

        assert call.constValue()==[1603,1625,1649]
        assert call.scopeRequired() is scope1
        assert call.isPureIn(scope3)

        vrs=list(call.varRefs())
        assert len(vrs)==4
        for vr in vrs:
            assert vr.scope==scope3

        assert list(map(lambda vr: vr.name,vrs))==[
            S('l'),S('james1'),S('charles1'),S('charles2')
            ]

    def testCallNativeWithKW(self):
        scope1=Scope(None)
        scope2=Scope(scope1)
        scope3=Scope(scope2)

        scope1.addDef(S('james1'),Constant(scope1,1603))
        scope2.addDef(S('charles1'),Constant(scope2,1625))
        scope3.addDef(S('charles2'),Constant(scope3,1649))

        scope2.addDef(S('l'),Constant(scope2,
                                      NativeFunction((lambda a,b,c,*,james2:
                                                          [a,b,c,james2]),
                                                     True)))

        call=Call(scope3,False,
                  VarRef(scope3,S('l')),
                  [VarRef(scope3,S('james1')),
                   VarRef(scope3,S('charles1')),
                   VarRef(scope3,S('charles2')),
                   VarRef(scope3,S(':james2')),Constant(scope3,'syphillis'),
                   ])

        assert len(call.posArgs)==3
        assert len(call.kwArgs)==1
        assert call.kwArgs[0][0]=='james2'

        assert call.constValue()==[1603,1625,1649,'syphillis']
        assert call.scopeRequired() is scope1
        assert call.isPureIn(scope3)

        vrs=list(call.varRefs())
        assert len(vrs)==4
        for vr in vrs:
            assert vr.scope==scope3

        assert list(map(lambda vr: vr.name,vrs))==[
            S('l'),S('james1'),S('charles1'),S('charles2')
            ]

    def testCallUser(self):
        scope1=Scope(None)
        scope2=Scope(scope1)
        scope3=Scope(scope2)
        scope4=Scope(scope2)

        env1=Env(scope1,None)
        env2=Env(scope2,env1)
        env3=Env(scope3,env2)

        scope1.addDef(S('james1'),Constant(scope1,1603))
        scope2.addDef(S('charles1'),Constant(scope2,1625))
        scope3.addDef(S('charles2'),Constant(scope3,1649))
        scope4.addFuncArg(S('a'))
        scope4.addFuncArg(S('b'))
        scope4.addFuncArg(S('c'))

        scope2.addDef(S('l'),Constant(scope2,
                                      NativeFunction((lambda a,b,c:
                                                          [a,b,c]),
                                                     True)))

        scope2.addDef(S('f'),
                      Constant(scope2,
                               UserFunction(scope2,
                                            [[VarRef(scope4,S('a')),
                                              VarRef(scope4,S('b')),
                                              VarRef(scope4,S('c'))],
                                             Call(scope4,False,
                                                  VarRef(scope4,S('l')),
                                                  [VarRef(scope4,S('c')),
                                                   VarRef(scope4,S('b')),
                                                   VarRef(scope4,S('a'))])],
                                            None,
                                            env3)))

        call=Call(scope3,False,
                  VarRef(scope3,S('f')),
                  [VarRef(scope3,S('james1')),
                   VarRef(scope3,S('charles1')),
                   VarRef(scope3,S('charles2'))])

        assert call.scopeRequired() is scope1
        assert call.isPureIn(scope3)
        assert call.evaluate(env3)==[1649,1625,1603]
        assert call.constValue()==[1649,1625,1603]

class BuildTestCase(unittest.TestCase):
    def testQuoteInt(self):
        scope=Scope(None)
        x=build(scope,[S('quote'),17],False)
        assert isinstance(x,Constant)
        assert x.value==17

    def testQuoteList(self):
        scope=Scope(None)
        x=build(scope,[S('quote'),[11,13,17]],False)
        assert isinstance(x,Constant)
        assert x.value==[11,13,17]

    def testScope(self):
        scope=Scope(None)
        x=build(scope,[S('scope'),S('y'),S('z')],False)
        assert isinstance(x,Call)
        assert isinstance(x.f,VarRef)
        assert x.f.name==S('begin')
        assert len(x.posArgs)==2
        assert not x.kwArgs
        assert isinstance(x.posArgs[0],VarRef)
        assert x.posArgs[0].name==S('y')
        assert isinstance(x.posArgs[1],VarRef)
        assert x.posArgs[1].name==S('z')
        yScope=x.posArgs[0].scope
        zScope=x.posArgs[1].scope
        assert yScope is zScope
        assert yScope is not scope
        assert yScope.parent is scope

class ReduceTestCase(unittest.TestCase):
    def setUp(self):
        gensym.nextId=1
        self.stmts=[]

    def tearDown(self):
        self.stmts=None

    def r(self,gomer,isStmt):
        res=reduce(gomer,isStmt,self.stmts.append)
        gensym.nextId=1
        return res

    def testIntExpr(self):
        assert self.r(7,False)==7
        assert not self.stmts

    def testIntStmt(self):
        assert self.r(7,True) is None
        assert not self.stmts

    def testSymbolExpr(self):
        assert self.r(S('fred'),False)==S('fred')
        assert not self.stmts

    def testSymbolStmt(self):
        assert self.r(S('fred'),True) is None
        assert not self.stmts

    def testSimpleFuncExpr(self):
        scratch=gensym('scratch')
        gensym.nextId=1
        assert self.r([S('fred'),7,8],False)==scratch
        assert self.stmts==[[S(':='),scratch,[S('fred'),7,8]]]

    def testNestedFuncExpr(self):
        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        gensym.nextId=1
        assert self.r([S('fred'),7,[S('barney'),9,S('pebbles')]],
                      False)==scratch2
        assert self.stmts==[
            [S(':='),scratch1,[S('barney'),9,S('pebbles')]],
            [S(':='),scratch2,[S('fred'),7,scratch1]]
            ]

    def testSimpleFuncStmt(self):
        scratch=gensym('scratch')
        gensym.nextId=1
        assert self.r([S('fred'),7,8],True) is None
        assert self.stmts==[[S('fred'),7,8]]

    def testNestedFuncStmt(self):
        scratch1=gensym('scratch')
        gensym.nextId=1
        assert self.r([S('fred'),7,[S('barney'),9,S('pebbles')]],
                      True) is None
        assert self.stmts==[
            [S(':='),scratch1,[S('barney'),9,S('pebbles')]],
            [S('fred'),7,scratch1]
            ]

    def testNestedFuncStmt(self):
        scratch1=gensym('scratch')
        gensym.nextId=1
        assert self.r([S('fred'),7,[S('barney'),9,S('pebbles')]],
                      True) is None
        assert self.stmts==[
            [S(':='),scratch1,[S('barney'),9,S('pebbles')]],
            [S('fred'),7,scratch1]
            ]

    def testIfWithElseExpr(self):
        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        ifScratch=gensym('if')
        scratch4=gensym('scratch')
        gensym.nextId=1
        x=self.r([S('if'),
                       [S('<'),S('n'),10],
                       [S('barney'),9,S('bam-bam')],
                       [S('fred'),7,S('pebbles')],
                       ],
                      False)
        assert x==ifScratch
        assert self.stmts==[
            [S(':='),scratch1,[S('<'),S('n'),10]],
            [S('if'),
             scratch1,
             [S('begin'),
              [S(':='),scratch2,[S('barney'),9,S('bam-bam')]],
              [S(':='),ifScratch,scratch2]],
             [S('begin'),
              [S(':='),scratch4,[S('fred'),7,S('pebbles')]],
              [S(':='),ifScratch,scratch4]],
             ],
            ]

    def testIfWithElseStmt(self):
        ifScratch=gensym('scratch')
        gensym.nextId=1
        x=self.r([S('if'),
                  [S('<'),S('n'),10],
                  [S('barney'),9,S('bam-bam')],
                  [S('fred'),7,S('pebbles')],
                  ],
                 True)
        assert x is None
        assert self.stmts==[
            [S(':='),ifScratch,[S('<'),S('n'),10]],
            [S('if'),
             ifScratch,
             [S('barney'),9,S('bam-bam')],
             [S('fred'),7,S('pebbles')]
             ]
            ]

    def testWhileExpr(self):
        whileScratch=gensym('while')
        condScratch=gensym('scratch')
        gensym.nextId=1
        x=self.r([S('while'),
                       [S('<'),S('n'),10],
                       [S(':='),S('n'),[S('+'),S('n'),1]]
                  ],
                 False)
        assert x==whileScratch
        assert self.stmts==[
            [S(':='),whileScratch,None],
            [S(':='),condScratch,[S('<'),S('n'),10]],
            [S('while'),
             condScratch,
             [S('begin'),
              [S(':='),S('n'),[S('+'),S('n'),1]],
              [S(':='),whileScratch,S('n')],
              [S(':='),condScratch,[S('<'),S('n'),10]]
              ]
             ]
            ]

    def testWhileStmt(self):
        condScratch=gensym('scratch')
        gensym.nextId=1
        x=self.r([S('while'),
                  [S('<'),S('n'),10],
                  [S(':='),S('n'),[S('+'),S('n'),1]]
                  ],
                 True)
        assert x is None
        assert self.stmts==[
            [S(':='),condScratch,[S('<'),S('n'),10]],
            [S('while'),
             condScratch,
             [S('begin'),
              [S(':='),S('n'),[S('+'),S('n'),1]],
              [S(':='),condScratch,[S('<'),S('n'),10]]
              ]
             ]
            ]

    def testWhileStmtWithBreak(self):
        whileCondScratch=gensym('scratch')
        ifCondScratch=gensym('scratch')
        gensym.nextId=1
        src=[S('while'),
                  [S('<'),S('n'),10],
                  [S(':='),S('n'),[S('+'),S('n'),1]],
                  [S('if'),[S('=='),S('n'),7],
                   [S('break')]
                   ]
                  ]
        x=self.r(src,
                 True)
        assert x is None
        assert self.stmts==[
            [S(':='),whileCondScratch,[S('<'),S('n'),10]],
            [S('while'),
             whileCondScratch,
             [S('begin'),
              [S(':='),S('n'),[S('+'),S('n'),1]],
              [S(':='),ifCondScratch,[S('=='),S('n'),7]],
              [S('if'),
               ifCondScratch,
               [S('break')]
               ],
              [S(':='),whileCondScratch,[S('<'),S('n'),10]],
              ]
             ]
            ]

    def testWhileStmtWithContinue(self):
        whileCondScratch=gensym('scratch')
        ifCondScratch=gensym('scratch')
        gensym.nextId=1
        src=[S('while'),
                  [S('<'),S('n'),10],
                  [S(':='),S('n'),[S('+'),S('n'),1]],
                  [S('if'),[S('=='),S('n'),7],
                   [S('continue')]
                   ]
                  ]
        x=self.r(src,
                 True)
        assert x is None
        assert self.stmts==[
            [S(':='),whileCondScratch,[S('<'),S('n'),10]],
            [S('while'),
             whileCondScratch,
             [S('begin'),
              [S(':='),S('n'),[S('+'),S('n'),1]],
              [S(':='),ifCondScratch,[S('=='),S('n'),7]],
              [S('if'),
               ifCondScratch,
               [S('continue')]
               ],
              [S(':='),whileCondScratch,[S('<'),S('n'),10]],
              ]
             ]
            ]

    def testDefunStmt(self):
        x=self.r([S('defun'),S('fact'),[S('n')],
                  [S('if'),
                   [S('<'),S('n'),2],
                   1,
                   [S('*'),S('n'),[S('fact'),[S('-'),S('n'),1]]]
                   ]
                  ],
                 True)
        assert x is None

        gensym.nextId=1
        condScratch=gensym('scratch')
        ifScratch=gensym('if')
        scratch2=gensym('scratch')
        scratch3=gensym('scratch')
        scratch4=gensym('scratch')
        scratch5=gensym('scratch')

        expected=[
            [S('def'),S('fact'),[S('n')],
             [S('begin'),
              [S(':='),condScratch,[S('<'),S('n'),2]],
              [S('if'),
               condScratch,
               [S(':='),ifScratch,1],
               [S('begin'),
                [S(':='),scratch2,[S('-'),S('n'),1]],
                [S(':='),scratch3,[S('fact'),scratch2]],
                [S(':='),scratch4,[S('*'),S('n'),scratch3]],
                [S(':='),ifScratch,scratch4]
                ]
               ],
              [S('return'),ifScratch],
              ]
             ]
            ]
        assert self.stmts==expected

    def testDefunExpr(self):
        x=self.r([S('defun'),S('fact'),[S('n')],
                  [S('if'),
                   [S('<'),S('n'),2],
                   1,
                   [S('*'),S('n'),[S('fact'),[S('-'),S('n'),1]]]
                   ]
                  ],
                 False)
        assert x==S('fact')

        gensym.nextId=1
        condScratch=gensym('scratch')
        ifScratch=gensym('if')
        scratch2=gensym('scratch')
        scratch3=gensym('scratch')
        scratch4=gensym('scratch')
        scratch5=gensym('scratch')

        expected=[
            [S('def'),S('fact'),[S('n')],
             [S('begin'),
              [S(':='),condScratch,[S('<'),S('n'),2]],
              [S('if'),
               condScratch,
               [S(':='),ifScratch,1],
               [S('begin'),
                [S(':='),scratch2,[S('-'),S('n'),1]],
                [S(':='),scratch3,[S('fact'),scratch2]],
                [S(':='),scratch4,[S('*'),S('n'),scratch3]],
                [S(':='),ifScratch,scratch4]
                ]
               ],
              [S('return'),ifScratch],
              ]
             ]
            ]
        assert self.stmts==expected

    def testLambdaExpr(self):
        x=self.r([S('lambda'),[S('n')],
                  [S('if'),
                   [S('<'),S('n'),2],
                   1,
                   [S('*'),S('n'),[S('fact'),[S('-'),S('n'),1]]]
                   ]
                  ],
                 False)

        gensym.nextId=1
        lambdaScratch=gensym('lambda')
        condScratch=gensym('scratch')
        ifScratch=gensym('if')
        scratch2=gensym('scratch')
        scratch3=gensym('scratch')
        scratch4=gensym('scratch')
        scratch5=gensym('scratch')

        assert x==lambdaScratch

        expected=[
            [S('def'),lambdaScratch,[S('n')],
             [S('begin'),
              [S(':='),condScratch,[S('<'),S('n'),2]],
              [S('if'),
               condScratch,
               [S(':='),ifScratch,1],
               [S('begin'),
                [S(':='),scratch2,[S('-'),S('n'),1]],
                [S(':='),scratch3,[S('fact'),scratch2]],
                [S(':='),scratch4,[S('*'),S('n'),scratch3]],
                [S(':='),ifScratch,scratch4]
                ]
               ],
              [S('return'),ifScratch],
              ]
             ]
            ]
        assert self.stmts==expected

    def testLambdaStmt(self):
        x=self.r([S('lambda'),[S('n')],
                  [S('if'),
                   [S('<'),S('n'),2],
                   1,
                   [S('*'),S('n'),[S('fact'),[S('-'),S('n'),1]]]
                   ]
                  ],
                 True)

        assert x is None
        assert not self.stmts

    def testBeginStmt(self):
        x=self.r([S('begin'),
                  [S(':='),S('x'),9],
                  [S(':='),S('y'),7],
                  [S(':='),S('z'),[S('*'),S('x'),S('y')]],
                  ],
                 True)

        assert x is None

        assert self.stmts==[
             [S(':='),S('x'),9],
             [S(':='),S('y'),7],
             [S(':='),S('z'),[S('*'),S('x'),S('y')]],
            ]

    def testBeginExpr(self):
        x=self.r([S('begin'),
                  [S(':='),S('x'),9],
                  [S(':='),S('y'),7],
                  [S(':='),S('z'),[S('*'),S('x'),S('y')]],
                  ],
                 False)

        assert x==S('z')

        assert self.stmts==[
             [S(':='),S('x'),9],
             [S(':='),S('y'),7],
             [S(':='),S('z'),[S('*'),S('x'),S('y')]],
            ]

    def testAssignStmt(self):
        x=self.r([S(':='),S('z'),[S('*'),9,7]],
                 True)

        assert x is None

        assert self.stmts==[
             [S(':='),S('z'),[S('*'),9,7]],
            ]

    def testAssignExpr(self):
        x=self.r([S(':='),S('z'),[S('*'),9,7]],
                 False)

        assert x==S('z')

        assert self.stmts==[
             [S(':='),S('z'),[S('*'),9,7]],
            ]

    def testImportStmt(self):
        x=self.r([S('import'),S('re'),S('adder.runtime')],
                 True)

        assert x is None

        assert self.stmts==[
            [S('import'),S('re')],
            [S('import'),S('adder.runtime')],
            ]

    def testImportExpr(self):
        x=self.r([S('import'),S('re'),S('adder.runtime')],
                 False)

        assert x==S('adder.runtime')

        assert self.stmts==[
            [S('import'),S('re')],
            [S('import'),S('adder.runtime')],
            ]

    def testQuoteIntExpr(self):
        x=self.r([S('quote'),9],
                 False)

        assert x==9
        assert not self.stmts

    def testQuoteNoneExpr(self):
        x=self.r([S('quote'),None],
                 False)

        assert x is None
        assert not self.stmts

    def testQuoteListExpr(self):
        x=self.r([S('quote'),[1,2,3]],
                 False)

        scratch=gensym('scratch')

        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('quote'),[1,2,3]]]
            ]

    def testQuoteIntStmt(self):
        x=self.r([S('quote'),9],
                 True)

        assert x is None
        assert not self.stmts

    def testQuoteNoneStmt(self):
        x=self.r([S('quote'),None],
                 True)

        assert x is None
        assert not self.stmts

    def testQuoteListStmt(self):
        x=self.r([S('quote'),[1,2,3]],
                 True)

        assert x is None
        assert not self.stmts

    def testReturnStmt(self):
        x=self.r([S('return'),[S('*'),9,7]],
                 True)

        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('*'),9,7]],
            [S('return'),scratch],
            ]

    def testReturnExpr(self):
        x=self.r([S('return'),[S('*'),9,7]],
                 False)

        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('*'),9,7]],
            [S('return'),scratch],
            ]

    def testYieldStmt(self):
        x=self.r([S('yield'),[S('*'),9,7]],
                 True)

        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('*'),9,7]],
            [S('yield'),scratch],
            ]

    def testYieldExpr(self):
        x=self.r([S('yield'),[S('*'),9,7]],
                 False)

        scratch=gensym('scratch')

        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('*'),9,7]],
            [S('yield'),scratch],
            ]

    def testAnd0Expr(self):
        x=self.r([S('and')],
                 False)

        assert x is True
        assert not self.stmts

    def testAnd1Expr(self):
        x=self.r([S('and'),S('x')],
                 False)

        assert x==S('x')
        assert not self.stmts

    def testAnd2Expr(self):
        x=self.r([S('and'),S('x'),S('y')],
                 False)

        ifScratch=gensym('if')
        assert x==ifScratch
        assert self.stmts==[
            [S('if'),S('x'),
             [S(':='),ifScratch,S('y')],
             [S(':='),ifScratch,S('x')],
             ]
            ]

    def testAnd2Stmt(self):
        x=self.r([S('and'),[S('f'),1],[S('f'),2]],
                 True)

        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('f'),1]],
            [S('if'),scratch,
             [S('f'),2],
             [S('begin')],
             ]
            ]

    def testAnd3Expr(self):
        x=self.r([S('and'),S('x'),S('y'),S('z')],
                 False)

        ifScratch1=gensym('if')
        ifScratch2=gensym('if')
        expected=[
            [S('if'),S('x'),
             [S('begin'),
              [S('if'),S('y'),
               [S(':='),ifScratch1,S('z')],
               [S(':='),ifScratch1,S('y')]
               ],
              [S(':='),ifScratch2,ifScratch1]
              ],
             [S(':='),ifScratch2,S('x')]
             ]
            ]
        assert x==ifScratch2
        assert self.stmts==expected

    def testOr0Expr(self):
        x=self.r([S('or')],
                 False)

        assert x is False
        assert not self.stmts

    def testOr1Expr(self):
        x=self.r([S('or'),S('x')],
                 False)

        assert x==S('x')
        assert not self.stmts

    def testOr2Expr(self):
        x=self.r([S('or'),S('x'),S('y')],
                 False)

        ifScratch=gensym('if')
        assert x==ifScratch
        assert self.stmts==[
            [S('if'),S('x'),
             [S(':='),ifScratch,S('x')],
             [S(':='),ifScratch,S('y')],
             ]
            ]

    def testOr2Stmt(self):
        x=self.r([S('or'),[S('f'),1],[S('f'),2]],
                 True)

        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('f'),1]],
            [S('if'),scratch,
             [S('begin')],
             [S('f'),2],
             ]
            ]

    def testOr3Expr(self):
        x=self.r([S('or'),S('x'),S('y'),S('z')],
                 False)

        ifScratch1=gensym('if')
        ifScratch2=gensym('if')
        expected=[
            [S('if'),S('x'),
             [S(':='),ifScratch1,S('x')],
             [S('begin'),
              [S('if'),S('y'),
               [S(':='),ifScratch2,S('y')],
               [S(':='),ifScratch2,S('z')]
               ],
              [S(':='),ifScratch1,ifScratch2]
              ]
             ]
            ]
        assert x==ifScratch1
        assert self.stmts==expected

    def testVarDot0Expr(self):
        x=self.r([S('.'),S('x')],
                 False)

        assert x==S('x')
        assert not self.stmts

    def testVarDot1Expr(self):
        x=self.r([S('.'),S('x'),S('y')],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('.'),S('x'),S('y')]]
            ]

    def testVarDot2Expr(self):
        x=self.r([S('.'),S('x'),S('y'),S('z')],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('.'),S('x'),S('y'),S('z')]]
            ]

    # F. Dot Fitzgerald
    def testFDot0Expr(self):
        x=self.r([S('.'),[S('f'),7]],
                 False)
        scratch=gensym('scratch')

        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,
             [S('f'),7]],
            ]

    def testFDot1Expr(self):
        x=self.r([S('.'),[S('f'),7],S('y')],
                 False)
        scratch1=gensym('scratch')
        scratch2=gensym('scratch')

        assert x==scratch2
        assert self.stmts==[
            [S(':='),scratch1,
             [S('f'),7]],
            [S(':='),scratch2,
             [S('.'),scratch1,S('y')]]
            ]

    def testFDot2Expr(self):
        x=self.r([S('.'),[S('f'),7],S('y'),S('z')],
                 False)
        scratch1=gensym('scratch')
        scratch2=gensym('scratch')

        assert x==scratch2
        assert self.stmts==[
            [S(':='),scratch1,
             [S('f'),7]],
            [S(':='),scratch2,
             [S('.'),scratch1,S('y'),S('z')]]
            ]

    def testVarDot0Stmt(self):
        x=self.r([S('.'),S('x')],
                 True)

        assert x is None
        assert not self.stmts

    def testVarDot1Stmt(self):
        x=self.r([S('.'),S('x'),S('y')],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert not self.stmts

    def testVarDot2Stmt(self):
        x=self.r([S('.'),S('x'),S('y'),S('z')],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert not self.stmts

    # F. Dot Fitzgerald
    def testFDot0Stmt(self):
        x=self.r([S('.'),[S('f'),7]],
                 True)
        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S('f'),7]
            ]

    def testFDot1Stmt(self):
        x=self.r([S('.'),[S('f'),7],S('y')],
                 True)
        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('f'),7]]
            ]

    def testFDot2Stmt(self):
        x=self.r([S('.'),[S('f'),7],S('y'),S('z')],
                 True)
        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('f'),7]]
            ]

    def testRaise(self):
        x=self.r([S('raise'),[S('f'),7]],
                 True)
        scratch=gensym('scratch')

        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('f'),7]],
            [S('raise'),scratch]
            ]

    def testReraise(self):
        x=self.r([S('raise')],
                 True)

        assert x is None
        assert self.stmts==[
            [S('reraise')]
            ]

    def testPrint0Stmt(self):
        x=self.r([S('print')],
                 True)

        assert x is None
        assert self.stmts==[
            [S('print')]
            ]

    def testPrint1Stmt(self):
        x=self.r([S('print'),5],
                 True)

        assert x is None
        assert self.stmts==[
            [S('print'),5]
            ]

    def testPrint2Stmt(self):
        x=self.r([S('print'),5,[S('x'),12]],
                 True)

        scratch=gensym('scratch')
        assert x is None
        assert self.stmts==[
            [S(':='),scratch,[S('x'),12]],
            [S('print'),5,scratch]
            ]

    def testPrint0Expr(self):
        x=self.r([S('print')],
                 False)

        assert x is None
        assert self.stmts==[
            [S('print')]
            ]

    def testPrint1Expr(self):
        x=self.r([S('print'),5],
                 False)

        assert x==5
        assert self.stmts==[
            [S('print'),5]
            ]

    def testPrint2Expr(self):
        x=self.r([S('print'),5,[S('x'),12]],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('x'),12]],
            [S('print'),5,scratch]
            ]

    def testPlus0Expr(self):
        x=self.r([S('+')],
                 False)

        assert x==0
        assert not self.stmts

    def testPlus1VarExpr(self):
        x=self.r([S('+'),5],
                 False)

        assert x==5
        assert not self.stmts

    def testPlus1FExpr(self):
        x=self.r([S('+'),[S('f'),7]],
                 False)

        scratch=gensym('scratch')
        assert x==scratch
        assert self.stmts==[
            [S(':='),scratch,[S('f'),7]],
            ]

    def testPlus2Expr(self):
        x=self.r([S('+'),5,[S('f'),7]],
                 False)

        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        assert x==scratch2
        assert self.stmts==[
            [S(':='),scratch1,[S('f'),7]],
            [S(':='),scratch2,[S('binop'),S('+'),5,scratch1]],
            ]

    def testPlus3Expr(self):
        x=self.r([S('+'),5,[S('f'),7],9],
                 False)

        scratch1=gensym('scratch')
        scratch2=gensym('scratch')
        scratch3=gensym('scratch')
        assert x==scratch3
        assert self.stmts==[
            [S(':='),scratch1,[S('f'),7]],
            [S(':='),scratch2,[S('binop'),S('+'),scratch1,9]],
            [S(':='),scratch3,[S('binop'),S('+'),5,scratch2]],
            ]

class CompyleTestCase(unittest.TestCase):
    def setUp(self):
        self.stmts=[]
        adder.common.gensym.nextId=1
        adder.gomer.Scope.nextId=1

    def tearDown(self):
        self.stmts=None

    def stmtCollector(self,stmt):
        self.stmts.append(stmt)

    def testConstantInt(self):
        scope=Scope(None)
        x=Constant(scope,5)
        assert x.compyle(self.stmtCollector)==5
        assert self.stmts==[]

    def testConstantStr(self):
        scope=Scope(None)
        x=Constant(scope,'fred')
        assert x.compyle(self.stmtCollector)=='fred'
        assert self.stmts==[]

    def testConstantBool(self):
        scope=Scope(None)
        x=Constant(scope,False)
        assert x.compyle(self.stmtCollector)==False
        assert self.stmts==[]

    def testConstantNone(self):
        scope=Scope(None)
        x=Constant(scope,None)
        assert x.compyle(self.stmtCollector)==None
        assert self.stmts==[]

    def testConstantFloat(self):
        scope=Scope(None)
        x=Constant(scope,3.7)
        assert x.compyle(self.stmtCollector)==3.7
        assert self.stmts==[]

    def testConstantTuple(self):
        scope=Scope(None)
        x=Constant(scope,(1,2,3))
        assert x.compyle(self.stmtCollector)==(1,2,3)
        assert self.stmts==[]

    def testConstantSymbol(self):
        scope=Scope(None)
        x=Constant(scope,S('fred'))
        assert x.compyle(self.stmtCollector)==[S('adder.common.Symbol'),
                                               ['fred']]
        assert self.stmts==[]

    def testConstantList(self):
        scope=Scope(None)
        x=Constant(scope,[1,2,3])
        assert x.compyle(self.stmtCollector)==[S('mk-list'),[1,2,3]]
        assert self.stmts==[]

    def testPredefinedTrue(self):
        scope=Scope(None)
        x=build(scope,S('true'),False)
        assert x.compyle(self.stmtCollector)==True
        assert self.stmts==[]

    def testPredefinedFalse(self):
        scope=Scope(None)
        x=build(scope,S('false'),False)
        assert x.compyle(self.stmtCollector)==False
        assert self.stmts==[]

    def testVarAtRoot(self):
        scope=Scope(None)
        scope.addDef(S('fred'),None)
        x=VarRef(scope,S('fred'))
        assert x.compyle(self.stmtCollector)==S('fred')
        assert self.stmts==[]

    def testVar(self):
        scope=Scope(Scope(None))
        scope.addDef(S('fred'),None)
        x=VarRef(scope,S('fred'))
        p=x.compyle(self.stmtCollector)
        assert p==S('fred_2')
        assert self.stmts==[]

    def testQuoteInt(self):
        scope=Scope(None)
        x=build(scope,[S('quote'),17],False)
        assert x.compyle(self.stmtCollector)==17
        assert self.stmts==[]

    def testQuoteSym(self):
        scope=Scope(None)
        x=build(scope,[S('quote'),S('x')],False)
        assert x.compyle(self.stmtCollector)==[S('adder.common.Symbol'),['x']]
        assert self.stmts==[]

    def testQuoteList(self):
        scope=Scope(None)
        x=build(scope,[S('quote'),[11,13,17]],False)
        assert x.compyle(self.stmtCollector)==[S('mk-list'),[11,13,17]]
        assert self.stmts==[]

    def testCallOnlyPos(self):
        scope=Scope(None)
        scope.addDef(S('f'),None)
        x=build(scope,[S('f'),11,13,17],False)
        assert x.compyle(self.stmtCollector)==[S('f'),[11,13,17]]
        assert self.stmts==[]

    def testCallBoth(self):
        scope=Scope(None)
        scope.addDef(S('f'),None)
        x=build(scope,[S('f'),11,13,17,S(':alpha'),23],False)
        assert x.compyle(self.stmtCollector)==[S('f'),
                                               [11,13,17],
                                               [['alpha',23]]
                                               ]
        assert self.stmts==[]

    def testCallImport(self):
        scope=Scope(None)
        x=build(scope,[S('import'),S('os')],True)
        x.compyle(self.stmtCollector)
        assert self.stmts==[[S('import'),[S('os')]]]

    def testIfExpr(self):
        scope=Scope(None)
        scope.addDef('n',None)
        x=build(scope,
                [S('if'),[S('<'),S('n'),2],
                  1,
                  7],False)
        p=x.compyle(self.stmtCollector)
        assert p==[S('if-expr'),
                   [[S('<'),[S('n'),2]],1,7]]

    def testIfStmt(self):
        scope=Scope(None)
        scope.addDef('n',None)
        x=build(scope,
                [S('if'),[S('<'),S('n'),2],
                  [S('print'),1],
                  [S('print'),7]],True)
        p=x.compyle(self.stmtCollector)
        assert not p
        assert self.stmts==[[S('if-stmt'),
                             [[S('<'),[S('n'),2]],
                              [S('print'),[1]],
                              [S('print'),[7]]]]]

    def testWhile(self):
        scope=Scope(None)
        scope.addDef('n',None)
        x=build(scope,
                [S('while'),[S('<'),S('n'),2],
                  1,
                  7],
                True)
        p=x.compyle(self.stmtCollector)
        assert not p
        scratch=S('#<gensym-scratch #1>')
        assert self.stmts==[[S('while'),
                             [[S('<'),[S('n'),2]],
                              1,
                              7]]]

    def testReturn(self):
        scope=Scope(None)
        x=build(scope,[S('return'),17],True)
        p=x.compyle(self.stmtCollector)
        assert not p
        assert self.stmts==[[S('return'),[17]]]

    def testYield(self):
        scope=Scope(None,isFunc=True)
        x=build(scope,[S('yield'),17],True)
        p=x.compyle(self.stmtCollector)
        assert not p
        assert self.stmts==[[S('yield'),[17]]]
        assert scope.funcYields

    def testReturnFrom(self):
        scope=Scope(None)
        x=build(scope,[S('return-from'),
                       S('fred'),
                       17],True)
        p=x.compyle(self.stmtCollector)
        assert not p
        assert self.stmts==[[S('raise'),
                             [[S('adder.runtime.ReturnValue'),
                               [[S('quote'),[S('fred')]],17]]]]]

    def testBlock(self):
        scope=Scope(None)
        x=build(scope,[S('block'),
                       S(':fred'),
                       [S('*'),9,7]],False)
        p=x.compyle(self.stmtCollector)
        adder.common.gensym.nextId=1
        scratch1=gensym('fred')
        rv=gensym('rv')
        scratch3=gensym('scratch')
        assert p==scratch3
        expected=[[S('begin'),
                   [[S(':='),[scratch1,None]],
                    [S('try'),
                     [[S('begin'),
                       [[S(':='),[scratch1,[S('*'),[9,7]]]]]
                       ]],
                     [['adder.runtime.ReturnValue',rv,
                       [S('begin'),
                       [[S('if-stmt'),
                         [[S('=='),
                           [[S('.'),[rv,S('block')]],
                            [S('adder.common.Symbol'),['fred']]]],
                          [S(':='),[scratch1,
                                    [S('.'),
                                     [S('#<gensym-rv #2>'),
                                      S('value')]]]],
                          [S('raise'),[]]]]]]
                        ]]],
                    [S(':='),
                     [S('#<gensym-scratch #3>'),
                      S('#<gensym-fred #1>')]]
                   ]]]
        assert self.stmts==expected

    def testDot0(self):
        scope=Scope(None)
        scope.addDef('o',None)
        x=build(scope,[S('.'),S('o')],False)
        p=x.compyle(self.stmtCollector)
        assert p==[S('.'),[S('o')]]
        assert not self.stmts

    def testDot1(self):
        scope=Scope(None)
        scope.addDef('o',None)
        x=build(scope,[S('.'),S('o'),S('x')],False)
        p=x.compyle(self.stmtCollector)
        assert p==[S('.'),[S('o'),S('x')]]
        assert not self.stmts

    def testDot3(self):
        scope=Scope(None)
        scope.addDef('o',None)
        x=build(scope,[S('.'),S('o'),S('x'),S('y'),S('z')],False)
        p=x.compyle(self.stmtCollector)
        assert p==[S('.'),[S('o'),S('x'),S('y'),S('z')]]
        assert not self.stmts

    def testDefun(self):
        scope=Scope(None)
        x=build(scope,
                [S('defun'),S('fact'),[S('n')],
                 [S('if'),[S('<'),S('n'),2],
                  1,
                  [S('*'),S('n'),[S('-'),S('n'),1]]]],
                False)
        p=x.compyle(self.stmtCollector)
        assert p==S('fact')
        expected=[
            [S('def'),[
                    S('fact'),
                    [S('n')],
                    [S('return'),[
                            [S('if-expr'),[
                                    [S('<'),[S('n'),2]],
                                    1,
                                    [S('*'), [
                                            S('n'),
                                            [S('-'),[S('n'),1]]
                                            ]]
                                    ]
                             ]
                            ]
                     ]
                    ]
             ]
            ]
        assert self.stmts==expected

    def testLambda(self):
        scope=Scope(None)
        x=build(scope,
                [S('lambda'),[S('n')],
                 [S('if'),[S('<'),S('n'),30],
                  10,
                  5]],False)
        p=x.compyle(self.stmtCollector)
        scratch=S('#<gensym-lambda #1>')
        scratchPy=scratch.toPython()
        assert p==scratch
        expected=[
            [S('def'),[
                    scratch,
                    [S('n')],
                    [S('return'),[
                            [S('if-expr'),[
                                    [S('<'),[S('n'),30]],
                                    10,5
                                    ]
                             ]
                            ]
                     ]
                    ]
             ]
            ]
        assert self.stmts==expected

suite=unittest.TestSuite(
    ( 
      unittest.makeSuite(VarEntryTestCase,'test'),
      unittest.makeSuite(ScopeTestCase,'test'),
      unittest.makeSuite(ExprTestCase,'test'),
      unittest.makeSuite(BuildTestCase,'test'),
      unittest.makeSuite(ReduceTestCase,'testPlus'),
      unittest.makeSuite(CompyleTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

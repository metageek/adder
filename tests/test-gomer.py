#!/usr/bin/env python3

import unittest,pdb,sys,os
from adder.gomer import *
from adder.common import Symbol as S
import adder.stdenv,adder.common

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

        call=Call(scope3,
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

        fExpr=Call(scope2,
                   VarRef(scope2,S('lambda')),
                   [[VarRef(scope4,S('a')),
                     VarRef(scope4,S('b')),
                     VarRef(scope4,S('c'))],
                    Call(scope4,
                         VarRef(scope4,S('l')),
                         [VarRef(scope4,S('c')),
                          VarRef(scope4,S('b')),
                          VarRef(scope4,S('a'))])])

        scope2.addDef(S('l'),Constant(scope2,
                                      NativeFunction((lambda a,b,c:
                                                          [a,b,c]),
                                                     True)))

        scope2.addDef(S('f'),Constant(scope2,UserFunction(fExpr,env3)))

        call=Call(scope3,
                  VarRef(scope3,S('f')),
                  [VarRef(scope3,S('james1')),
                   VarRef(scope3,S('charles1')),
                   VarRef(scope3,S('charles2'))])

        assert call.scopeRequired() is scope1
        assert call.isPureIn(scope3)
        assert call.evaluate(env3)==[1649,1625,1603]
        assert call.constValue()==[1649,1625,1603]

class StdEnvTestCase(unittest.TestCase):
    def setUp(self):
        (self.scope,self.env)=adder.stdenv.mkStdEnv()
        adder.common.gensym.nextId=1

    def tearDown(self):
        self.scope=self.env=None

    def call(self,fname,*argConsts):
        expr=Call(self.scope,
                  VarRef(self.scope,S(fname)),
                  list(map(lambda c: Constant(self.scope,c),argConsts)))
        return expr.evaluate(self.env)

    def testPlus(self):
        assert self.call('+',1,2,3,4)==10
        
    def testMinus(self):
        assert self.call('-',1,2,3)==-4
        assert self.call('-',1)==-1

    def testTimes(self):
        assert self.call('*',1,2,3,4)==24
        assert self.call('*')==1

    def testFDiv(self):
        assert self.call('/',25,3,4)==25/3/4
        assert self.call('/',8)==1/8

    def testIDiv(self):
        assert self.call('//',25,3,4)==2
        assert self.call('//',8)==0
        assert self.call('//',1)==1
        assert self.call('//',-1)==-1

    def testMod(self):
        assert self.call('%',25,3)==1
        assert self.call('%',25,7)==4
        assert self.call('%',-25,7)==3

    def testEq(self):
        assert self.call('==',25,3,4)==False
        assert self.call('==',24,24,7)==False
        assert self.call('==',24,24,24)==True
        assert self.call('==',24,24)==True
        assert self.call('==',24)==True
        assert self.call('==')==True

    def testNe(self):
        assert self.call('!=',25,3,4)==True
        assert self.call('!=',24,24,7)==True
        assert self.call('!=',24,24,24)==False
        assert self.call('!=',24,24)==False
        assert self.call('!=',24)==False
        assert self.call('!=')==False

    def testLt(self):
        assert self.call('<')==True
        assert self.call('<',3)==True
        assert self.call('<',3,4)==True
        assert self.call('<',4,3)==False
        assert self.call('<',4,4)==False
        assert self.call('<',3,4,5)==True
        assert self.call('<',5,4,3)==False
        assert self.call('<',3,5,4)==False
        assert self.call('<',4,3,5)==False

    def testGt(self):
        assert self.call('>')==True
        assert self.call('>',3)==True
        assert self.call('>',3,4)==False
        assert self.call('>',4,3)==True
        assert self.call('>',4,4)==False
        assert self.call('>',3,4,5)==False
        assert self.call('>',5,4,3)==True
        assert self.call('>',3,5,4)==False
        assert self.call('>',4,3,5)==False

    def testLe(self):
        assert self.call('<=')==True
        assert self.call('<=',3)==True
        assert self.call('<=',3,4)==True
        assert self.call('<=',4,3)==False
        assert self.call('<=',4,4)==True
        assert self.call('<=',3,4,5)==True
        assert self.call('<=',5,4,3)==False
        assert self.call('<=',3,5,4)==False
        assert self.call('<=',4,3,5)==False

    def testGe(self):
        assert self.call('>=')==True
        assert self.call('>=',3)==True
        assert self.call('>=',3,4)==False
        assert self.call('>=',4,3)==True
        assert self.call('>=',4,4)==True
        assert self.call('>=',3,4,5)==False
        assert self.call('>=',5,4,3)==True
        assert self.call('>=',3,5,4)==False
        assert self.call('>=',4,3,5)==False

    def testIn(self):
        assert self.call('in','x','fox')==True
        assert self.call('in','x','fob')==False

    def testRaise(self):
        try:
            self.call('raise',Exception('foo'))
        except Exception as e:
            assert type(e)==Exception
            assert e.args==('foo',)

    def testGensym(self):
        x=self.call('gensym','x')
        assert isinstance(x,S)
        assert x==S('#<gensym-x #1>')

        y=self.call('gensym','y')
        assert isinstance(y,S)
        assert y==S('#<gensym-y #2>')

    def testGetitem(self):
        assert self.call('[]',[2,3,5,7],2)==5

    def testSlice(self):
        assert self.call('slice',[2,3,5,7],2)==[5,7]
        assert self.call('slice',[2,3,5,7],1,3)==[3,5]

    def testList(self):
        assert self.call('list',(2,3,5,7))==[2,3,5,7]

    def testTuple(self):
        assert self.call('tuple',[2,3,5,7])==(2,3,5,7)

    def testSet(self):
        assert self.call('set',(2,3,5,7))==set([2,3,5,7])

    def testMkList(self):
        assert self.call('mk-list',2,3,5,7)==[2,3,5,7]

    def testMkTuple(self):
        assert self.call('mk-tuple',2,3,5,7)==(2,3,5,7)

    def testMkSet(self):
        assert self.call('mk-set',2,3,5,7)==set([2,3,5,7])

suite=unittest.TestSuite(
    ( unittest.makeSuite(VarEntryTestCase,'test'),
      unittest.makeSuite(ScopeTestCase,'test'),
      unittest.makeSuite(ExprTestCase,'test'),
      unittest.makeSuite(StdEnvTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

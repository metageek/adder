#!/usr/bin/env python3

import unittest,pdb,sys,os
from adder.gomer import *
from adder.common import Symbol as S

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

    def testCallNative(self):
        scope1=Scope(None)
        scope2=Scope(scope1)
        scope3=Scope(scope2)
        scope4=Scope(scope2)

        scope1.addDef(S('james1'),Constant(scope1,1603))
        scope2.addDef(S('charles1'),Constant(scope2,1625))
        scope3.addDef(S('charles2'),Constant(scope3,1649))
        scope4.addFuncArg(S('a'))
        scope4.addFuncArg(S('b'))
        scope4.addFuncArg(S('c'))

        fExpr=Call(scope2,
                   VarRef(scope2,S('lambda')),
                   [VarRef(scope4,S('a')),
                    VarRef(scope4,S('b')),
                    VarRef(scope4,S('c'))],
                   Call(scope4,
                        VarRef(scope4,S('l')),
                        [VarRef(scope4,S('c')),
                         VarRef(scope4,S('b')),
                         VarRef(scope4,S('a'))]))

        scope2.addDef(S('l'),Constant(scope2,fExpr))

        call=Call(scope3,
                  VarRef(scope3,S('l')),
                  [VarRef(scope3,S('james1')),
                   VarRef(scope3,S('charles1')),
                   VarRef(scope3,S('charles2'))])

        assert call.scopeRequired() is scope1
        assert call.isPureIn(scope3)
        assert call.constValue()==[1649,1625,1603]

suite=unittest.TestSuite(
    ( unittest.makeSuite(VarEntryTestCase,'test'),
      unittest.makeSuite(ScopeTestCase,'test'),
      unittest.makeSuite(ExprTestCase,'test'),
     )
    )

unittest.TextTestRunner().run(suite)

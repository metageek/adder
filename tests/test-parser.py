#!/usr/bin/env python3

import unittest,pdb,sys,os

from adder.parser import lex,parse,parseFile,stripLines,ATOM,OPEN,CLOSE,QUOTE,BACKQUOTE,COMMA,STRING

from adder.common import q,Symbol

S=Symbol

class LexerTestCase(unittest.TestCase):
    def test1(self):
        assert list(lex("1 2 b + ( \n17 'foo"))==[(ATOM,"1",1),
                                                  (ATOM,"2",1),
                                                  (ATOM,"b",1),
                                                  (ATOM,"+",1),
                                                  (OPEN,None,1),
                                                  (ATOM,"17",2),
                                                  (QUOTE,None,2),
                                                  (ATOM,"foo",2)]

    def test2(self):
        assert list(lex('(foo "bar\\nquux" \'baz)'))==[(OPEN,None,1),
                                                       (ATOM,"foo",1),
                                                       (STRING,"bar\nquux",1),
                                                       (QUOTE,None,1),
                                                       (ATOM,"baz",1),
                                                       (CLOSE,None,1)]
    def test3(self):
        assert list(lex('(foo ,"bar\\nquux" `baz)'))==[
            (OPEN,None,1),
            (ATOM,"foo",1),
            (COMMA,None,1),
            (STRING,"bar\nquux",1),
            (BACKQUOTE,None,1),
            (ATOM,"baz",1),
            (CLOSE,None,1)]

class ParserTestCase(unittest.TestCase):
    def testSymbol(self):
        l=list(parse('foo'))
        assert l==[(S('foo'),1)]
        assert isinstance(l[0][0],S)

    def testQuotedSymbol(self):
        l=list(parse("'foo"))
        l2=[([(S('quote'),1),(S('foo'),1)],1)]
        assert l==l2
        assert isinstance(l[0][0][0][0],S)

    def testQuotedList(self):
        l=list(parse("'(1 2)"))
        l2=[([(S('quote'),1),([(1,1),(2,1)],1)],1)]
        assert l==l2
        assert isinstance(l[0][0][0][0],S)

    def testQuotedListLineBreak(self):
        l=list(parse("'(1\n2)"))
        l2=[([(S('quote'),1),([(1,1),(2,2)],1)],1)]
        assert l==l2
        assert isinstance(l[0][0][0][0],S)

    def testBackQuotedSymbol(self):
        l=list(parse("`foo"))
        l2=[([(S('backquote'),1),(S('foo'),1)],1)]
        assert l==l2
        assert isinstance(l[0][0][0][0],S)

    def testBackQuotedList(self):
        l=list(parse("`(1 2)"))
        l2=[([(S('backquote'),1),([(1,1),(2,1)],1)],1)]
        assert l==l2
        assert isinstance(l[0][0][0][0],S)

    def testBackQuotedListWithComma(self):
        l=list(parse("`(1 2 ,foo)"))
        l2=[([(S('backquote'),1),([(1,1),(2,1),
                                   ([(S(','),1),(S('foo'),1)],1)
                                   ],1)],1)]
        assert l==l2
        assert isinstance(l[0][0][0][0],S)

    def testBackQuotedListWithCommaAt(self):
        l=list(parse("`(1 2 ,@foo)"))
        l2=[([(S('backquote'),1),([(1,1),(2,1),
                                   ([(S(',@'),1),(S('foo'),1)],1)
                                   ],1)],1)]
        assert l==l2
        assert isinstance(l[0][0][0][0],S)

    def testString(self):
        l=list(parse('"foo"'))
        assert l==[("foo",1)]
        assert not isinstance(l[0][0],S)

    def testInteger(self):
        l=list(parse('17'))
        assert l==[(17,1)]

    def testFloat(self):
        l=list(parse('17.3'))
        assert l==[(17.3,1)]

    def testSimpleList(self):
        l=list(parse('(17.3 12 foo "bar" quux)'))
        assert l==[([(17.3,1),(12,1),(S("foo"),1),("bar",1),(S("quux"),1)],1)]

    def testSimpleListLineBreaks(self):
        l=list(parse('(17.3 12\nfoo "bar"\nquux)'))
        assert l==[([(17.3,1),(12,1),(S("foo"),2),("bar",2),(S("quux"),3)],1)]

    def testSimpleListQuotes(self):
        l=list(parse('(17.3 12 \'foo "bar" quux)'))
        l2=[([(17.3,1),(12,1),
              ([(S("quote"),1),(S("foo"),1)],1),
              ("bar",1),(S("quux"),1)],1)]
        assert l==l2

    def testNestedListQuotes(self):
        l=list(parse('(17.3 12 (+ x y 17) \'foo "bar" quux)'))
        l2=[([(17.3,1),(12,1),
              ([(S('+'),1),(S('x'),1),(S('y'),1),(17,1)],1),
              ([(S("quote"),1),(S("foo"),1)],1),
              ("bar",1),(S("quux"),1)],1)]
        assert l==l2

    def testBareNestedListQuotes(self):
        l=list(map(stripLines,parse('(17.3 12 (+ x y 17) \'foo "bar" quux)')))
        assert l==[[17.3,12,[S('+'),S('x'),S('y'),17],
                    q(S('foo')),'bar',S('quux')]]

    def testParseFile(self):
        thisFile=self.__class__.testParseFile.__code__.co_filename
        thisDir=os.path.split(thisFile)[0]
        codeFile=os.path.join(thisDir,'test-parse.+')
        l=list(parseFile(codeFile))
        l2=[([(S('defun'),1),(S('foo'),1),
              ([(S('x'),1),(S('y'),1)],1),
              ([(S('+'),2),(S('x'),2),
                ([(S('*'),2),(S('y'),2),(17,2)],2)
                ],2)
              ],1),
            ([(S('defun'),4),(S('bar'),4),
              ([(S('q'),4),(S('*bip'),4)],4),
              ([(S('bounding'),5),(S('bip'),5)
                ],5)
              ],4),
            ]
        assert l==l2

suite=unittest.TestSuite(
    ( unittest.makeSuite(LexerTestCase,'test'),
      unittest.makeSuite(ParserTestCase,'test')
     )
    )

unittest.TextTestRunner().run(suite)

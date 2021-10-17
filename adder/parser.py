from adder.symbol import intern

ATOM=1
OPEN=2
CLOSE=3
QUOTE=4
BACKQUOTE=5
COMMA=6
COMMA_AT=7
STRING=8

charEscapes={'a': '\a',
             'b': '\b',
             'f': '\f',
             'n': '\n',
             'r': '\r',
             't': '\t',
             'v': '\v',
             '\n': ''}

def escapeChar(ch):
    return charEscapes.get(ch,ch)

def lex(s,*,initLine=1):
    line=initLine
    curAtom=''
    inString=False
    inComment=False
    commaPendingAt=False
    escaped=False
    for ch in s:
        if commaPendingAt:
            commaPendingAt=False
            if ch=='@':
                yield (COMMA_AT,None,line)
                continue
            else:
                yield (COMMA,None,line)
                #do not continue; we want to lex the non-@ as normal
        if inComment:
            if ch=='\n':
                inComment=False
            continue
        if inString:
            if escaped:
                curAtom+=escapeChar(ch)
                escaped=False
                continue
            if ch=='\\':
                escaped=True
                continue
            if ch=='"':
                yield (STRING,curAtom,line)
                curAtom=''
                inString=False
            else:
                curAtom+=ch
            continue
                
        if ch.isspace():
            if curAtom:
                yield (ATOM,curAtom,line)
                curAtom=''
            if ch=='\n':
                line+=1
            continue
        if ch=='"':
            if curAtom:
                yield (ATOM,curAtom,line)
                curAtom=''
            inString=True
            continue
        if ch=="'":
            if curAtom:
                yield (ATOM,curAtom,line)
                curAtom=''
            yield (QUOTE,None,line)
            continue
        if ch=="`":
            if curAtom:
                yield (ATOM,curAtom,line)
                curAtom=''
            yield (BACKQUOTE,None,line)
            continue
        if ch==",":
            if curAtom:
                yield (ATOM,curAtom,line)
                curAtom=''
            commaPendingAt=True
            continue
        if ch=="(":
            if curAtom:
                yield (ATOM,curAtom,line)
                curAtom=''
            yield (OPEN,None,line)
            continue
        if ch==")":
            if curAtom:
                yield (ATOM,curAtom,line)
                curAtom=''
            yield (CLOSE,None,line)
            continue

        if ch==';':
            inComment=True
            continue
        curAtom+=ch
    if curAtom and not inString:
        yield (ATOM,curAtom,line)

def parse(s):
    def maybeQuote(x,quoteIt):
        if quoteIt:
            (sym,line)=quoteIt
            return ([(intern(sym),line),x],line)
        else:
            return x
    listStack=[]
    quotePending=None
    for (kind,arg,line) in lex(s):
        if kind==OPEN:
            listStack.append([quotePending,line])
            quotePending=None
            continue
        if kind==CLOSE:
            l=listStack.pop()
            lRes=maybeQuote((l[2:],l[1]),l[0])
            if listStack:
                listStack[-1].append(lRes)
            else:
                yield lRes
            quotePending=None
            continue
        if kind==QUOTE:
            quotePending=('quote',line)
            continue
        if kind==BACKQUOTE:
            quotePending=('backquote',line)
            continue
        if kind==COMMA:
            quotePending=(',',line)
            continue
        if kind==COMMA_AT:
            quotePending=(',@',line)
            continue
        if kind==ATOM:
            try:
                arg=int(arg)
            except ValueError as x:
                try:
                    arg=float(arg)
                except ValueError as x:
                    arg=intern(arg)
            a=maybeQuote((arg,line),quotePending)
            if listStack:
                listStack[-1].append(a)
            else:
                yield a
            quotePending=None
            continue
        if kind==STRING:
            if listStack:
                listStack[-1].append((arg,line))
            else:
                yield (arg,line)
            quotePending=None
            continue

def stripLines(ast):
    (bare,line)=ast
    if isinstance(bare,list):
        return list(map(stripLines,bare))
    return bare

def streamToChars(s):
    for line in s:
        for c in line:
            yield c

def parseStream(s):
    return parse(streamToChars(s))

def parseFile(f):
    return parseStream(open(f))

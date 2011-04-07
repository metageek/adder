import pdb,types,re

pythonLegal=re.compile('^[_a-z0-9A-Z]+$')

pythonReservedWords={'def','global','nonlocal','class','for','while','if'}

def isLegalPython(s):
    if s in pythonReservedWords:
        return False
    return pythonLegal.match(s)

def literable(x):
    return (x is None
            or type(x) in [int,str,float,bool])

class Symbol:
    registry={}
    def __new__(cls,s):
        if isinstance(s,Symbol):
            return s
        try:
            return Symbol.registry[s]
        except KeyError:
            res=super(Symbol,cls).__new__(cls)
            Symbol.registry[s]=res
            return res

    def __init__(self,s):
        if hasattr(self,'s'):
            return
        self.s=s
        self.isScratch=False
        self.h=None
        self.p=None

    def __getitem__(self,i):
        return self.s[i]

    def __len__(self):
        return len(self.s)

    def __str__(self):
        return self.s

    def __iter__(self):
        return iter(self.s)

    def __contains__(self,x):
        return x in self.s

    def __hash__(self):
        if self.h is None:
            self.h=7*hash(self.s)
        return self.h

    def __eq__(self,other):
        return ((self is other)
                or (type(other)==Symbol and self.s==other.s)
                )

    def __ne__(self,other):
        return not (self==other)

    def __ge__(self,other):
        return type(other)==Symbol and self.s>=other.s

    def __le__(self,other):
        return type(other)==Symbol and self.s<=other.s

    def __gt__(self,other):
        return type(other)==Symbol and self.s>other.s

    def __lt__(self,other):
        return type(other)==Symbol and self.s<other.s

    def startswith(self,prefix):
        return self.s.startswith(prefix)

    def isGensym(self):
        return self.startswith('#<gensym')

    def isKeyword(self):
        return (self[0]==':') and (self.s!=':=')

    def __repr__(self):
        return 'adder.common.Symbol('+repr(str(self))+')'

    def isLegalPython(self):
        return isLegalPython(self.s)

    def toPython(self):
        if self.p is None:
            if self.s=='..':
                self.p='_adder_dotdot_'
            else:
                if self.isLegalPython():
                    self.p=self.s
                else:
                    def escapeSegment(seg):
                        if isLegalPython(seg):
                            return seg
                        def escape1(ch):
                            if ch=='_':
                                return '_'
                            if pythonLegal.match(ch):
                                return ch
                            return '_%04x' % ord(ch)
                        return '_adder_'+''.join(map(escape1,seg))
                    self.p='.'.join(map(escapeSegment,self.s.split('.')))
        return self.p

def gensym(base=None):
    id=gensym.nextId
    gensym.nextId+=1
    name='#<gensym'
    if base:
        name+='-'+str(base)
    name+=' #'+str(id)+'>'
    return Symbol(name)

def mkScratch(base='scratch'):
    res=gensym(base)
    res.isScratch=True
    return res

def parseGensym(sym):
    if not (sym.startswith('#<gensym') and sym.endswith('>')):
        return (None,None)
    contents=sym[8:-1]
    if contents.startswith('-'):
        (base,contents)=contents[1:].split(' ')
    else:
        base=None
    if not contents.startswith('#'):
        return (None,None)
    try:
        i=int(contents[1:])
    except ValueError:
        return (None,None)
    return (base,i)

gensym.nextId=1

class DuplicateKeyError(Exception):
    def __init__(self,key):
        self.key=key

    def __str__(self):
        return 'Duplicate variable name: '+self.key

def q(value):
    if type(value) in [int,str,float,bool]:
        return value
    return [Symbol('quote'),value]

def isFunc(x):
    return isinstance(x,types.FunctionType) or isinstance(x,types.BuiltinFunctionType)

def adderStr(x):
    if type(x)==list:
        return '(%s)' % (' '.join(map(adderStr,x)))
    if type(x)==Symbol:
        return str(x)
    if isFunc(x):
        if hasattr(x,'__name__'):
            return '#<FUNCTION %s>' % x.__name__
    if type(x)==str:
        return '"'+x.replace('"','\\"')+'"'
    return repr(x)

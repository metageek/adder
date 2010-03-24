import pdb,types

class Symbol(str):
    def __repr__(self):
        return 'adder.common.Symbol('+repr(str(self))+')'

def gensym(base=None):
    id=gensym.nextId
    gensym.nextId+=1
    name='#<gensym'
    if base:
        name+='-'+base
    name+=' #'+str(id)+'>'
    return Symbol(name)

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
    if isinstance(value,str) and not isinstance(value,Symbol):
        value=Symbol(value)
    return [Symbol('quote'),value]

def isFunc(x):
    return isinstance(x,types.FunctionType) or isinstance(x,types.BuiltinFunctionType)

def adderStr(x):
    if isinstance(x,list):
        return '(%s)' % (' '.join(map(adderStr,x)))
    if isinstance(x,Symbol):
        return str(x)
    if isFunc(x):
        if hasattr(x,'__name__'):
            return '#<FUNCTION %s>' % x.__name__
    return repr(x)

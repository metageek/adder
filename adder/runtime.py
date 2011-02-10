import os
from adder.common import gensym, Symbol as S
import adder.compiler,adder.util
import pdb

def getScopeById(id):
    return getScopeById.scopes[id]
getScopeById.scopes={}

def eval(adderCode,scope,globalDict,localDict):
    from adder.gomer import geval

    parsedExpr=adder.compiler.addLines(adderCode,0)
    gomer=adder.compiler.stripAnnotations(adder.compiler.annotate(parsedExpr,
                                                                  scope,
                                                                  globalDict,
                                                                  localDict))
    return geval(gomer,globalDict=globalDict,localDict=localDict)

def load(f,scope,globalDict,cache):
    (lastValue,globalDict)=adder.compiler.loadFile(f,scope,globalDict,
                                                   cache=cache)
    return lastValue

def adder_function_wrapper(fSym,args,scopeOrId):
    localDict={}
    if isinstance(scopeOrId,adder.compiler.Scope):
        parentScope=scopeOrId
    else:
        parentScope=getScopeById(scopeOrId)
    scope=parentScope.mkChild()
    adderCode=[fSym]
    for (i,arg) in enumerate(args):
        name=S('a%d' % i)
        pyName=S('a%d-%d' % (i,scope.id)).toPython()
        localDict[pyName]=arg
        scope.addDef(name,None,1)
        adderCode.append(name)
    return eval(adderCode,scope,adder_function_wrapper.globals,localDict)

adder_function_wrapper.globals=None

def setupGlobals(f):
    if adder_function_wrapper.globals is None:
        adder_function_wrapper.globals=f()

def nativeMkDict(**d):
    return d

globals=__builtins__['globals']
locals=__builtins__['locals']

from adder.common import gensym, Symbol as S
import pdb

def getScopeById(id):
    return getScopeById.scopes[id]
getScopeById.scopes={}

def eval(adder,scope,globalDict,localDict):
    from adder.compiler import annotate,stripAnnotations,addLines
    from adder.gomer import geval

    parsedExpr=addLines(adder,0)
    gomer=stripAnnotations(annotate(parsedExpr,scope,globalDict,localDict))
    return geval(gomer,globalDict=globalDict,localDict=localDict)

def load(f,scope,globalDict):
    from adder.compiler import loadFile
    (lastValue,globalDict)=loadFile(f,scope,globalDict)
    return lastValue

def adder_function_wrapper(fSym,args,scopeId):
    localDict={}
    scope=getScopeById(scopeId).mkChild()
    adder=[fSym]
    for (i,arg) in enumerate(args):
        name=S('a%d' % i)
        pyName=S('a%d-%d' % (i,scope.id)).toPython()
        localDict[pyName]=arg
        scope.addDef(name,None,1)
        adder.append(name)
    return eval(adder,scope,adder_function_wrapper.globals,localDict)

adder_function_wrapper.globals=None

def setupGlobals(f):
    if adder_function_wrapper.globals is None:
        adder_function_wrapper.globals=f()

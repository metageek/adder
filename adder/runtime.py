from adder.common import gensym

def getScopeById(id):
    return getScopeById.scopes[id]
getScopeById.scopes={}

def eval(adder,scope,globalDict,localDict):
    from adder.compiler2 import annotate,stripAnnotations,addLines
    from adder.gomer import geval

    parsedExpr=addLines(adder,0)
    gomer=stripAnnotations(annotate(parsedExpr,scope,globalDict,localDict))
    return geval(gomer,globalDict=globalDict,localDict=localDict)

def load(f,scope,globalDict):
    from adder.compiler2 import loadFile
    (lastValue,globalDict)=loadFile(f,scope,globalDict)
    return lastValue

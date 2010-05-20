from adder.common import gensym

def getScopeById(id):
    return getScopeById.scopes[id]
getScopeById.scopes={}

def eval(adder,scope,globalDict,localDict):
    from adder.compiler2 import annotate,stripAnnotations
    from adder.gomer import geval

    def withLines(expr):
        if isinstance(expr,list):
            expr=list(map(withLines,expr))
        return (expr,0)

    parsedExpr=withLines(adder)
    gomer=stripAnnotations(annotate(parsedExpr,scope,globalDict,localDict))
    return geval(gomer,globalDict=globalDict,localDict=localDict)

def load(f,scope,globalDict):
    from adder.compiler2 import loadFile
    (lastValue,globalDict)=loadFile(f,scope,globalDict)
    return lastValue

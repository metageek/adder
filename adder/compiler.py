import pdb,os
from adder.common import Symbol as S, gensym, q, literable
import adder.gomer

def const(expr):
    if isinstance(expr,tuple):
        expr=expr[0]
    if expr is None:
        return (True,expr)
    for t in [int,float,str,bool]:
        if isinstance(expr,t):
            return (True,expr)
    if (isinstance(expr,list)
        and expr[0]
        and isinstance(expr[0],S)
        ):
        if expr[0] in const.knownFuncs:
            args=[]
            for arg in expr[1:]:
                (argConstP,argValue)=const(arg)
                if not argConstP:
                    return (False,None)
                args.append(argValue)
            try:
                return (True,const.knownFuncs[arg[0]](*args))
            except Exception:
                return (False,None)
        if expr[0]==S('quote'):
            assert len(expr)==2
            return (True,expr[1])
    return (False,None)

def times(*args):
    r=1
    for a in args:
        r=r*a
    return a

def minus(*args):
    if len(args)==0:
        return 0
    if len(args)==1:
        return -args[0]
    return args[0]-sum(args[1:])

def fdiv(*args):
    if len(args)==0:
        return 1
    if len(args)==1:
        return 1/args[0]
    r=args[0]
    for a in args[1:]:
        r=r/a
    return a

def idiv(*args):
    if len(args)==0:
        return 1
    if len(args)==1:
        return 1//args[0]
    r=args[0]
    for a in args[1:]:
        r=r//a
    return a

const.knownFuncs={
    S('+'): lambda *a: sum(a),
    S('-'): minus,
    S('*'): times,
    S('/'): fdiv,
    S('//'): idiv,
    }

class Undefined(Exception):
    def __init__(self,sym):
        Exception.__init__(self,sym)

    def __str__(self):
        return 'Undefined variable: %s' % self.args

class Redefined(Exception):
    def __init__(self,var,initExpr,oldEntry):
        Exception.__init__(self,var,initExpr,oldEntry)

    def __str__(self):
        return 'Variable redefined: %s defined as %s after being defined at %s' % self.args

class AssignedToConst(Exception):
    def __init__(self,var):
        Exception.__init__(self,var)

    def __str__(self):
        return 'Assigning to constant: %s' % self.args

class Scope:
    class Entry:
        def __init__(self,*,initExpr,line,
                     asConst=False,ignoreScopeId=False,
                     macroExpander=None,
                     isBuiltinFunc=False,
                     nativeFunc=None):
            self.initExpr=initExpr
            if initExpr is None:
                (self.constValueValid,self.constValue)=(False,None)
            else:
                (self.constValueValid,self.constValue)=const(initExpr)
            self.line=line
            self.asConst=asConst
            self.ignoreScopeId=ignoreScopeId
            self.macroExpander=macroExpander
            self.isBuiltinFunc=isBuiltinFunc
            self.nativeFunc=nativeFunc if isBuiltinFunc else None

    nextId=1

    def __init__(self,parent,*,isRoot=False,isClassScope=False):
        self.entries={}
        id=None

        if parent is None:
            if isRoot:
                self.parent=None
                id=0
            else:
                self.parent=Scope.root
        else:
            self.parent=parent

        if id is None:
            self.id=Scope.nextId
            Scope.nextId+=1
        else:
            self.id=id
        self.readOnly=False
        self.isClassScope=isClassScope

        self.addConst(S('current-scope'),self,0,ignoreScopeId=True)

    root=None

    def mkChild(self):
        return Scope(self)

    def __repr__(self):
        return 'adder.runtime.getScopeById(%d)' % self.id

    def addDef(self,name,initExpr,line,*,
               asConst=False,
               ignoreScopeId=False,
               macroExpander=None,
               redefPermitted=False,
               isBuiltinFunc=False,
               nativeFunc=None):
        if self.isClassScope:
            ignoreScopeId=True
        assert not self.readOnly
        if name in self.entries and not redefPermitted:
            raise Redefined(name,initExpr,self.entries[name])
        self.entries[name]=Scope.Entry(initExpr=initExpr,
                                       line=line,
                                       asConst=asConst,
                                       ignoreScopeId=ignoreScopeId,
                                       macroExpander=macroExpander,
                                       isBuiltinFunc=isBuiltinFunc,
                                       nativeFunc=nativeFunc)

    def addConst(self,name,value,line,*,
                 ignoreScopeId=False):
        self.addDef(name,q(value),line,
                    asConst=True,
                    ignoreScopeId=ignoreScopeId)

    def __iter__(self):
        cur=self
        already=set()
        while cur is not None:
            if not cur.isClassScope:
                for key in self.entries:
                    if key not in already:
                        already.add(key)
                        yield key
            cur=cur.parent

    def __len__(self):
        cur=self
        already=set()
        res=0
        while cur is not None:
            if not cur.isClassScope:
                for key in self.entries:
                    if key not in already:
                        already.add(key)
                        res+=1
            cur=cur.parent
        return res

    def get(self,key,*,skipClassScopes=True):
        cur=self
        while cur is not None:
            if not (skipClassScopes and cur.isClassScope):
                if key in cur.entries:
                    return cur.entries[key]
            cur=cur.parent
        raise Undefined(key)

    def __getitem__(self,key):
        return self.get(key)

    def requiredScope(self,sym,*,skipClassScopes=True):
        if  not (skipClassScopes and self.isClassScope):
            if sym in self.entries:
                return self
        if self.parent is not None:
            return self.parent.requiredScope(sym,
                                             skipClassScopes=skipClassScopes)
        raise Undefined(sym)

Scope.root=Scope(None,isRoot=True)
for name in ['not',
             '==','!=','<=','<','>=','>',
             '+','-','*','/','//','%','in',
             'print','gensym','[]','getattr','slice','isinstance',
             'list','tuple','set','dict',
             'mk-list','mk-tuple','mk-set','mk-symbol',
             'reverse','stdenv','apply','eval','exec-py',
             'getScopeById','globals','locals',
             'load','adder_function_wrapper'
             ]:
    Scope.root.addDef(S(name),None,0,redefPermitted=True,isBuiltinFunc=True)

for (name,native) in [('mk-dict','nativeMkDict'),
                      ('globals','globals'),
                      ('locals','locals')]:
    Scope.root.addDef(S(name),None,0,redefPermitted=True,isBuiltinFunc=True,
                      nativeFunc=native)

for name in ['and','or',':=','.',
             'adder','python',
             'class','defun','lambda','defvar','scope','try',
             'quote','backquote',
             'import',
             'if','while','break','continue','begin',
             'yield', 'return','raise',
             'defconst',
             #'getScopeById','globals','locals',
             'defmacro','adder_function_wrapper'
             ]:
    Scope.root.addDef(S(name),None,0,redefPermitted=True,isBuiltinFunc=True)
    Scope.root.addDef(S(name),None,0,redefPermitted=True)

Scope.root.addConst(S('true'),True,0)
Scope.root.addConst(S('false'),False,0)
Scope.root.addConst(S('none'),None,0)
Scope.root.readOnly=True

class Annotator:
    pynamesForSymbols={'.': 'dot', ':=': 'assign'}
    def methodFor(self,f):
        s=str(f)
        if s in Annotator.pynamesForSymbols:
            s=Annotator.pynamesForSymbols[s]
        return 'annotate_%s' % s.replace('-','_')

    def wrapForApply(self,expr,line,scope,entry):
        if entry.nativeFunc:
            return ([(S('.'),line,),
                     (S('adder'),line),
                     (S('runtime'),line),
                     (S(entry.nativeFunc),line)],
                     line)
        adder.runtime.setupGlobals(adder.gomer.mkGlobals)
        adder.runtime.getScopeById.scopes[scope.id]=scope
        return ([(S('lambda'),line),
                 ([(S('&rest'),line),(S('args'),line)],line),
                 ([(S('adder_function_wrapper'),line),
                   ([(S('quote'),line),(expr,line)],line),
                   (S('args'),line),
                   (scope.id,line)
                   ],line)
                 ],line)

    def __call__(self,parsedExpr,scope,globalDict,localDict,*,asFunc=False):
        try:
            (expr,line)=parsedExpr
        except ValueError as ve:
            print(ve,parsedExpr)
            raise
        if expr and isinstance(expr,list):
            if isinstance(expr[0][0],S):
                f=expr[0][0]
                required=scope.requiredScope(f)
                if required is Scope.root:
                    m=self.methodFor(f)
                    if hasattr(self,m):
                        return getattr(self,m)(expr,line,scope,
                                               globalDict,localDict)
                if required[f].macroExpander:
                    xArgs=stripLines((expr[1:],expr[1][1]))
                    expanded=required[f].macroExpander(xArgs,
                                                       scope,
                                                       globalDict,
                                                       localDict)
                    return self(addLines(expanded,line),
                                scope,globalDict,localDict)
            scoped=([self(expr[0],scope,globalDict,localDict,asFunc=True)]
                    +list(map(lambda e: self(e,scope,globalDict,localDict),
                              expr[1:])))
            return (scoped,line,scope)
        if isinstance(expr,S):
            if expr.isKeyword():
                return (expr,line,Scope.root)
            else:
                if str(expr)=='current-scope':
                    adder.runtime.getScopeById.scopes[scope.id]=scope
                    return self(([(S('getScopeById'),line),
                                  (scope.id,line)],line),scope,
                                globalDict,localDict)
                required=scope.requiredScope(expr)

                exprPy=expr.toPython()
                if (required is Scope.root
                    and exprPy in globalDict
                    and literable(globalDict[exprPy])):
                    return (globalDict[exprPy],line,required)
                if (required is scope
                    and exprPy in localDict
                    and literable(localDict[exprPy])):
                    return (localDict[exprPy],line,required)

                entry=required[expr]

                if entry.isBuiltinFunc and not asFunc:
                    return self(self.wrapForApply(expr,line,scope,entry),
                                scope,globalDict,localDict)

                if (entry.asConst
                    and entry.constValueValid
                    and (isinstance(entry.constValue,int)
                         or isinstance(entry.constValue,float)
                         or isinstance(entry.constValue,str)
                         or isinstance(entry.constValue,bool)
                         )
                    ):
                    expr=entry.constValue
                return (expr,line,required)
        return (expr,line,scope)

    def annotate_try(self,expr,line,scope,globalDict,localDict):
        gomerBody=[]
        gomerClauses=None
        for (stmtOrClause,stmtOrClauseLine) in expr[1:]:
            if (isinstance(stmtOrClause,list)
                and isinstance(stmtOrClause[0][0],S)
                and stmtOrClause[0][0].isKeyword()):
                clauseScope=Scope(scope)
                if not gomerClauses:
                    gomerClauses=[]
                (exnClass,exnClassLine)=stmtOrClause[0]
                if exnClass is S(':finally'):
                    if len(stmtOrClause)>1:
                        exnBodyLine=stmtOrClause[1][1]
                        exnBody=(([(S('begin'),exnBodyLine,Scope.root)]
                                  +list(map(lambda e:
                                                self(e,clauseScope,
                                                     globalDict,localDict),
                                            stmtOrClause[1:]))),
                                 exnBodyLine,clauseScope)
                        gomerClauses.append(([(S(':finally'),
                                               exnClassLine,scope),
                                              exnBody],exnClassLine,scope))
                        
                    else:
                        pass # "finally: pass" can be optimized out
                else:
                    (exnVar,exnVarLine)=stmtOrClause[1]
                    clauseScope.addDef(exnVar,None,exnVarLine)
                    if len(stmtOrClause)>2:
                        exnBodyLine=stmtOrClause[2][1]
                        exnBody=(([(S('begin'),exnBodyLine,Scope.root)]
                                  +list(map(lambda e:
                                                self(e,clauseScope,
                                                     globalDict,localDict),
                                            stmtOrClause[2:]))),
                                 exnBodyLine,clauseScope)
                    else:
                        exnBody=([(S('pass'),exnVarLine,clauseScope)],
                                 exnVarLine,clauseScope)
                    gomerClauses.append(([(exnClass,exnClassLine,scope),
                                          (exnVar,exnVarLine,clauseScope),
                                          exnBody
                                          ],exnClassLine,scope))
            else:
                assert not gomerClauses
                gomerBody.append(self((stmtOrClause,stmtOrClauseLine),
                                      scope,globalDict,localDict))
        return ([(S('try'),line,Scope.root),
                 ([(S('begin'),line,Scope.root)]+gomerBody,line,scope)
                 ]+gomerClauses,
                line,scope)

    def annotate_defmacro(self,expr,line,scope,globalDict,localDict):
        (name,nameLine)=expr[1]
        expanderName=gensym('macro-'+('dot-dot' if str(name)=='..'
                                      else str(name)))
        def expand(xArgs,xScope,xGlobalDict,xLocalDict):
            xCall=[expanderName]+list(map(q,xArgs))
            return adder.runtime.eval(xCall,xScope,xGlobalDict,xLocalDict)
        scope.addDef(name,None,line,macroExpander=expand,redefPermitted=True)
        return self(([(S('defun'),line),(expanderName,line)]+expr[2:],
                     line),
                    scope,globalDict,localDict)

    def annotate_assign(self,expr,line,scope,globalDict,localDict):
        assert len(expr)==3
        (lhs,lhsLine)=expr[1]
        if isinstance(lhs,S):
            entry=scope[lhs]
            if entry.asConst:
                raise AssignedToConst(lhs)
        return ([(S(':='),line,Scope.root),
                 self(expr[1],scope,globalDict,localDict),
                 self(expr[2],scope,globalDict,localDict)],
                line,scope)
    
    def annotate_eval(self,expr,line,scope,globalDict,localDict):
        assert len(expr)>=2 and len(expr)<=4
        adderArg=self(expr[1],scope,globalDict,localDict)
        scopeArg=self((S('current-scope'),line),scope,globalDict,localDict)
        if len(expr)>=3:
            globalArg=self(expr[2],scope,globalDict,localDict)
        else:
            globalArg=self(([(S('globals'),line)],line),scope,
                           globalDict,localDict)
        if len(expr)>=4:
            localArg=self(expr[3],scope,globalDict,localDict)
        else:
            localArg=self(([(S('locals'),line)],line),scope,
                          globalDict,localDict)
        return ([self(expr[0],scope,globalDict,localDict,asFunc=True),
                 adderArg,scopeArg,globalArg,localArg],line,scope)
    
    def annotate_load(self,expr,line,scope,globalDict,localDict):
        assert len(expr)>=2 and len(expr)<=3
        fileArg=self(expr[1],scope,globalDict,localDict)
        scopeArg=self((S('current-scope'),line),scope,globalDict,localDict)
        if len(expr)==3:
            globalArg=self(expr[2],scope,globalDict,localDict)
        else:
            globalArg=self(([(S('globals'),line)],line),scope,
                           globalDict,localDict)
        return ([self(expr[0],scope,globalDict,localDict,asFunc=True),
                 fileArg,scopeArg,globalArg],line,scope)

    def annotate_exec_py(self,expr,line,scope,globalDict,localDict):
        assert len(expr)>=2 and len(expr)<=4
        pyArg=self(expr[1],scope,globalDict,localDict)
        if len(expr)>=3:
            globalArg=self(expr[2],scope,globalDict,localDict)
        else:
            globalArg=self(([(S('globals'),line)],line),scope,
                           globalDict,localDict)
        if len(expr)>=4:
            localArg=self(expr[3],scope,globalDict,localDict)
        else:
            localArg=self(([(S('locals'),line)],line),scope,
                          globalDict,localDict)
        return ([self(([(S('.'),line),
                        (S('python'),line),
                        (S('exec'),line)],
                       line),scope,globalDict,localDict),
                 pyArg,globalArg,localArg],line,scope)

    def annotate_scope(self,expr,line,scope,globalDict,localDict):
        scopedScope=self(expr[0],scope,globalDict,localDict,asFunc=True)
        childScope=Scope(scope)
        scopedChildren=list(map(lambda e: self(e,childScope,
                                               globalDict,localDict),
                                expr[1:]))
        return ([scopedScope]+scopedChildren,line,scope)

    def annotate_quote(self,expr,line,scope,globalDict,localDict):
        return self.quoteOrImport(expr,line,scope,True,
                                  globalDict,localDict)

    def annotate_import(self,expr,line,scope,globalDict,localDict):
        res=self.quoteOrImport(expr,line,scope,False,
                               globalDict,localDict)
        for (pkg,pkgLine) in expr[1:]:
            scope.addDef(S(str(pkg).split('.')[0]),None,pkgLine,
                         ignoreScopeId=True,redefPermitted=True)
        return res

    def quoteOrImport(self,expr,line,scope,justOneArg,globalDict,localDict):
        def annotateDumbly(parsedExpr):
            try:
                (expr,line)=parsedExpr
            except ValueError as ve:
                print(ve,parsedExpr)
                raise
            if isinstance(expr,list):
                return [list(map(annotateDumbly,expr)),line,scope]
            else:
                return (expr,line,scope)

        if justOneArg:
            assert len(expr)==2
            args=[expr[1]]
        else:
            args=expr[1:]
            
        return (([self(expr[0],scope,globalDict,localDict,asFunc=True)]
                 +list(map(annotateDumbly,args))
                 ),
                line,scope)

    def annotate_backquote(self,expr,line,scope,globalDict,localDict):
        assert len(expr)==2
        (arg,argLine)=expr[1]
        if not isinstance(arg,list):
            expr=[(S('quote'),expr[0][1]),expr[1]]
            return self.annotate_quote(expr,line,scope,
                                       globalDict,localDict)
        sublists=[]
        curSublist=[]
        curSublistFirstLine=None

        for (a,aLine) in arg:
            if isinstance(a,list) and a[0][0] is S(',@'):
                if curSublist:
                    sublists.append(([(S('mk-list'),
                                       curSublistFirstLine,
                                       Scope.root)]+curSublist,
                                     curSublistFirstLine,scope))
                    curSublist=[]
                    curSublistFirstLine=None
                sublists.append(self(([(S('list'),aLine),a[1]],aLine),
                                     scope,globalDict,localDict))
                continue
            if (isinstance(a,int)
                or isinstance(a,str)
                or isinstance(a,float)
                or isinstance(a,bool)):
                curItem=(a,aLine,scope)
            else:
                if isinstance(a,list) and a[0][0] is S(','):
                    curItem=self(a[1],scope,globalDict,localDict)
                else:
                    curItem=self(([(S('backquote'),aLine),(a,aLine)],aLine),
                                 scope,globalDict,localDict)
            if not curSublist:
                curSublistFirstLine=aLine
            curSublist.append(curItem)
        if curSublist:
            sublists.append(([(S('mk-list'),
                               curSublistFirstLine,
                               Scope.root)]+curSublist,
                             curSublistFirstLine,scope))
        if len(sublists)==1:
            return sublists[0]
        else:
            return ([(S('+'),line,Scope.root)]+sublists,
                    line,scope)

    def annotate_dot(self,expr,line,scope,globalDict,localDict):
        def annotateDumbly(parsedExpr):
            (expr,line)=parsedExpr
            assert isinstance(expr,S)
            return (expr,line,scope)

        return (([self(expr[0],scope,globalDict,localDict,asFunc=True),
                  self(expr[1],scope,globalDict,localDict)
                  ]
                 +list(map(annotateDumbly,expr[2:]))
                 ),
                line,scope)

    def annotate_defvar(self,expr,line,scope,globalDict,localDict):
        return self.defvarOrDefconst(expr,line,scope,False,
                                     globalDict,localDict)

    def annotate_defconst(self,expr,line,scope,globalDict,localDict):
        return self.defvarOrDefconst(expr,line,scope,True,
                                     globalDict,localDict)

    def defvarOrDefconst(self,expr,line,scope,asConst,globalDict,localDict):
        scopedDef=self((S(':='),expr[0][1]),scope,globalDict,localDict,
                       asFunc=True)
        scopedInitExpr=self(expr[2],scope,globalDict,localDict)
        scope.addDef(expr[1][0],scopedInitExpr,expr[1][1],
                     asConst=asConst,redefPermitted=not asConst)
        scopedVar=(expr[1][0],expr[1][1],scope)
        return ([scopedDef,
                 scopedVar,scopedInitExpr],line,scope)

    def annotate_class(self,expr,line,scope,globalDict,localDict):
        classScope=Scope(scope,isClassScope=True)
        namePE=expr[1]
        scope.addDef(namePE[0],namePE[1],None,redefPermitted=True)
        return (([(S('class'),expr[0][1],Scope.root),
                  (namePE[0],namePE[1],scope),
                  (list(map(lambda e: self(e,scope,globalDict,localDict),
                            expr[2][0])),
                   expr[2][1],
                   scope)
                  ]
                 +list(map(lambda e: self(e,classScope,globalDict,localDict),
                           expr[3:]))
                 ),
                line,scope)

    def annotate_defun(self,expr,line,scope,globalDict,localDict):
        return self.defunOrLambda(expr[0],expr[1],expr[2],expr[3:],
                                  line,scope,globalDict,localDict)

    def annotate_lambda(self,expr,line,scope,globalDict,localDict):
        return self.defunOrLambda(expr[0],None,expr[1],expr[2:],
                                  line,scope,globalDict,localDict)

    def defunOrLambda(self,opPE,namePE,argsPE,bodyPEs,
                      line,scope,globalDict,localDict):
        childScope=Scope(scope)
        def doArg(arg):
            (argExpr,argLine)=arg
            if argExpr[0]=='&':
                return (argExpr,argLine,scope)
            childScope.addDef(argExpr,argLine,None)
            return (argExpr,argLine,childScope)
        scoped=[self(opPE,scope,globalDict,localDict,asFunc=True)]
        if namePE:
            scope.addDef(namePE[0],namePE[1],None,redefPermitted=True)
            scoped.append((namePE[0],namePE[1],scope))
        (argsExpr,argsLine)=argsPE
        scoped.append((list(map(doArg,argsExpr)),argsLine,scope))
        for parsedExpr in bodyPEs:
            scoped.append(self(parsedExpr,childScope,globalDict,localDict))
        return (scoped,line,scope)

    def annotate_scope(self,expr,line,scope,globalDict,localDict):
        childScope=Scope(scope)
        return (([(S('begin'),expr[0][1],Scope.root)]
                 +list(map(lambda e: self(e,childScope,globalDict,localDict),
                           expr[1:]))
                 ),
                line,scope)

def annotate(parsedExpr,scope,globalDict,localDict):
    if globalDict is None:
        globalDict=adder.gomer.mkGlobals()
    if localDict is None:
        localDict=globalDict
    return annotate.annotator(parsedExpr,scope,globalDict,localDict)
annotate.annotator=Annotator()

def stripAnnotations(annotated,*,quoted=False):
    try:
        (expr,line,scope)=annotated
    except ValueError as ve:
        print(ve,annotated)
        raise
    if (not quoted
        and isinstance(expr,S)
        and not expr.isKeyword()):
        if expr is S('&rest'):
            return expr
        if (scope.id>0
            and not scope.get(expr,skipClassScopes=False).ignoreScopeId):
            return S('%s-%d' % (str(expr),scope.id))
    if not (expr and isinstance(expr,list)):
        return expr
    if not quoted and expr[0][0] in [S('quote'),S('import')]:
        return ([expr[0][0]]
                +list(map(lambda e: stripAnnotations(e,quoted=True),expr[1:]))
                )
    if not quoted and expr[0][0]==S('.'):
        return ([expr[0][0],
                 stripAnnotations(expr[1])]
                 +list(map(lambda e: stripAnnotations(e,quoted=True),
                           expr[2:]))
                )
    return list(map(lambda e: stripAnnotations(e,quoted=quoted),expr))

def addLines(expr,defLine):
    if literable(expr) or isinstance(expr,S):
        return (expr,defLine)
    assert isinstance(expr,list)
    return (list(map(lambda e: addLines(e,defLine),expr)),defLine)

def stripLines(parsedExpr):
    (expr,line)=parsedExpr
    if literable(expr) or isinstance(expr,S):
        return expr
    assert isinstance(expr,list)
    return list(map(stripLines,expr))

def compileAndEval(expr,scope,globalDict,localDict,*,
                   hasLines=False,defLine=0,
                   verbose=False):
    if scope is None:
        scope=Scope(None)
    if globalDict is None:
        globalDict=adder.gomer.mkGlobals()
    if localDict is None:
        localDict=globalDict

    if not hasLines:
        expr=addLines(expr,defLine)
    annotated=annotate(expr,scope,globalDict,localDict)
    gomer=stripAnnotations(annotated)
    return adder.gomer.geval(gomer,
                             globalDict=globalDict,
                             localDict=localDict,
                             verbose=verbose)

def loadFile(f,scope,globalDict,*,inSrcDir=False):
    if scope is None:
        scope=Scope(None)
    if globalDict is None:
        globalDict=adder.gomer.mkGlobals()
    res=None

    if inSrcDir:
        srcFile=loadFile.__code__.co_filename
        srcDir=os.path.split(srcFile)[0]
        f=os.path.join(srcDir,f)

    for parsedExpr in adder.parser.parseFile(f):
        res=compileAndEval(parsedExpr,scope,
                           globalDict,None,
                           hasLines=True)
    return (res,globalDict)

class Context:
    def __init__(self,*,loadPrelude=True):
        self.scope=Scope(None)
        self.globals=adder.gomer.mkGlobals()
        if loadPrelude:
            self.load('prelude.+',inSrcDir=True)

    def load(self,f,*,inSrcDir=False):
        loadFile(f,self.scope,self.globals,inSrcDir=inSrcDir)

    def eval(self,expr,*,verbose=False,hasLines=False,defLine=0):
        return compileAndEval(expr,
                              self.scope,self.globals,
                              None,
                              hasLines=hasLines,defLine=defLine,
                              verbose=verbose)

    def define(self,name,value):
        self.scope.addDef(S(name),value,0,redefPermitted=True)
        self.globals[S("%s-1" % name).toPython()]=value

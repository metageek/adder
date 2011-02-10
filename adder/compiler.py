import pdb,os,pickle,io
from adder.common import Symbol as S, gensym, q, literable, mkScratch
import adder.gomer,adder.parser,adder.util

def const(expr):
    if type(expr)==tuple:
        expr=expr[0]
    if literable(expr):
        return (True,expr)
    if (type(expr)==list
        and expr
        and type(expr[0])==S
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
        if expr[0] is S('quote'):
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

class UndefinedInModule(Exception):
    def __init__(self,sym,module):
        Exception.__init__(self,sym,module)

    def __str__(self):
        return "Can't find variable %s in module %s" % self.args

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

class SyntaxError(Exception):
    def __init__(self,line,expr):
        Exception.__init__(self,line,expr)

    def __str__(self):
        return 'Syntax error at line %d: %s' % self.args

def listPickle(obj):
    byteStream=io.BytesIO()
    pickle.dump(obj,byteStream)
    byteStream.flush()
    byteStream.seek(0)
    return list(byteStream.read())

def listDepickle(byteList):
    byteStream=io.BytesIO(bytes(byteList))
    return pickle.load(byteStream)

class Scope:
    nextId=1

    class Entry:
        def __init__(self,*,initExpr,line,
                     asConst=False,ignoreScopeId=False,
                     macroExpander=None,
                     isBuiltinFunc=False,
                     nativeFunc=None):
            self.initExpr=None#initExpr
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

        def flatten(self):
            # We don't need to serialize isBuiltinFunc or nativeFunc,
            #  because they're only for the root env, which doesn't
            #  get serialized.  And macroExpander is no longer a
            #  function, so that's easy.
            cucumber={'initExpr' : self.initExpr,
                      'line': self.line,
                      'asConst': self.asConst,
                      'ignoreScopeId': self.ignoreScopeId,
                      'macroExpander': self.macroExpander
                      }
            if self.constValueValid:
                cucumber['constValue']=self.constValue
            return cucumber

        def expand(cucumber):
            return Scope.Entry(initExpr=cucumber['initExpr'],
                               line=cucumber['line'],
                               asConst=cucumber['asConst'],
                               ignoreScopeId=cucumber['ignoreScopeId'],
                               macroExpander=cucumber['macroExpander'])

    def __init__(self,parent,*,
                 isRoot=False,
                 isClassScope=False,
                 isFuncScope=False,
                 trackDescendants=False,
                 idFromCucumber=None,
                 context=None):
        self.entries={}
        id=idFromCucumber

        if parent is None:
            if isRoot:
                self.parent=None
                id=0
            else:
                self.parent=Scope.root
            self.context=context
        else:
            self.parent=parent
            self.context=self.parent.context

        if self.parent:
            self.parent.addChild(self)

        if id is None:
            self.id=Scope.nextId
            Scope.nextId+=1
            if self.context:
                self.id=abs(hash((self.context.cacheOutputFileName,self.id)))
        else:
            self.id=id
        self.readOnly=False
        self.isClassScope=isClassScope
        self.isFuncScope=isFuncScope

        self.addConst(S('current-scope'),self,0,ignoreScopeId=True)

        if trackDescendants:
            self.descendants=[self]
        else:
            self.descendants=None

    root=None

    def addChild(self,child):
        if self.descendants:
            self.descendants.append(child)
        else:
            if self.parent:
                self.parent.addChild(child)

    def flatten(self,*,suppress=None):
        if suppress is None:
            suppress=set()
        assert self.parent
        cucumber={'id': self.id,
                  'parent': self.parent,
                  'readOnly': self.readOnly,
                  'isClassScope': self.isClassScope,
                  'isFuncScope': self.isFuncScope,
                  'entries': {}}
        for (name,entry) in self.entries.items():
            if name not in suppress:
                cucumber['entries'][name]=entry.flatten()
        return cucumber

    def expand(cucumber):
        scope=Scope(cucumber['parent'],
                    idFromCucumber=cucumber['id'],
                    isClassScope=cucumber['isClassScope'],
                    isFuncScope=cucumber['isFuncScope'])
        scope.readOnly=cucumber['readOnly']
        for (name,entryCucumber) in cucumber['entries'].items():
            scope.entries[name]=Scope.Entry.expand(entryCucumber)
        adder.runtime.getScopeById.scopes[scope.id]=scope
        return scope

    def varNameForCache(self):
        return '__adder__module_scope_%d__' % self.id

    def dump(self,outputStream):
        oldReprForCache=Scope.reprForCache
        Scope.reprForCache=True
        for scope in self.descendants:
            outputStream.writelines([
                    scope.varNameForCache(),
                    '=adder.compiler.Scope.expand(',
                    repr(scope.flatten(suppress={S('current-scope')})),
                    ')\n'
                    ])
        outputStream.writelines(['__adder__module_scope__=',
                                 self.varNameForCache(),
                                 '\n'])
        Scope.reprForCache=oldReprForCache

    def atGlobalScope(self):
        if self.isFuncScope:
            return False
        if not self.parent:
            return True
        return self.parent.atGlobalScope()

    def mkChild(self):
        return Scope(self)

    reprForCache=False
    def __repr__(self):
        if Scope.reprForCache:
            if self.parent:
                return self.varNameForCache()
            else:
                return 'adder.compiler.Scope.root'
        else:
            return 'adder.runtime.getScopeById(%d)' % self.id

    def addDef(self,name,initExpr,line,*,
               asConst=False,
               ignoreScopeId=False,
               macroExpander=None,
               redefPermitted=False,
               isBuiltinFunc=False,
               nativeFunc=None):
        assert not (isBuiltinFunc and self.parent)
        assert not (nativeFunc and self.parent)

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

    def addModule(self,module,moduleLine,asName,targets):
        #if module is S('html'):
        #    pdb.set_trace()
        moduleName=asName or module
        targetLimitationList=None if targets is S('*') else targets
        if targets and isinstance(targets,list):
            targetExpectedSet=set(targets)
        else:
            targetExpectedSet=set()
        g={}
        exec("import %s" % module,g)
        parts=str(module).split('.')
        if not targets:
            self.addDef(asName or S(parts[0]),None,moduleLine,
                        ignoreScopeId=True,redefPermitted=True)
        mod=g[parts[0]]
        for part in parts[1:]:
            mod=getattr(mod,part)
        if hasattr(mod,'__adder__module_scope__'):
            scope=mod.__adder__module_scope__
            for name in scope:
                if '.' in str(name):
                    continue
                if targetLimitationList and name not in targetLimitationList:
                    if targetExpectedSet:
                        continue
                    else:
                        break
                entry=scope[name]
                if not (targets or entry.macroExpander):
                    continue
                if targets:
                    localName=name
                    if targetExpectedSet:
                        targetExpectedSet.remove(localName)
                else:
                    localName=S('%s.%s' % (moduleName,str(name)))
                if entry.macroExpander:
                    localExpander=S('%s.%s-%d' % (moduleName,
                                                  str(entry.macroExpander),
                                                  scope.id
                                                  )
                                    )
                else:
                    localExpander=None
                self.addDef(localName,None,moduleLine,
                            ignoreScopeId=True,redefPermitted=True,
                            macroExpander=localExpander
                            )
                if targets and not (entry.macroExpander
                                    or name is S('current-scope')
                                    ):
                    code=([(S('defvar'),moduleLine),
                           (S('%s-%d' % (str(name),self.id)),moduleLine),
                           (name,moduleLine)],
                          moduleLine)
                    yield (name,code)
            if targetExpectedSet:
                raise UndefinedInModule(next(iter(targetExpectedSet)),
                                        module)

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

    def iterDontAscend(self):
        return iter(self.entries)

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

    def isMacro(self,sym):
        try:
            scope=self.requiredScope(sym)
        except Undefined:
            return False
        entry=scope[sym]
        return not (not entry.macroExpander)

    def isDescendantOf(self,other):
        if self is other:
            return True
        if self.parent is not None:
            return self.parent.isDescendantOf(other)
        return False

    def serialize(self,outputStream):
        outputStream.write('None')

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
             'class','defun','lambda','defvar','scope','extern','try',
             'quote','backquote',
             'import',
             'if','while','break','continue','begin',
             'yield', 'return','raise',
             'defconst',
             #'getScopeById','globals','locals',
             'defmacro','adder_function_wrapper',
             '__adder__last__'
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
        if type(expr)==list and expr:
            if type(expr[0][0])==S:
                (f,_,_)=self(expr[0],scope,globalDict,localDict,asFunc=True)
                if isinstance(f,S):
                    required=scope.requiredScope(f)
                    if required is Scope.root:
                        m=self.methodFor(f)
                        if hasattr(self,m):
                            return getattr(self,m)(expr,line,scope,
                                                   globalDict,localDict)
                    if required[f].macroExpander:
                        xArgs=stripLines((expr[1:],expr[1][1]))
                        xCall=[required[f].macroExpander]+list(map(q,xArgs))
                        expanded=adder.runtime.eval(xCall,scope,
                                                    globalDict,localDict)
                        return self(addLines(expanded,line),
                                    scope,globalDict,localDict)
            scoped=[self(expr[0],scope,globalDict,localDict,asFunc=True)]
            for e in expr[1:]:
                scoped.append(self(e,scope,globalDict,localDict))
            return (scoped,line,scope)
        if type(expr)==S:
            if expr.isKeyword():
                return (expr,line,Scope.root)
            else:
                symbolName=str(expr)
                if symbolName=='current-scope':
                    adder.runtime.getScopeById.scopes[scope.id]=scope
                    return self(([(S('getScopeById'),line),
                                  (scope.id,line)],line),scope,
                                globalDict,localDict)

                if ((symbolName!='.')
                    and ('.' in symbolName)
                    and not (asFunc and scope.isMacro(expr))
                    ):
                    op='..' if symbolName[0]=='.' else '.'
                    expanded=[op]+list(filter(None,symbolName.split('.')))
                    expanded=list(map(lambda s: (S(s),line),expanded))
                    return self((expanded,line),
                                scope,globalDict,localDict,asFunc=asFunc)

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
                    and (type(entry.constValue)==int
                         or type(entry.constValue)==float
                         or type(entry.constValue)==str
                         or type(entry.constValue)==bool
                         )
                    ):
                    expr=entry.constValue
                return (expr,line,required)
        return (expr,line,scope)

    def annotate_try(self,expr,line,scope,globalDict,localDict):
        gomerBody=[]
        gomerClauses=None
        for (stmtOrClause,stmtOrClauseLine) in expr[1:]:
            if (type(stmtOrClause)==list
                and type(stmtOrClause[0][0])==S
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
        scope.addDef(name,None,line,
                     macroExpander=expanderName,
                     redefPermitted=True)
        return self(([(S('defun'),line),(expanderName,line)]+expr[2:],
                     line),
                    scope,globalDict,localDict)

    def annotate_assign(self,expr,line,scope,globalDict,localDict):
        assert len(expr)==3
        (lhs,lhsLine)=expr[1]
        if type(lhs)==S:
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
        assert len(expr)>=2
        cacheArg=None
        fileArg=self(expr[1],scope,globalDict,localDict)
        scopeArg=self((S('current-scope'),line),scope,globalDict,localDict)
        globalArg=None
        if len(expr)>2:
            i=2
            sawKeyword=False
            while i<len(expr):
                (arg,argLine)=expr[i]
                if isinstance(arg,S) and arg.isKeyword():
                    assert (i+1)<len(expr)
                    value=self(expr[i+1],scope,globalDict,localDict)
                    assert(arg is S(':cache'))
                    assert(cacheArg is None)
                    cacheArg=value
                    sawKeyword=True
                    i+=2
                else:
                    assert(not sawKeyword)
                    assert(globalArg is None)
                    globalArg=self(expr[i],scope,globalDict,localDict)
                    i+=1

        if globalArg is None:
            globalArg=self(([(S('globals'),line)],line),scope,
                           globalDict,localDict)
        if cacheArg is None:
            cacheArg=self((S('none'),line),scope,
                           globalDict,localDict)
        return ([self(expr[0],scope,globalDict,localDict,asFunc=True),
                 fileArg,scopeArg,globalArg,cacheArg],line,scope)

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

    def annotate_quote(self,expr,line,scope,globalDict,localDict):
        return self.quoteOrImport(expr,line,scope,True,
                                  globalDict,localDict)

    def annotate_import(self,expr,line,scope,globalDict,localDict):
        def parseImportee(importee,importeeLine):
            if isinstance(importee,S):
                return (importee,None,None)
            if not (isinstance(importee,list) and len(importee)==3):
                raise SyntaxError(importeeLine,
                                  "Imported item must be symbol, as-spec, or from-spec: %s" % str(importee))
            ((first,firstLine),(kw,_),(last,_))=importee
            if kw is S(":as"):
                return (first,last,None)
            if kw is S(":from"):
                def parseTarget(t):
                    (target,targetLine)=t
                    if not (isinstance(target,S)):
                        raise SyntaxError(targetLine,
                                          ("Item to import must be symbol, not %s"
                                           % str(target)))
                    return target
                if first is S('*'):
                    targets=first
                else:
                    if isinstance(first,list) and first:
                        targets=list(map(parseTarget,first))
                    else:
                        raise SyntaxError(firstLine,
                                          ("Spec of items to import from %s must be a non-empty list or *: %s"
                                           % (last,first)))
                return (last,None,targets)
            raise SyntaxError(importeeLine,
                              "Imported item must be symbol, as-spec, or from-spec: %s" % str(importee))

        extraRes=[]
        limitedNames=[]
        for (importee,importeeLine) in expr[1:]:
            (moduleName,asName,targets)=parseImportee(importee,importeeLine)
            for (name,command) in scope.addModule(moduleName,importeeLine,
                                                  asName,targets):
                if name:
                    limitedNames.append(name)
                extraRes.append(self(command,scope,globalDict,localDict))
        if (limitedNames
            and isinstance(expr[1][0],list)
            and (expr[1][0][0][0] is S('*'))
            ):
            expr=list(expr)
            expr[1]=(list(expr[1][0]),expr[1][1])
            starLine=expr[1][0][0][1]
            expr[1][0][0]=(list(map(lambda name: (name,starLine),
                                    limitedNames)),
                           starLine)
        res=self.quoteOrImport(expr,line,scope,False,
                               globalDict,localDict)
        if extraRes:
            return (([(S('begin'),line,Scope.root),res]
                     +extraRes),line,scope)
        else:
            return res

    def quoteOrImport(self,expr,line,scope,justOneArg,globalDict,localDict):
        def annotateDumbly(parsedExpr):
            try:
                (expr,line)=parsedExpr
            except ValueError as ve:
                print(ve,parsedExpr)
                raise
            if type(expr)==list:
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
        if not type(arg)==list:
            expr=[(S('quote'),expr[0][1]),expr[1]]
            return self.annotate_quote(expr,line,scope,
                                       globalDict,localDict)
        sublists=[]
        curSublist=[]
        curSublistFirstLine=None

        for (a,aLine) in arg:
            if type(a)==list and a and a[0] and a[0][0] is S(',@'):
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
            if (type(a)==int
                or type(a)==str
                or type(a)==float
                or type(a)==bool):
                curItem=(a,aLine,scope)
            else:
                if type(a)==list and not a:
                    curItem=([(S('mk-list'),aLine,scope.root)],aLine,scope)
                else:
                    if type(a)==list and a and a[0] and a[0][0] is S(','):
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
            assert type(expr)==S
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
        scope.addDef(namePE[0],None,namePE[1],redefPermitted=True)
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
        childScope=Scope(scope,isFuncScope=True)
        keyArgs=[]
        inKeys=False
        def doArg(arg):
            nonlocal keyArgs,inKeys
            (argExpr,argLine)=arg
            if type(argExpr)==list:
                (argExprPE,argDefaultPE)=argExpr
                argExpr=argExprPE[0]
            else:
                argDefaultPE=None
            if argExpr[0]=='&':
                inKeys=(argExpr is S('&key'))
                return (argExpr,argLine,scope)
            childScope.addDef(argExpr,argLine,None)
            if inKeys:
                keyArgs.append((argExpr,argLine))
                scopeToUse=None
            else:
                scopeToUse=childScope
            if argDefaultPE:
                return ([(argExpr,argLine,scopeToUse),
                         self(argDefaultPE,scope,globalDict,localDict)],
                        argLine,scope)
            else:
                return (argExpr,argLine,scopeToUse)

        def seekAssignments(scopedExpr):
            (expr,_,scope)=scopedExpr
            if not (type(expr)==list and expr):
                return
            fExpr=expr[0][0]
            if type(fExpr)==S:
                searchSpace=expr
                if fExpr is S(':='):
                    (lhs,lhsLine,lhsScope)=expr[1]
                    if type(lhs)==S:
                        yield (lhs,lhsScope)
                        searchSpace=[expr[2]]
                else:
                    if fExpr is S('lambda'):
                        searchSpace=expr[2:]
                    else:
                        if fExpr is S('defun'):
                            searchSpace=expr[3:]
                for e in searchSpace:
                    for assignment in seekAssignments(e):
                        yield assignment

        scoped=[self(opPE,scope,globalDict,localDict,asFunc=True)]

        if namePE:
            scope.addDef(namePE[0],None,namePE[1],redefPermitted=True)
            scoped.append((namePE[0],namePE[1],scope))
        (argsExpr,argsLine)=argsPE
        scopedArgs=[]
        for a in argsExpr:
            scopedArgs.append(doArg(a))

        bodyScoped=[]
        for (keyArg,keyLine) in keyArgs:
            bodyScoped.append(([(S(':='),keyLine,Scope.root),
                                (keyArg,keyLine,childScope),
                                (keyArg,keyLine,None)],
                               keyLine,childScope))


        nonlocalVars=set()
        globalVars=set()
        for parsedExpr in bodyPEs:
            bodyPart=self(parsedExpr,childScope,globalDict,localDict)
            bodyScoped.append(bodyPart)
            for (var,varScope) in seekAssignments(bodyPart):
                if not varScope.isDescendantOf(childScope):
                    (globalVars
                     if varScope.atGlobalScope()
                     else nonlocalVars).add((var,varScope))

        for (key,vs) in [('nonlocal',nonlocalVars),
                         ('global',globalVars)]:
            if vs:
                scopedArgs.append((S('&'+key),argsLine,Scope.root))
            for (v,vScope) in vs:
                scopedArgs.append((v,argsLine,vScope))
        scoped.append((scopedArgs,argsLine,scope))
        scoped+=bodyScoped
        return (scoped,line,scope)

    def annotate_scope(self,expr,line,scope,globalDict,localDict):
        childScope=Scope(scope)
        return (([(S('begin'),expr[0][1],Scope.root)]
                 +list(map(lambda e: self(e,childScope,globalDict,localDict),
                           expr[1:]))
                 ),
                line,scope)

    def annotate_extern(self,expr,line,scope,globalDict,localDict):
        assert len(expr)==2
        (var,varLine)=expr[1]
        assert isinstance(var,S)
        scope.addDef(var,None,varLine)
        return self(expr[1],scope,globalDict,localDict)

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
    if (scope is None) and type(expr)==S:
        return expr
    if (not quoted
        and type(expr)==S
        and not expr.isKeyword()):
        if expr is S('&rest') or expr is S('&key') or expr is S('&optional'):
            return expr
        if (scope.parent
            and not scope.get(expr,skipClassScopes=False).ignoreScopeId):
            return S('%s-%d' % (str(expr),scope.id))
    if not (type(expr)==list and expr):
        return expr
    if not quoted and (expr[0][0] is S('quote')
                       or expr[0][0] is S('import')):
        return ([expr[0][0]]
                +list(map(lambda e: stripAnnotations(e,quoted=True),expr[1:]))
                )
    if not quoted and expr[0][0] is S('.'):
        return ([expr[0][0],
                 stripAnnotations(expr[1])]
                 +list(map(lambda e: stripAnnotations(e,quoted=True),
                           expr[2:]))
                )
    return list(map(lambda e: stripAnnotations(e,quoted=quoted),expr))

def addLines(expr,defLine):
    if literable(expr) or type(expr)==S:
        return (expr,defLine)
    #assert type(expr)==list
    return (list(map(lambda e: addLines(e,defLine),expr)),defLine)

def stripLines(parsedExpr):
    (expr,line)=parsedExpr
    if literable(expr) or type(expr)==S:
        return expr
    #assert type(expr)==list
    return list(map(stripLines,expr))

def compileAndEval(expr,scope,globalDict,localDict,*,
                   hasLines=False,defLine=0,
                   verbose=False,
                   printCompilationExn=True,
                   cacheOutputFile=None):
    if scope is None:
        scope=Scope(None)
    if globalDict is None:
        globalDict=adder.gomer.mkGlobals()
    if localDict is None:
        localDict=globalDict

    if not hasLines:
        expr=addLines(expr,defLine)
    try:
        annotated=annotate(expr,scope,globalDict,localDict)
        gomer=stripAnnotations(annotated)
    except Exception as e:
        if printCompilationExn:
            print('Compilation exception in',expr)
        raise
    return adder.gomer.geval(gomer,
                             globalDict=globalDict,
                             localDict=localDict,
                             verbose=verbose,
                             cacheOutputFile=cacheOutputFile)

def tagWithIsLast(g):
    prev=None
    prevValid=False
    for x in g:
        if prevValid:
            yield (prev,False)
        prev=x
        prevValid=True
    if prevValid:
        yield (prev,True)

def loadFile(f,scope,globalDict,*,
             inSrcDir=False,
             cacheOutputFile=None,
             cache=False):
    if scope is None:
        scope=Scope(None)
    if globalDict is None:
        globalDict=adder.gomer.mkGlobals()
    res=None

    if cache and (cacheOutputFile is None) and f.endswith('.+'):
        cacheOutputFileName=f[:-2]+'.py'
        if (os.path.exists(cacheOutputFileName)
            and adder.util.isNewer(cacheOutputFileName,f)):
            code=open(cacheOutputFileName,'r').read()
            exec(code,globalDict)
            return (globalDict.get(S('__adder__last__').toPython(),None),
                    globalDict)
        else:
            cacheOutputFile=open(cacheOutputFileName,'w')

    if inSrcDir:
        srcFile=loadFile.__code__.co_filename
        srcDir=os.path.split(srcFile)[0]
        f=os.path.join(srcDir,f)

    for (parsedExpr,isLast) in tagWithIsLast(adder.parser.parseFile(f)):
        if isLast and cacheOutputFile:
            line=parsedExpr[1]
            parsedExpr=([(S(':='),line),
                         (S('__adder__last__'),line),
                         parsedExpr],line)
        res=compileAndEval(parsedExpr,scope,
                           globalDict,None,
                           hasLines=True,
                           cacheOutputFile=cacheOutputFile)
    return (res,globalDict)

class Context:
    def __init__(self,*,loadPrelude=True,
                 cacheOutputFileName=None):
        self.cacheOutputFileName=cacheOutputFileName
        self.scope=Scope(None,trackDescendants=True,context=self)
        self.globals=adder.gomer.mkGlobals()
        if self.cacheOutputFileName:
            self.cacheOutputFile=open(self.cacheOutputFileName,'w')
            self.cacheOutputFile.write("""import adder.gomer, adder.compiler
from adder.runtime import *
python=adder.gomer.mkPython()

""")
            self.cacheBodyStream=io.StringIO()
        else:
            self.cacheBodyStream=None
            self.cacheOutputFile=None
        if loadPrelude:
            self.load('prelude.+',inSrcDir=True)

    def load(self,f,*,inSrcDir=False,cache=False):
        loadFile(f,self.scope,self.globals,
                 inSrcDir=inSrcDir,
                 cacheOutputFile=self.cacheBodyStream,
                 cache=cache)

    def eval(self,expr,*,verbose=False,hasLines=False,defLine=0,
             printCompilationExn=True):
        if self.cacheBodyStream:
            self.cacheBodyStream.writelines(['\n']
                                            +list(map(lambda l: '#'+l+'\n',
                                                      adder.common.adderStr(expr).split('\n')
                                                     )
                                                 )
                                            +['\n']
                                            )
        return compileAndEval(expr,
                              self.scope,self.globals,
                              None,
                              hasLines=hasLines,defLine=defLine,
                              verbose=verbose,
                              printCompilationExn=printCompilationExn,
                              cacheOutputFile=self.cacheBodyStream)

    def define(self,name,value):
        self.scope.addDef(S(name),value,0,redefPermitted=True)
        self.globals[S("%s-%d" % (name,self.scope.id)).toPython()]=value

    def close(self):
        if self.cacheOutputFile:
            self.cacheOutputFile.write('\n\n')
            self.scope.dump(self.cacheOutputFile)
            self.cacheOutputFile.write('\n\n')

            self.cacheBodyStream.seek(0)
            self.cacheOutputFile.write(self.cacheBodyStream.read())

            self.cacheOutputFile.write('\n\n')
            for varName in self.scope.iterDontAscend():
                if varName not in Scope.root:
                    entry=self.scope[varName]
                    if not (entry.macroExpander
                            or entry.isBuiltinFunc):
                        scopedVarName=S('%s-%d' % (str(varName),
                                                  self.scope.id))
                        pyVarName=scopedVarName.toPython()
                        self.cacheOutputFile.write('%s=%s\n'
                                                   % (varName.toPython(),
                                                      pyVarName))
                        # TODO: is this necessary? If it's legal
                        # Python, then varName.toPython() is just
                        # varName, right?
                        if varName.isLegalPython():
                            self.cacheOutputFile.write('%s=%s\n'
                                                       % (varName,
                                                          pyVarName))

            self.cacheOutputFile.flush()

import adder.gomer, adder.compiler
from adder.runtime import *
python=adder.gomer.mkPython()



__adder__module_scope_1596213198__=adder.compiler.Scope.expand({'isFuncScope': False, 'parent': adder.compiler.Scope.root, 'isClassScope': False, 'readOnly': False, 'entries': {adder.common.Symbol('len-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<ul>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-define-fontstyle-elements #1591>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('if-bind'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-if-bind #1173>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('gensym-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('eval-py'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('zip'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('symbol?-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<thead>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<tt>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<s>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-let #108>'): {'macroExpander': None, 'line': 84, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('set?'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<font>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('type-set-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<hr>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('stdout'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('str'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('set?-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<big>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<h6>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('next'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<label>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<optgroup>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<frame>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('type-tuple-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<img>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<em>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<form>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('type-dict'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<table>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('stdin'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('dict?-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<i>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<h3>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('sys'): {'macroExpander': None, 'line': 38, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('tuple?-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<q>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('expand-attr-groups'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('os'): {'macroExpander': None, 'line': 2, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<col>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-if-bind #1173>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<samp>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<th>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<script>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<h2>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<tfoot>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<meta>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('type-set'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<object>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('type-generator-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<code>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('tail'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('file-to-load'): {'macroExpander': None, 'line': 25, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-for #1106>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<samp>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<frameset>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('intern-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<dt>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('str?-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-define-phrase-elements #1579>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<select>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-let #885>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('define-element'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-define-element #1453>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<sub>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-dp #798>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-dp #798>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<b>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('@'): {'macroExpander': None, 'line': 43, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('type-list'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<base>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('len'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-case #183>'): {'macroExpander': None, 'line': 118, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<area>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-with-macro-vars #915>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-define-phrase-elements #1579>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-unless #270>'): {'macroExpander': None, 'line': 152, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('..'): {'macroExpander': adder.common.Symbol('#<gensym-macro-dot-dot #63>'), 'line': 57, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('ecase'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-ecase #1018>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<basefont>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-cond #46>'): {'macroExpander': None, 'line': 44, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<q>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('define-phrase-elements'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-define-phrase-elements #1579>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<html>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<legend>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<fieldset>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<body>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<ol>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<acronym>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-delay #1057>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<h1>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<pre>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('unless'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-unless #1047>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-if-bind #1173>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<option>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('type-symbol-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<sub>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-if-bind #396>'): {'macroExpander': None, 'line': 178, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<legend>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('type-str'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<li>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<style>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<div>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<ol>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-dp #21>'): {'macroExpander': None, 'line': 22, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<dir>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<a>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-unless #1047>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<menu>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<fieldset>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('head'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<var>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<script>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<strike>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<h3>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('reverse!-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('cgi-fields'): {'macroExpander': None, 'line': 4, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<h2>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('head-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('gensym'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('iter'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('list?-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<address>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<select>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<tr>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('cons-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('field'): {'macroExpander': None, 'line': 6, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-when-bind #1199>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<font>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<dt>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-dot-dot #63>'): {'macroExpander': None, 'line': 57, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<ins>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('error-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<center>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('stderr'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<head>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<colgroup>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-foreach #1568>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('lookup-attr-group'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-case #960>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('with-macro-vars'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-with-macro-vars #915>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('yield*'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-yield* #1225>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('int?'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-when #262>'): {'macroExpander': None, 'line': 148, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('symbol?'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('field-names'): {'macroExpander': None, 'line': 22, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<td>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('type-str-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-define #151>'): {'macroExpander': None, 'line': 108, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<a>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<h1>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('force'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<strong>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('take'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<thead>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<style>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<optgroup>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-define-fontstyle-elements #1591>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<h5>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<dl>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<acronym>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<kbd>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('write'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('delay'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-delay #1057>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<noframes>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-case #960>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<small>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('map-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('foreach'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-foreach #1568>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<tbody>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<iframe>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<abbr>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<map>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<isindex>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-ecase #1018>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<u>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-ecase #1018>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<small>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('lookup-attr-group-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('stdout-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<dd>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('stdin-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<span>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<strong>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<dfn>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-when-bind #422>'): {'macroExpander': None, 'line': 186, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('map'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-with-macro-vars #138>'): {'macroExpander': None, 'line': 104, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<body>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<p>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<i>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('when-bind'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-when-bind #1199>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<textarea>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-ecase #241>'): {'macroExpander': None, 'line': 137, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<map>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<h6>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<tt>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('page-env'): {'macroExpander': None, 'line': 40, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('dict?'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-define-element #1453>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<h5>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<dfn>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('define'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-define #928>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('generator?-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<big>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-let #885>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<th>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('int?-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('str?'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<br>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<link>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<param>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('let*'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-let* #867>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<li>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<h4>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<basefont>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<dl>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('list?'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-foreach #1568>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-yield* #1225>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('take-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<img>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<ins>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<dir>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<u>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-define-element #1453>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<title>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<tr>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<span>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<link>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<cite>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('define-fontstyle-elements'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-define-fontstyle-elements #1591>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<strike>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<h4>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('reverse!'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<area>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<table>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('tuple?'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('force-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-dot-dot #840>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('type-dict-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-when-bind #1199>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<sup>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<kbd>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('tag-to-sym'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('expand-attr-groups-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('case'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-case #960>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<caption>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('when'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-when #1039>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-delay #1057>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-let* #867>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<del>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<sup>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-for #329>'): {'macroExpander': None, 'line': 168, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('iter-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('let'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-let #885>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<cite>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-let* #90>'): {'macroExpander': None, 'line': 70, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<em>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('tail-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<noscript>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<code>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('intern'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('next-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<s>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('type-int'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-yield* #1225>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<meta>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<ul>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<td>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<br>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('error'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<base>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<blockquote>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-cond #823>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('write-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<bdo>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('tag-to-sym-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('type-symbol'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-delay #280>'): {'macroExpander': None, 'line': 156, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<center>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<tbody>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('type-int-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<pre>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('for'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-for #1106>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<p>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('dp'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-dp #798>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('cons'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-yield* #448>'): {'macroExpander': None, 'line': 193, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-when #1039>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-define #928>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<html>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<bdo>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<b>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<isindex>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<address>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<head>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<title>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<blockquote>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-define #928>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<textarea>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<hr>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('fields'): {'macroExpander': None, 'line': 14, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('type-list-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-when #1039>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('cond'): {'macroExpander': adder.common.Symbol('htmlout.#<gensym-macro-cond #823>-1975524393'), 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<applet>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-unless #1047>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('type-generator'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<option>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-for #1106>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<caption>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('eval-py-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<button>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<dd>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('cgi'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<var>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('generator?'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<colgroup>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-with-macro-vars #915>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<frameset>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<div>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<input>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<col>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<form>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<button>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-dot-dot #840>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('type-tuple'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<applet>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('stderr-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('str-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<abbr>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('O'): {'macroExpander': None, 'line': 42, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<menu>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-let* #867>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('zip-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<noscript>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<object>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<del>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<noframes>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<tfoot>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<frame>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<iframe>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<param>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('#<gensym-macro-cond #823>'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': True, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<label>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}, adder.common.Symbol('<input>-1596213198'): {'macroExpander': None, 'line': 1, 'ignoreScopeId': False, 'asConst': False, 'initExpr': None}}, 'id': 1596213198})
__adder__module_scope__=__adder__module_scope_1596213198__


_adder_eval_002dpy_002d1596213198=python.eval
_adder__0023_003cgensym_002dres_0020_00231_003e=_adder_eval_002dpy_002d1596213198
_adder_map_002d1596213198=python.map
_adder__0023_003cgensym_002dres_0020_00232_003e=_adder_map_002d1596213198
_adder_zip_002d1596213198=python.zip
_adder__0023_003cgensym_002dres_0020_00233_003e=_adder_zip_002d1596213198
_adder_next_002d1596213198=python.next
_adder__0023_003cgensym_002dres_0020_00234_003e=_adder_next_002d1596213198
_adder_iter_002d1596213198=python.iter
_adder__0023_003cgensym_002dres_0020_00235_003e=_adder_iter_002d1596213198
_adder_len_002d1596213198=python.len
_adder__0023_003cgensym_002dres_0020_00236_003e=_adder_len_002d1596213198
_adder_str_002d1596213198=python.str
_adder__0023_003cgensym_002dres_0020_00237_003e=_adder_str_002d1596213198
_adder_stdin_002d1596213198=python.sys.stdin
_adder__0023_003cgensym_002dres_0020_00238_003e=_adder_stdin_002d1596213198
_adder_stdout_002d1596213198=python.sys.stdout
_adder__0023_003cgensym_002dres_0020_00239_003e=_adder_stdout_002d1596213198
_adder_stderr_002d1596213198=python.sys.stderr
_adder__0023_003cgensym_002dres_0020_002310_003e=_adder_stderr_002d1596213198
_adder_type_002dlist_002d1596213198=python.list
_adder__0023_003cgensym_002dres_0020_002311_003e=_adder_type_002dlist_002d1596213198
_adder_type_002dtuple_002d1596213198=python.tuple
_adder__0023_003cgensym_002dres_0020_002312_003e=_adder_type_002dtuple_002d1596213198
_adder_type_002dset_002d1596213198=python.set
_adder__0023_003cgensym_002dres_0020_002313_003e=_adder_type_002dset_002d1596213198
_adder_type_002ddict_002d1596213198=python.dict
_adder__0023_003cgensym_002dres_0020_002314_003e=_adder_type_002ddict_002d1596213198
_adder_type_002dsymbol_002d1596213198=adder.common.Symbol
_adder__0023_003cgensym_002dres_0020_002315_003e=_adder_type_002dsymbol_002d1596213198
_adder_type_002dint_002d1596213198=python.int
_adder__0023_003cgensym_002dres_0020_002316_003e=_adder_type_002dint_002d1596213198
_adder_type_002dstr_002d1596213198=python.str
_adder__0023_003cgensym_002dres_0020_002317_003e=_adder_type_002dstr_002d1596213198
_adder_type_002dgenerator_002d1596213198=python.types.GeneratorType
_adder__0023_003cgensym_002dres_0020_002318_003e=_adder_type_002dgenerator_002d1596213198
_adder_gensym_002d1596213198=adder.common.gensym
_adder__0023_003cgensym_002dres_0020_002319_003e=_adder_gensym_002d1596213198
_adder_intern_002d1596213198=adder.common.Symbol
_adder__0023_003cgensym_002dres_0020_002320_003e=_adder_intern_002d1596213198
def _adder__0023_003cgensym_002dmacro_002ddp_0020_002321_003e_002d1596213198(_adder_expr_002d1599460773):
    _adder_scratch_002d1599460773=_adder_gensym_002d1596213198()
    _adder__0023_003cgensym_002dscratch_0020_002322_003e=adder.common.Symbol('scope')
    _adder__0023_003cgensym_002dscratch_0020_002323_003e=adder.common.Symbol('defvar')
    _adder__0023_003cgensym_002dscratch_0020_002324_003e=[_adder__0023_003cgensym_002dscratch_0020_002323_003e, _adder_scratch_002d1599460773, _adder_expr_002d1599460773]
    _adder__0023_003cgensym_002dscratch_0020_002325_003e=adder.common.Symbol('print')
    _adder__0023_003cgensym_002dscratch_0020_002326_003e=adder.common.Symbol('quote')
    _adder__0023_003cgensym_002dscratch_0020_002327_003e=[_adder__0023_003cgensym_002dscratch_0020_002326_003e, _adder_expr_002d1599460773]
    _adder__0023_003cgensym_002dscratch_0020_002328_003e=adder.common.Symbol('.')
    _adder__0023_003cgensym_002dscratch_0020_002329_003e=adder.common.Symbol('adder')
    _adder__0023_003cgensym_002dscratch_0020_002330_003e=adder.common.Symbol('common')
    _adder__0023_003cgensym_002dscratch_0020_002331_003e=adder.common.Symbol('adderStr')
    _adder__0023_003cgensym_002dscratch_0020_002332_003e=[_adder__0023_003cgensym_002dscratch_0020_002328_003e, _adder__0023_003cgensym_002dscratch_0020_002329_003e, _adder__0023_003cgensym_002dscratch_0020_002330_003e, _adder__0023_003cgensym_002dscratch_0020_002331_003e]
    _adder__0023_003cgensym_002dscratch_0020_002333_003e=[_adder__0023_003cgensym_002dscratch_0020_002332_003e, _adder_scratch_002d1599460773]
    _adder__0023_003cgensym_002dscratch_0020_002334_003e=[_adder__0023_003cgensym_002dscratch_0020_002325_003e, _adder__0023_003cgensym_002dscratch_0020_002327_003e, ':', _adder__0023_003cgensym_002dscratch_0020_002333_003e]
    _adder__0023_003cgensym_002dscratch_0020_002335_003e=[_adder__0023_003cgensym_002dscratch_0020_002322_003e, _adder__0023_003cgensym_002dscratch_0020_002324_003e, _adder__0023_003cgensym_002dscratch_0020_002334_003e, _adder_scratch_002d1599460773]
    return _adder__0023_003cgensym_002dscratch_0020_002335_003e
_adder__0023_003cgensym_002dres_0020_002336_003e=_adder__0023_003cgensym_002dmacro_002ddp_0020_002321_003e_002d1596213198
def _adder_head_002d1596213198(_adder_l_002d1598378248):
    _adder__0023_003cgensym_002dscratch_0020_002337_003e=_adder_l_002d1598378248[0]
    return _adder__0023_003cgensym_002dscratch_0020_002337_003e
_adder__0023_003cgensym_002dres_0020_002338_003e=_adder_head_002d1596213198
def _adder_tail_002d1596213198(_adder_l_002d1592965623):
    _adder__0023_003cgensym_002dscratch_0020_002339_003e=_adder_l_002d1592965623[1:]
    return _adder__0023_003cgensym_002dscratch_0020_002339_003e
_adder__0023_003cgensym_002dres_0020_002340_003e=_adder_tail_002d1596213198
def _adder_reverse_0021_002d1596213198(_adder_l_002d1591883098):
    _adder__0023_003cgensym_002dscratch_0020_002341_003e=_adder_l_002d1591883098.reverse
    _adder__0023_003cgensym_002dscratch_0020_002341_003e()
    return _adder_l_002d1591883098
_adder__0023_003cgensym_002dres_0020_002342_003e=_adder_reverse_0021_002d1596213198
def _adder_cons_002d1596213198(_adder_h_002d1595130673,_adder_t_002d1595130673):
    _adder__0023_003cgensym_002dscratch_0020_002343_003e=[_adder_h_002d1595130673]
    _adder__0023_003cgensym_002dscratch_0020_002344_003e=_adder__0023_003cgensym_002dscratch_0020_002343_003e+_adder_t_002d1595130673
    return _adder__0023_003cgensym_002dscratch_0020_002344_003e
_adder__0023_003cgensym_002dres_0020_002345_003e=_adder_cons_002d1596213198
def _adder__0023_003cgensym_002dmacro_002dcond_0020_002346_003e_002d1596213198(*_adder_cases_002d1594048148):
    def _adder_mk_002d1594048148(_adder_cs_002d1588635523):
        _adder__0023_003cgensym_002dscratch_0020_002347_003e=not(_adder_cs_002d1588635523)
        if _adder__0023_003cgensym_002dscratch_0020_002347_003e:
            _adder__0023_003cgensym_002dif_0020_002348_003e=None
        else:
            _adder__0023_003cgensym_002dscratch_0020_002349_003e=adder.common.Symbol('if')
            _adder__0023_003cgensym_002dscratch_0020_002350_003e=_adder_head_002d1596213198(_adder_cs_002d1588635523)
            _adder__0023_003cgensym_002dscratch_0020_002351_003e=_adder_head_002d1596213198(_adder__0023_003cgensym_002dscratch_0020_002350_003e)
            _adder__0023_003cgensym_002dscratch_0020_002352_003e=adder.common.Symbol('begin')
            _adder__0023_003cgensym_002dscratch_0020_002353_003e=[_adder__0023_003cgensym_002dscratch_0020_002352_003e]
            _adder__0023_003cgensym_002dscratch_0020_002354_003e=_adder_head_002d1596213198(_adder_cs_002d1588635523)
            _adder__0023_003cgensym_002dscratch_0020_002355_003e=_adder_tail_002d1596213198(_adder__0023_003cgensym_002dscratch_0020_002354_003e)
            _adder__0023_003cgensym_002dscratch_0020_002356_003e=list(_adder__0023_003cgensym_002dscratch_0020_002355_003e)
            _adder__0023_003cgensym_002dscratch_0020_002357_003e=_adder__0023_003cgensym_002dscratch_0020_002353_003e+_adder__0023_003cgensym_002dscratch_0020_002356_003e
            _adder__0023_003cgensym_002dscratch_0020_002358_003e=_adder_tail_002d1596213198(_adder_cs_002d1588635523)
            _adder__0023_003cgensym_002dscratch_0020_002359_003e=_adder_mk_002d1594048148(_adder__0023_003cgensym_002dscratch_0020_002358_003e)
            _adder__0023_003cgensym_002dscratch_0020_002360_003e=[_adder__0023_003cgensym_002dscratch_0020_002349_003e, _adder__0023_003cgensym_002dscratch_0020_002351_003e, _adder__0023_003cgensym_002dscratch_0020_002357_003e, _adder__0023_003cgensym_002dscratch_0020_002359_003e]
            _adder__0023_003cgensym_002dif_0020_002348_003e=_adder__0023_003cgensym_002dscratch_0020_002360_003e
        return _adder__0023_003cgensym_002dif_0020_002348_003e
    _adder__0023_003cgensym_002dscratch_0020_002361_003e=_adder_mk_002d1594048148(_adder_cases_002d1594048148)
    return _adder__0023_003cgensym_002dscratch_0020_002361_003e
_adder__0023_003cgensym_002dres_0020_002362_003e=_adder__0023_003cgensym_002dmacro_002dcond_0020_002346_003e_002d1596213198
def _adder__0023_003cgensym_002dmacro_002ddot_002ddot_0020_002363_003e_002d1596213198(*_adder_parts_002d1587552998):
    _adder__0023_003cgensym_002dscratch_0020_002364_003e=adder.common.Symbol('lambda')
    _adder__0023_003cgensym_002dscratch_0020_002365_003e=adder.common.Symbol('obj')
    _adder__0023_003cgensym_002dscratch_0020_002366_003e=[_adder__0023_003cgensym_002dscratch_0020_002365_003e]
    _adder__0023_003cgensym_002dscratch_0020_002367_003e=adder.common.Symbol('.')
    _adder__0023_003cgensym_002dscratch_0020_002368_003e=adder.common.Symbol('obj')
    _adder__0023_003cgensym_002dscratch_0020_002369_003e=[_adder__0023_003cgensym_002dscratch_0020_002367_003e, _adder__0023_003cgensym_002dscratch_0020_002368_003e]
    _adder__0023_003cgensym_002dscratch_0020_002370_003e=list(_adder_parts_002d1587552998)
    _adder__0023_003cgensym_002dscratch_0020_002371_003e=_adder__0023_003cgensym_002dscratch_0020_002369_003e+_adder__0023_003cgensym_002dscratch_0020_002370_003e
    _adder__0023_003cgensym_002dscratch_0020_002372_003e=[_adder__0023_003cgensym_002dscratch_0020_002364_003e, _adder__0023_003cgensym_002dscratch_0020_002366_003e, _adder__0023_003cgensym_002dscratch_0020_002371_003e]
    return _adder__0023_003cgensym_002dscratch_0020_002372_003e
_adder__0023_003cgensym_002dres_0020_002373_003e=_adder__0023_003cgensym_002dmacro_002ddot_002ddot_0020_002363_003e_002d1596213198
def _adder_list_003f_002d1596213198(_adder_x_002d1590800573):
    _adder__0023_003cgensym_002dscratch_0020_002374_003e=python.isinstance(_adder_x_002d1590800573,_adder_type_002dlist_002d1596213198)
    return _adder__0023_003cgensym_002dscratch_0020_002374_003e
_adder__0023_003cgensym_002dres_0020_002375_003e=_adder_list_003f_002d1596213198
def _adder_tuple_003f_002d1596213198(_adder_x_002d1589718048):
    _adder__0023_003cgensym_002dscratch_0020_002376_003e=python.isinstance(_adder_x_002d1589718048,_adder_type_002dtuple_002d1596213198)
    return _adder__0023_003cgensym_002dscratch_0020_002376_003e
_adder__0023_003cgensym_002dres_0020_002377_003e=_adder_tuple_003f_002d1596213198
def _adder_set_003f_002d1596213198(_adder_x_002d1584305423):
    _adder__0023_003cgensym_002dscratch_0020_002378_003e=python.isinstance(_adder_x_002d1584305423,_adder_type_002dset_002d1596213198)
    return _adder__0023_003cgensym_002dscratch_0020_002378_003e
_adder__0023_003cgensym_002dres_0020_002379_003e=_adder_set_003f_002d1596213198
def _adder_dict_003f_002d1596213198(_adder_x_002d1583222898):
    _adder__0023_003cgensym_002dscratch_0020_002380_003e=python.isinstance(_adder_x_002d1583222898,_adder_type_002ddict_002d1596213198)
    return _adder__0023_003cgensym_002dscratch_0020_002380_003e
_adder__0023_003cgensym_002dres_0020_002381_003e=_adder_dict_003f_002d1596213198
def _adder_symbol_003f_002d1596213198(_adder_x_002d1586470473):
    _adder__0023_003cgensym_002dscratch_0020_002382_003e=python.isinstance(_adder_x_002d1586470473,_adder_type_002dsymbol_002d1596213198)
    return _adder__0023_003cgensym_002dscratch_0020_002382_003e
_adder__0023_003cgensym_002dres_0020_002383_003e=_adder_symbol_003f_002d1596213198
def _adder_int_003f_002d1596213198(_adder_x_002d1585387948):
    _adder__0023_003cgensym_002dscratch_0020_002384_003e=python.isinstance(_adder_x_002d1585387948,_adder_type_002dint_002d1596213198)
    return _adder__0023_003cgensym_002dscratch_0020_002384_003e
_adder__0023_003cgensym_002dres_0020_002385_003e=_adder_int_003f_002d1596213198
def _adder_str_003f_002d1596213198(_adder_x_002d1579975323):
    _adder__0023_003cgensym_002dscratch_0020_002386_003e=python.isinstance(_adder_x_002d1579975323,_adder_type_002dstr_002d1596213198)
    return _adder__0023_003cgensym_002dscratch_0020_002386_003e
_adder__0023_003cgensym_002dres_0020_002387_003e=_adder_str_003f_002d1596213198
def _adder_generator_003f_002d1596213198(_adder_x_002d1578892798):
    _adder__0023_003cgensym_002dscratch_0020_002388_003e=python.isinstance(_adder_x_002d1578892798,_adder_type_002dgenerator_002d1596213198)
    return _adder__0023_003cgensym_002dscratch_0020_002388_003e
_adder__0023_003cgensym_002dres_0020_002389_003e=_adder_generator_003f_002d1596213198
def _adder__0023_003cgensym_002dmacro_002dlet_002a_0020_002390_003e_002d1596213198(_adder_decls_002d1582140373,*_adder_body_002d1582140373):
    _adder__0023_003cgensym_002dscratch_0020_002391_003e=adder.common.Symbol('scope')
    _adder__0023_003cgensym_002dscratch_0020_002392_003e=[_adder__0023_003cgensym_002dscratch_0020_002391_003e]
    def _adder__0023_003cgensym_002dlambda_0020_002393_003e(_adder_def_002d1581057848):
        _adder__0023_003cgensym_002dscratch_0020_002394_003e=_adder_list_003f_002d1596213198(_adder_def_002d1581057848)
        if _adder__0023_003cgensym_002dscratch_0020_002394_003e:
            _adder__0023_003cgensym_002dscratch_0020_002395_003e=adder.common.Symbol('defvar')
            _adder__0023_003cgensym_002dscratch_0020_002396_003e=_adder_def_002d1581057848[0]
            _adder__0023_003cgensym_002dscratch_0020_002397_003e=_adder_def_002d1581057848[1]
            _adder__0023_003cgensym_002dscratch_0020_002398_003e=[_adder__0023_003cgensym_002dscratch_0020_002395_003e, _adder__0023_003cgensym_002dscratch_0020_002396_003e, _adder__0023_003cgensym_002dscratch_0020_002397_003e]
            _adder__0023_003cgensym_002dif_0020_002399_003e=_adder__0023_003cgensym_002dscratch_0020_002398_003e
        else:
            _adder__0023_003cgensym_002dscratch_0020_0023100_003e=adder.common.Symbol('defvar')
            _adder__0023_003cgensym_002dscratch_0020_0023101_003e=[_adder__0023_003cgensym_002dscratch_0020_0023100_003e, _adder_def_002d1581057848]
            _adder__0023_003cgensym_002dif_0020_002399_003e=_adder__0023_003cgensym_002dscratch_0020_0023101_003e
        return _adder__0023_003cgensym_002dif_0020_002399_003e
    _adder__0023_003cgensym_002dscratch_0020_0023102_003e=_adder_map_002d1596213198(_adder__0023_003cgensym_002dlambda_0020_002393_003e,_adder_decls_002d1582140373)
    _adder__0023_003cgensym_002dscratch_0020_0023103_003e=list(_adder__0023_003cgensym_002dscratch_0020_0023102_003e)
    _adder__0023_003cgensym_002dscratch_0020_0023104_003e=list(_adder_body_002d1582140373)
    _adder__0023_003cgensym_002dscratch_0020_0023105_003e=_adder__0023_003cgensym_002dscratch_0020_0023103_003e+_adder__0023_003cgensym_002dscratch_0020_0023104_003e
    _adder__0023_003cgensym_002dscratch_0020_0023106_003e=_adder__0023_003cgensym_002dscratch_0020_002392_003e+_adder__0023_003cgensym_002dscratch_0020_0023105_003e
    return _adder__0023_003cgensym_002dscratch_0020_0023106_003e
_adder__0023_003cgensym_002dres_0020_0023107_003e=_adder__0023_003cgensym_002dmacro_002dlet_002a_0020_002390_003e_002d1596213198
def _adder__0023_003cgensym_002dmacro_002dlet_0020_0023108_003e_002d1596213198(_adder_decls_002d1575645223,*_adder_body_002d1575645223):
    def _adder__0023_003cgensym_002dlambda_0020_0023109_003e(_adder_def_002d1574562698):
        _adder__0023_003cgensym_002dscratch_0020_0023110_003e=_adder_list_003f_002d1596213198(_adder_def_002d1574562698)
        if _adder__0023_003cgensym_002dscratch_0020_0023110_003e:
            _adder__0023_003cgensym_002dscratch_0020_0023111_003e=_adder_head_002d1596213198(_adder_def_002d1574562698)
            _adder__0023_003cgensym_002dif_0020_0023112_003e=_adder__0023_003cgensym_002dscratch_0020_0023111_003e
        else:
            _adder__0023_003cgensym_002dif_0020_0023112_003e=_adder_def_002d1574562698
        return _adder__0023_003cgensym_002dif_0020_0023112_003e
    _adder__0023_003cgensym_002dscratch_0020_0023113_003e=_adder_map_002d1596213198(_adder__0023_003cgensym_002dlambda_0020_0023109_003e,_adder_decls_002d1575645223)
    _adder_vars_002d1575645223=list(_adder__0023_003cgensym_002dscratch_0020_0023113_003e)
    def _adder__0023_003cgensym_002dlambda_0020_0023114_003e(_adder_def_002d1577810273):
        _adder__0023_003cgensym_002dscratch_0020_0023115_003e=_adder_list_003f_002d1596213198(_adder_def_002d1577810273)
        if _adder__0023_003cgensym_002dscratch_0020_0023115_003e:
            _adder__0023_003cgensym_002dscratch_0020_0023116_003e=_adder_def_002d1577810273[1]
            _adder__0023_003cgensym_002dif_0020_0023117_003e=_adder__0023_003cgensym_002dscratch_0020_0023116_003e
        else:
            _adder__0023_003cgensym_002dif_0020_0023117_003e=None
        return _adder__0023_003cgensym_002dif_0020_0023117_003e
    _adder__0023_003cgensym_002dscratch_0020_0023118_003e=_adder_map_002d1596213198(_adder__0023_003cgensym_002dlambda_0020_0023114_003e,_adder_decls_002d1575645223)
    _adder_exprs_002d1575645223=list(_adder__0023_003cgensym_002dscratch_0020_0023118_003e)
    _adder__0023_003cgensym_002dscratch_0020_0023119_003e=_adder_map_002d1596213198(_adder_gensym_002d1596213198,_adder_vars_002d1575645223)
    _adder_scratches_002d1575645223=list(_adder__0023_003cgensym_002dscratch_0020_0023119_003e)
    def _adder__0023_003cgensym_002dlambda_0020_0023120_003e(*_adder_args_002d1576727748):
        _adder__0023_003cgensym_002dscratch_0020_0023121_003e=adder.common.Symbol('list')
        _adder__0023_003cgensym_002dscratch_0020_0023122_003e=adder_function_wrapper(_adder__0023_003cgensym_002dscratch_0020_0023121_003e,_adder_args_002d1576727748,1575645223)
        return _adder__0023_003cgensym_002dscratch_0020_0023122_003e
    _adder__0023_003cgensym_002dscratch_0020_0023123_003e=_adder_zip_002d1596213198(_adder_scratches_002d1575645223,_adder_exprs_002d1575645223)
    _adder__0023_003cgensym_002dscratch_0020_0023124_003e=_adder_map_002d1596213198(_adder__0023_003cgensym_002dlambda_0020_0023120_003e,_adder__0023_003cgensym_002dscratch_0020_0023123_003e)
    _adder_decl_002dscratches_002d1575645223=list(_adder__0023_003cgensym_002dscratch_0020_0023124_003e)
    def _adder__0023_003cgensym_002dlambda_0020_0023125_003e(*_adder_args_002d1571315123):
        _adder__0023_003cgensym_002dscratch_0020_0023126_003e=adder.common.Symbol('list')
        _adder__0023_003cgensym_002dscratch_0020_0023127_003e=adder_function_wrapper(_adder__0023_003cgensym_002dscratch_0020_0023126_003e,_adder_args_002d1571315123,1575645223)
        return _adder__0023_003cgensym_002dscratch_0020_0023127_003e
    _adder__0023_003cgensym_002dscratch_0020_0023128_003e=_adder_zip_002d1596213198(_adder_vars_002d1575645223,_adder_scratches_002d1575645223)
    _adder__0023_003cgensym_002dscratch_0020_0023129_003e=_adder_map_002d1596213198(_adder__0023_003cgensym_002dlambda_0020_0023125_003e,_adder__0023_003cgensym_002dscratch_0020_0023128_003e)
    _adder_decl_002dvars_002d1575645223=list(_adder__0023_003cgensym_002dscratch_0020_0023129_003e)
    _adder__0023_003cgensym_002dscratch_0020_0023130_003e=adder.common.Symbol('let*')
    _adder__0023_003cgensym_002dscratch_0020_0023131_003e=list(_adder_decl_002dscratches_002d1575645223)
    _adder__0023_003cgensym_002dscratch_0020_0023132_003e=list(_adder_decl_002dvars_002d1575645223)
    _adder__0023_003cgensym_002dscratch_0020_0023133_003e=_adder__0023_003cgensym_002dscratch_0020_0023131_003e+_adder__0023_003cgensym_002dscratch_0020_0023132_003e
    _adder__0023_003cgensym_002dscratch_0020_0023134_003e=[_adder__0023_003cgensym_002dscratch_0020_0023130_003e, _adder__0023_003cgensym_002dscratch_0020_0023133_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023135_003e=list(_adder_body_002d1575645223)
    _adder__0023_003cgensym_002dscratch_0020_0023136_003e=_adder__0023_003cgensym_002dscratch_0020_0023134_003e+_adder__0023_003cgensym_002dscratch_0020_0023135_003e
    return _adder__0023_003cgensym_002dscratch_0020_0023136_003e
_adder__0023_003cgensym_002dres_0020_0023137_003e=_adder__0023_003cgensym_002dmacro_002dlet_0020_0023108_003e_002d1596213198
def _adder__0023_003cgensym_002dmacro_002dwith_002dmacro_002dvars_0020_0023138_003e_002d1596213198(_adder_vars_002d1570232598,*_adder_body_002d1570232598):
    _adder__0023_003cgensym_002dscratch_0020_0023139_003e=adder.common.Symbol('let')
    def _adder__0023_003cgensym_002dlambda_0020_0023140_003e(_adder_v_002d1573480173):
        _adder__0023_003cgensym_002dscratch_0020_0023141_003e=adder.common.Symbol('quote')
        _adder__0023_003cgensym_002dscratch_0020_0023142_003e=_adder_gensym_002d1596213198(_adder_v_002d1573480173)
        _adder__0023_003cgensym_002dscratch_0020_0023143_003e=[_adder__0023_003cgensym_002dscratch_0020_0023141_003e, _adder__0023_003cgensym_002dscratch_0020_0023142_003e]
        _adder__0023_003cgensym_002dscratch_0020_0023144_003e=[_adder_v_002d1573480173, _adder__0023_003cgensym_002dscratch_0020_0023143_003e]
        return _adder__0023_003cgensym_002dscratch_0020_0023144_003e
    _adder__0023_003cgensym_002dscratch_0020_0023145_003e=_adder_map_002d1596213198(_adder__0023_003cgensym_002dlambda_0020_0023140_003e,_adder_vars_002d1570232598)
    _adder__0023_003cgensym_002dscratch_0020_0023146_003e=list(_adder__0023_003cgensym_002dscratch_0020_0023145_003e)
    _adder__0023_003cgensym_002dscratch_0020_0023147_003e=[_adder__0023_003cgensym_002dscratch_0020_0023139_003e, _adder__0023_003cgensym_002dscratch_0020_0023146_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023148_003e=list(_adder_body_002d1570232598)
    _adder__0023_003cgensym_002dscratch_0020_0023149_003e=_adder__0023_003cgensym_002dscratch_0020_0023147_003e+_adder__0023_003cgensym_002dscratch_0020_0023148_003e
    return _adder__0023_003cgensym_002dscratch_0020_0023149_003e
_adder__0023_003cgensym_002dres_0020_0023150_003e=_adder__0023_003cgensym_002dmacro_002dwith_002dmacro_002dvars_0020_0023138_003e_002d1596213198
def _adder__0023_003cgensym_002dmacro_002ddefine_0020_0023151_003e_002d1596213198(_adder_name_002dand_002dmaybe_002dargs_002d1572397648,*_adder_body_002dor_002dvalue_002d1572397648):
    _adder__0023_003cgensym_002dscratch_0020_0023170_003e=_adder_list_003f_002d1596213198(_adder_name_002dand_002dmaybe_002dargs_002d1572397648)
    if _adder__0023_003cgensym_002dscratch_0020_0023170_003e:
        _adder__0023_003cgensym_002dname_0020_0023156_003e_002d1631936523=_adder_head_002d1596213198(_adder_name_002dand_002dmaybe_002dargs_002d1572397648)
        _adder__0023_003cgensym_002dargs_0020_0023157_003e_002d1631936523=_adder_tail_002d1596213198(_adder_name_002dand_002dmaybe_002dargs_002d1572397648)
        _adder_name_002d1631936523=_adder__0023_003cgensym_002dname_0020_0023156_003e_002d1631936523
        _adder_args_002d1631936523=_adder__0023_003cgensym_002dargs_0020_0023157_003e_002d1631936523
        _adder__0023_003cgensym_002dscratch_0020_0023171_003e=adder.common.Symbol('defun')
        _adder__0023_003cgensym_002dscratch_0020_0023172_003e=[_adder__0023_003cgensym_002dscratch_0020_0023171_003e, _adder_name_002d1631936523, _adder_args_002d1631936523]
        _adder__0023_003cgensym_002dscratch_0020_0023173_003e=list(_adder_body_002dor_002dvalue_002d1572397648)
        _adder__0023_003cgensym_002dscratch_0020_0023174_003e=_adder__0023_003cgensym_002dscratch_0020_0023172_003e+_adder__0023_003cgensym_002dscratch_0020_0023173_003e
        _adder__0023_003cgensym_002dif_0020_0023175_003e=_adder__0023_003cgensym_002dscratch_0020_0023174_003e
    else:
        _adder__0023_003cgensym_002dscratch_0020_0023176_003e=adder.common.Symbol('defvar')
        _adder__0023_003cgensym_002dscratch_0020_0023177_003e=_adder_head_002d1596213198(_adder_body_002dor_002dvalue_002d1572397648)
        _adder__0023_003cgensym_002dscratch_0020_0023178_003e=[_adder__0023_003cgensym_002dscratch_0020_0023176_003e, _adder_name_002dand_002dmaybe_002dargs_002d1572397648, _adder__0023_003cgensym_002dscratch_0020_0023177_003e]
        _adder__0023_003cgensym_002dif_0020_0023175_003e=_adder__0023_003cgensym_002dscratch_0020_0023178_003e
    return _adder__0023_003cgensym_002dif_0020_0023175_003e
_adder__0023_003cgensym_002dres_0020_0023179_003e=_adder__0023_003cgensym_002dmacro_002ddefine_0020_0023151_003e_002d1596213198
def _adder_error_002d1596213198(_adder_msg_002d1630853998):
    _adder__0023_003cgensym_002dscratch_0020_0023180_003e=python.Exception
    _adder__0023_003cgensym_002dscratch_0020_0023181_003e=_adder__0023_003cgensym_002dscratch_0020_0023180_003e(_adder_msg_002d1630853998)
    raise _adder__0023_003cgensym_002dscratch_0020_0023181_003e
    return None
_adder__0023_003cgensym_002dres_0020_0023182_003e=_adder_error_002d1596213198
def _adder__0023_003cgensym_002dmacro_002dcase_0020_0023183_003e_002d1596213198(_adder_key_002d1634101573,*_adder_cases_002d1634101573):
    _adder__0023_003cgensym_002dvalue_0020_0023193_003e_002d1626523898=adder.common.Symbol('#<gensym-value #188>')
    _adder_value_002d1626523898=_adder__0023_003cgensym_002dvalue_0020_0023193_003e_002d1626523898
    _adder__0023_003cgensym_002dscratch_0020_0023215_003e=adder.common.Symbol('scope')
    _adder__0023_003cgensym_002dscratch_0020_0023216_003e=adder.common.Symbol('define')
    _adder__0023_003cgensym_002dscratch_0020_0023217_003e=[_adder__0023_003cgensym_002dscratch_0020_0023216_003e, _adder_value_002d1626523898, _adder_key_002d1634101573]
    _adder__0023_003cgensym_002dscratch_0020_0023218_003e=adder.common.Symbol('cond')
    _adder__0023_003cgensym_002dscratch_0020_0023219_003e=[_adder__0023_003cgensym_002dscratch_0020_0023218_003e]
    def _adder__0023_003cgensym_002dlambda_0020_0023220_003e(_adder_values_002dand_002dbody_002d1629771473):
        _adder_values_002d1629771473=_adder_head_002d1596213198(_adder_values_002dand_002dbody_002d1629771473)
        _adder_body_002d1629771473=_adder_tail_002d1596213198(_adder_values_002dand_002dbody_002d1629771473)
        _adder__0023_003cgensym_002dscratch_0020_0023221_003e=_adder_list_003f_002d1596213198(_adder_values_002d1629771473)
        if _adder__0023_003cgensym_002dscratch_0020_0023221_003e:
            _adder__0023_003cgensym_002dscratch_0020_0023222_003e=adder.common.Symbol('in')
            _adder__0023_003cgensym_002dscratch_0020_0023223_003e=adder.common.Symbol('quote')
            _adder__0023_003cgensym_002dscratch_0020_0023224_003e=[_adder__0023_003cgensym_002dscratch_0020_0023223_003e, _adder_values_002d1629771473]
            _adder__0023_003cgensym_002dscratch_0020_0023225_003e=[_adder__0023_003cgensym_002dscratch_0020_0023222_003e, _adder_value_002d1626523898, _adder__0023_003cgensym_002dscratch_0020_0023224_003e]
            _adder__0023_003cgensym_002dif_0020_0023226_003e=_adder__0023_003cgensym_002dscratch_0020_0023225_003e
        else:
            _adder__0023_003cgensym_002dscratch_0020_0023227_003e=adder.common.Symbol('otherwise')
            _adder__0023_003cgensym_002dscratch_0020_0023228_003e=_adder_values_002d1629771473==_adder__0023_003cgensym_002dscratch_0020_0023227_003e
            if _adder__0023_003cgensym_002dscratch_0020_0023228_003e:
                _adder__0023_003cgensym_002dif_0020_0023229_003e=True
            else:
                if True:
                    _adder__0023_003cgensym_002dscratch_0020_0023230_003e=adder.common.Symbol('==')
                    _adder__0023_003cgensym_002dscratch_0020_0023231_003e=[_adder__0023_003cgensym_002dscratch_0020_0023230_003e, _adder_value_002d1626523898, _adder_values_002d1629771473]
                    _adder__0023_003cgensym_002dif_0020_0023232_003e=_adder__0023_003cgensym_002dscratch_0020_0023231_003e
                else:
                    _adder__0023_003cgensym_002dif_0020_0023232_003e=None
                _adder__0023_003cgensym_002dif_0020_0023229_003e=_adder__0023_003cgensym_002dif_0020_0023232_003e
            _adder__0023_003cgensym_002dif_0020_0023226_003e=_adder__0023_003cgensym_002dif_0020_0023229_003e
        _adder__0023_003cgensym_002dscratch_0020_0023233_003e=[_adder__0023_003cgensym_002dif_0020_0023226_003e]
        _adder__0023_003cgensym_002dscratch_0020_0023234_003e=list(_adder_body_002d1629771473)
        _adder__0023_003cgensym_002dscratch_0020_0023235_003e=_adder__0023_003cgensym_002dscratch_0020_0023233_003e+_adder__0023_003cgensym_002dscratch_0020_0023234_003e
        return _adder__0023_003cgensym_002dscratch_0020_0023235_003e
    _adder__0023_003cgensym_002dscratch_0020_0023236_003e=_adder_map_002d1596213198(_adder__0023_003cgensym_002dlambda_0020_0023220_003e,_adder_cases_002d1634101573)
    _adder__0023_003cgensym_002dscratch_0020_0023237_003e=list(_adder__0023_003cgensym_002dscratch_0020_0023236_003e)
    _adder__0023_003cgensym_002dscratch_0020_0023238_003e=_adder__0023_003cgensym_002dscratch_0020_0023219_003e+_adder__0023_003cgensym_002dscratch_0020_0023237_003e
    _adder__0023_003cgensym_002dscratch_0020_0023239_003e=[_adder__0023_003cgensym_002dscratch_0020_0023215_003e, _adder__0023_003cgensym_002dscratch_0020_0023217_003e, _adder__0023_003cgensym_002dscratch_0020_0023238_003e]
    return _adder__0023_003cgensym_002dscratch_0020_0023239_003e
_adder__0023_003cgensym_002dres_0020_0023240_003e=_adder__0023_003cgensym_002dmacro_002dcase_0020_0023183_003e_002d1596213198
def _adder__0023_003cgensym_002dmacro_002decase_0020_0023241_003e_002d1596213198(_adder_key_002d1628688948,*_adder_cases_002d1628688948):
    _adder__0023_003cgensym_002dscratch_0020_0023242_003e=adder.common.Symbol('case')
    _adder__0023_003cgensym_002dscratch_0020_0023243_003e=[_adder__0023_003cgensym_002dscratch_0020_0023242_003e, _adder_key_002d1628688948]
    _adder__0023_003cgensym_002dscratch_0020_0023244_003e=list(_adder_cases_002d1628688948)
    _adder__0023_003cgensym_002dscratch_0020_0023245_003e=adder.common.Symbol('otherwise')
    _adder__0023_003cgensym_002dscratch_0020_0023246_003e=adder.common.Symbol('error')
    _adder__0023_003cgensym_002dscratch_0020_0023247_003e=[_adder__0023_003cgensym_002dscratch_0020_0023246_003e, 'Fell through ecase']
    _adder__0023_003cgensym_002dscratch_0020_0023248_003e=[_adder__0023_003cgensym_002dscratch_0020_0023245_003e, _adder__0023_003cgensym_002dscratch_0020_0023247_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023249_003e=[_adder__0023_003cgensym_002dscratch_0020_0023248_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023250_003e=_adder__0023_003cgensym_002dscratch_0020_0023244_003e+_adder__0023_003cgensym_002dscratch_0020_0023249_003e
    _adder__0023_003cgensym_002dscratch_0020_0023251_003e=_adder__0023_003cgensym_002dscratch_0020_0023243_003e+_adder__0023_003cgensym_002dscratch_0020_0023250_003e
    return _adder__0023_003cgensym_002dscratch_0020_0023251_003e
_adder__0023_003cgensym_002dres_0020_0023252_003e=_adder__0023_003cgensym_002dmacro_002decase_0020_0023241_003e_002d1596213198
def _adder_take_002d1596213198(_adder_i_002d1623276323,_adder_n_002d1623276323):
    _adder_i_002d1623276323=_adder_iter_002d1596213198(_adder_i_002d1623276323)
    _adder__0023_003cgensym_002dwhile_0020_0023258_003e=None
    _adder__0023_003cgensym_002dscratch_0020_0023259_003e=_adder_n_002d1623276323>0
    while _adder__0023_003cgensym_002dscratch_0020_0023259_003e:
        _adder__0023_003cgensym_002dscratch_0020_0023260_003e=_adder_next_002d1596213198(_adder_i_002d1623276323)
        yield _adder__0023_003cgensym_002dscratch_0020_0023260_003e
        _adder_n_002d1623276323=_adder_n_002d1623276323-1
        _adder__0023_003cgensym_002dwhile_0020_0023258_003e=_adder_n_002d1623276323
        _adder__0023_003cgensym_002dscratch_0020_0023259_003e=_adder_n_002d1623276323>0
_adder__0023_003cgensym_002dres_0020_0023261_003e=_adder_take_002d1596213198
def _adder__0023_003cgensym_002dmacro_002dwhen_0020_0023262_003e_002d1596213198(_adder_cond_002d1622193798,*_adder_body_002d1622193798):
    _adder__0023_003cgensym_002dscratch_0020_0023263_003e=adder.common.Symbol('if')
    _adder__0023_003cgensym_002dscratch_0020_0023264_003e=adder.common.Symbol('begin')
    _adder__0023_003cgensym_002dscratch_0020_0023265_003e=[_adder__0023_003cgensym_002dscratch_0020_0023264_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023266_003e=list(_adder_body_002d1622193798)
    _adder__0023_003cgensym_002dscratch_0020_0023267_003e=_adder__0023_003cgensym_002dscratch_0020_0023265_003e+_adder__0023_003cgensym_002dscratch_0020_0023266_003e
    _adder__0023_003cgensym_002dscratch_0020_0023268_003e=[_adder__0023_003cgensym_002dscratch_0020_0023263_003e, _adder_cond_002d1622193798, _adder__0023_003cgensym_002dscratch_0020_0023267_003e]
    return _adder__0023_003cgensym_002dscratch_0020_0023268_003e
_adder__0023_003cgensym_002dres_0020_0023269_003e=_adder__0023_003cgensym_002dmacro_002dwhen_0020_0023262_003e_002d1596213198
def _adder__0023_003cgensym_002dmacro_002dunless_0020_0023270_003e_002d1596213198(_adder_cond_002d1625441373,*_adder_body_002d1625441373):
    _adder__0023_003cgensym_002dscratch_0020_0023271_003e=adder.common.Symbol('if')
    _adder__0023_003cgensym_002dscratch_0020_0023272_003e=adder.common.Symbol('not')
    _adder__0023_003cgensym_002dscratch_0020_0023273_003e=[_adder__0023_003cgensym_002dscratch_0020_0023272_003e, _adder_cond_002d1625441373]
    _adder__0023_003cgensym_002dscratch_0020_0023274_003e=adder.common.Symbol('begin')
    _adder__0023_003cgensym_002dscratch_0020_0023275_003e=[_adder__0023_003cgensym_002dscratch_0020_0023274_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023276_003e=list(_adder_body_002d1625441373)
    _adder__0023_003cgensym_002dscratch_0020_0023277_003e=_adder__0023_003cgensym_002dscratch_0020_0023275_003e+_adder__0023_003cgensym_002dscratch_0020_0023276_003e
    _adder__0023_003cgensym_002dscratch_0020_0023278_003e=[_adder__0023_003cgensym_002dscratch_0020_0023271_003e, _adder__0023_003cgensym_002dscratch_0020_0023273_003e, _adder__0023_003cgensym_002dscratch_0020_0023277_003e]
    return _adder__0023_003cgensym_002dscratch_0020_0023278_003e
_adder__0023_003cgensym_002dres_0020_0023279_003e=_adder__0023_003cgensym_002dmacro_002dunless_0020_0023270_003e_002d1596213198
def _adder__0023_003cgensym_002dmacro_002ddelay_0020_0023280_003e_002d1596213198(_adder_expr_002d1624358848):
    _adder__0023_003cgensym_002dcache_0020_0023291_003e_002d1614616123=adder.common.Symbol('#<gensym-cache #285>')
    _adder__0023_003cgensym_002dcache_002dvalid_002dp_0020_0023292_003e_002d1614616123=adder.common.Symbol('#<gensym-cache-valid-p #286>')
    _adder_cache_002d1614616123=_adder__0023_003cgensym_002dcache_0020_0023291_003e_002d1614616123
    _adder_cache_002dvalid_002dp_002d1614616123=_adder__0023_003cgensym_002dcache_002dvalid_002dp_0020_0023292_003e_002d1614616123
    _adder__0023_003cgensym_002dscratch_0020_0023305_003e=adder.common.Symbol('let')
    _adder__0023_003cgensym_002dscratch_0020_0023306_003e=adder.common.Symbol('none')
    _adder__0023_003cgensym_002dscratch_0020_0023307_003e=[_adder_cache_002d1614616123, _adder__0023_003cgensym_002dscratch_0020_0023306_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023308_003e=adder.common.Symbol('false')
    _adder__0023_003cgensym_002dscratch_0020_0023309_003e=[_adder_cache_002dvalid_002dp_002d1614616123, _adder__0023_003cgensym_002dscratch_0020_0023308_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023310_003e=[_adder__0023_003cgensym_002dscratch_0020_0023307_003e, _adder__0023_003cgensym_002dscratch_0020_0023309_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023311_003e=adder.common.Symbol('lambda')
    _adder__0023_003cgensym_002dscratch_0020_0023312_003e=[]
    _adder__0023_003cgensym_002dscratch_0020_0023313_003e=adder.common.Symbol('unless')
    _adder__0023_003cgensym_002dscratch_0020_0023314_003e=adder.common.Symbol(':=')
    _adder__0023_003cgensym_002dscratch_0020_0023315_003e=[_adder__0023_003cgensym_002dscratch_0020_0023314_003e, _adder_cache_002d1614616123, _adder_expr_002d1624358848]
    _adder__0023_003cgensym_002dscratch_0020_0023316_003e=adder.common.Symbol(':=')
    _adder__0023_003cgensym_002dscratch_0020_0023317_003e=adder.common.Symbol('true')
    _adder__0023_003cgensym_002dscratch_0020_0023318_003e=[_adder__0023_003cgensym_002dscratch_0020_0023316_003e, _adder_cache_002dvalid_002dp_002d1614616123, _adder__0023_003cgensym_002dscratch_0020_0023317_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023319_003e=[_adder__0023_003cgensym_002dscratch_0020_0023313_003e, _adder_cache_002dvalid_002dp_002d1614616123, _adder__0023_003cgensym_002dscratch_0020_0023315_003e, _adder__0023_003cgensym_002dscratch_0020_0023318_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023320_003e=[_adder__0023_003cgensym_002dscratch_0020_0023311_003e, _adder__0023_003cgensym_002dscratch_0020_0023312_003e, _adder__0023_003cgensym_002dscratch_0020_0023319_003e, _adder_cache_002d1614616123]
    _adder__0023_003cgensym_002dscratch_0020_0023321_003e=[_adder__0023_003cgensym_002dscratch_0020_0023305_003e, _adder__0023_003cgensym_002dscratch_0020_0023310_003e, _adder__0023_003cgensym_002dscratch_0020_0023320_003e]
    return _adder__0023_003cgensym_002dscratch_0020_0023321_003e
_adder__0023_003cgensym_002dres_0020_0023322_003e=_adder__0023_003cgensym_002dmacro_002ddelay_0020_0023280_003e_002d1596213198
def _adder_force_002d1596213198(_adder_promise_002d1613533598):
    _adder__0023_003cgensym_002dscratch_0020_0023327_003e=_adder_promise_002d1613533598()
    return _adder__0023_003cgensym_002dscratch_0020_0023327_003e
_adder__0023_003cgensym_002dres_0020_0023328_003e=_adder_force_002d1596213198
def _adder__0023_003cgensym_002dmacro_002dfor_0020_0023329_003e_002d1596213198(_adder_var_002dand_002dseq_002d1616781173,*_adder_body_002d1616781173):
    _adder__0023_003cgensym_002di_0020_0023340_003e_002d1611368548=adder.common.Symbol('#<gensym-i #334>')
    _adder__0023_003cgensym_002de_0020_0023341_003e_002d1611368548=adder.common.Symbol('#<gensym-e #335>')
    _adder_i_002d1611368548=_adder__0023_003cgensym_002di_0020_0023340_003e_002d1611368548
    _adder_e_002d1611368548=_adder__0023_003cgensym_002de_0020_0023341_003e_002d1611368548
    _adder__0023_003cgensym_002dvar_0020_0023358_003e_002d1601625823=_adder_var_002dand_002dseq_002d1616781173[0]
    _adder__0023_003cgensym_002dseq_0020_0023359_003e_002d1601625823=_adder_var_002dand_002dseq_002d1616781173[1]
    _adder_var_002d1601625823=_adder__0023_003cgensym_002dvar_0020_0023358_003e_002d1601625823
    _adder_seq_002d1601625823=_adder__0023_003cgensym_002dseq_0020_0023359_003e_002d1601625823
    _adder__0023_003cgensym_002dscratch_0020_0023372_003e=adder.common.Symbol('let')
    _adder__0023_003cgensym_002dscratch_0020_0023373_003e=adder.common.Symbol('iter')
    _adder__0023_003cgensym_002dscratch_0020_0023374_003e=[_adder__0023_003cgensym_002dscratch_0020_0023373_003e, _adder_seq_002d1601625823]
    _adder__0023_003cgensym_002dscratch_0020_0023375_003e=[_adder_i_002d1611368548, _adder__0023_003cgensym_002dscratch_0020_0023374_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023376_003e=[_adder__0023_003cgensym_002dscratch_0020_0023375_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023377_003e=adder.common.Symbol('while')
    _adder__0023_003cgensym_002dscratch_0020_0023378_003e=adder.common.Symbol('true')
    _adder__0023_003cgensym_002dscratch_0020_0023379_003e=adder.common.Symbol('let')
    _adder__0023_003cgensym_002dscratch_0020_0023380_003e=adder.common.Symbol('try')
    _adder__0023_003cgensym_002dscratch_0020_0023381_003e=adder.common.Symbol('next')
    _adder__0023_003cgensym_002dscratch_0020_0023382_003e=[_adder__0023_003cgensym_002dscratch_0020_0023381_003e, _adder_i_002d1611368548]
    _adder__0023_003cgensym_002dscratch_0020_0023383_003e=adder.common.Symbol(':StopIteration')
    _adder__0023_003cgensym_002dscratch_0020_0023384_003e=adder.common.Symbol('break')
    _adder__0023_003cgensym_002dscratch_0020_0023385_003e=[_adder__0023_003cgensym_002dscratch_0020_0023384_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023386_003e=[_adder__0023_003cgensym_002dscratch_0020_0023383_003e, _adder_e_002d1611368548, _adder__0023_003cgensym_002dscratch_0020_0023385_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023387_003e=[_adder__0023_003cgensym_002dscratch_0020_0023380_003e, _adder__0023_003cgensym_002dscratch_0020_0023382_003e, _adder__0023_003cgensym_002dscratch_0020_0023386_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023388_003e=[_adder_var_002d1601625823, _adder__0023_003cgensym_002dscratch_0020_0023387_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023389_003e=[_adder__0023_003cgensym_002dscratch_0020_0023388_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023390_003e=[_adder__0023_003cgensym_002dscratch_0020_0023379_003e, _adder__0023_003cgensym_002dscratch_0020_0023389_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023391_003e=list(_adder_body_002d1616781173)
    _adder__0023_003cgensym_002dscratch_0020_0023392_003e=_adder__0023_003cgensym_002dscratch_0020_0023390_003e+_adder__0023_003cgensym_002dscratch_0020_0023391_003e
    _adder__0023_003cgensym_002dscratch_0020_0023393_003e=[_adder__0023_003cgensym_002dscratch_0020_0023377_003e, _adder__0023_003cgensym_002dscratch_0020_0023378_003e, _adder__0023_003cgensym_002dscratch_0020_0023392_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023394_003e=[_adder__0023_003cgensym_002dscratch_0020_0023372_003e, _adder__0023_003cgensym_002dscratch_0020_0023376_003e, _adder__0023_003cgensym_002dscratch_0020_0023393_003e]
    return _adder__0023_003cgensym_002dscratch_0020_0023394_003e
_adder__0023_003cgensym_002dres_0020_0023395_003e=_adder__0023_003cgensym_002dmacro_002dfor_0020_0023329_003e_002d1596213198
def _adder__0023_003cgensym_002dmacro_002dif_002dbind_0020_0023396_003e_002d1596213198(_adder_var_002dand_002dcond_002d1600543298,_adder_then_002d1600543298,_adder_else_002d1600543298):
    _adder__0023_003cgensym_002dvar_0020_0023401_003e_002d1668742373=_adder_var_002dand_002dcond_002d1600543298[0]
    _adder__0023_003cgensym_002dcond_0020_0023402_003e_002d1668742373=_adder_var_002dand_002dcond_002d1600543298[1]
    _adder_var_002d1668742373=_adder__0023_003cgensym_002dvar_0020_0023401_003e_002d1668742373
    _adder_cond_002d1668742373=_adder__0023_003cgensym_002dcond_0020_0023402_003e_002d1668742373
    _adder__0023_003cgensym_002dscratch_0020_0023415_003e=adder.common.Symbol('let')
    _adder__0023_003cgensym_002dscratch_0020_0023416_003e=[_adder_var_002d1668742373, _adder_cond_002d1668742373]
    _adder__0023_003cgensym_002dscratch_0020_0023417_003e=[_adder__0023_003cgensym_002dscratch_0020_0023416_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023418_003e=adder.common.Symbol('if')
    _adder__0023_003cgensym_002dscratch_0020_0023419_003e=[_adder__0023_003cgensym_002dscratch_0020_0023418_003e, _adder_var_002d1668742373, _adder_then_002d1600543298, _adder_else_002d1600543298]
    _adder__0023_003cgensym_002dscratch_0020_0023420_003e=[_adder__0023_003cgensym_002dscratch_0020_0023415_003e, _adder__0023_003cgensym_002dscratch_0020_0023417_003e, _adder__0023_003cgensym_002dscratch_0020_0023419_003e]
    return _adder__0023_003cgensym_002dscratch_0020_0023420_003e
_adder__0023_003cgensym_002dres_0020_0023421_003e=_adder__0023_003cgensym_002dmacro_002dif_002dbind_0020_0023396_003e_002d1596213198
def _adder__0023_003cgensym_002dmacro_002dwhen_002dbind_0020_0023422_003e_002d1596213198(_adder_var_002dand_002dcond_002d1667659848,_adder_then_002d1667659848):
    _adder__0023_003cgensym_002dvar_0020_0023427_003e_002d1657917123=_adder_var_002dand_002dcond_002d1667659848[0]
    _adder__0023_003cgensym_002dcond_0020_0023428_003e_002d1657917123=_adder_var_002dand_002dcond_002d1667659848[1]
    _adder_var_002d1657917123=_adder__0023_003cgensym_002dvar_0020_0023427_003e_002d1657917123
    _adder_cond_002d1657917123=_adder__0023_003cgensym_002dcond_0020_0023428_003e_002d1657917123
    _adder__0023_003cgensym_002dscratch_0020_0023441_003e=adder.common.Symbol('let')
    _adder__0023_003cgensym_002dscratch_0020_0023442_003e=[_adder_var_002d1657917123, _adder_cond_002d1657917123]
    _adder__0023_003cgensym_002dscratch_0020_0023443_003e=[_adder__0023_003cgensym_002dscratch_0020_0023442_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023444_003e=adder.common.Symbol('when')
    _adder__0023_003cgensym_002dscratch_0020_0023445_003e=[_adder__0023_003cgensym_002dscratch_0020_0023444_003e, _adder_var_002d1657917123, _adder_then_002d1667659848]
    _adder__0023_003cgensym_002dscratch_0020_0023446_003e=[_adder__0023_003cgensym_002dscratch_0020_0023441_003e, _adder__0023_003cgensym_002dscratch_0020_0023443_003e, _adder__0023_003cgensym_002dscratch_0020_0023445_003e]
    return _adder__0023_003cgensym_002dscratch_0020_0023446_003e
_adder__0023_003cgensym_002dres_0020_0023447_003e=_adder__0023_003cgensym_002dmacro_002dwhen_002dbind_0020_0023422_003e_002d1596213198
def _adder__0023_003cgensym_002dmacro_002dyield_002a_0020_0023448_003e_002d1596213198(_adder_subseq_002d1656834598):
    _adder__0023_003cgensym_002dx_0020_0023461_003e_002d1651421973=adder.common.Symbol('#<gensym-x #453>')
    _adder__0023_003cgensym_002di_0020_0023462_003e_002d1651421973=adder.common.Symbol('#<gensym-i #454>')
    _adder__0023_003cgensym_002dstack_0020_0023463_003e_002d1651421973=adder.common.Symbol('#<gensym-stack #455>')
    _adder__0023_003cgensym_002dstop_0020_0023464_003e_002d1651421973=adder.common.Symbol('#<gensym-stop #456>')
    _adder_x_002d1651421973=_adder__0023_003cgensym_002dx_0020_0023461_003e_002d1651421973
    _adder_i_002d1651421973=_adder__0023_003cgensym_002di_0020_0023462_003e_002d1651421973
    _adder_stack_002d1651421973=_adder__0023_003cgensym_002dstack_0020_0023463_003e_002d1651421973
    _adder_stop_002d1651421973=_adder__0023_003cgensym_002dstop_0020_0023464_003e_002d1651421973
    _adder__0023_003cgensym_002dscratch_0020_0023485_003e=adder.common.Symbol('let')
    _adder__0023_003cgensym_002dscratch_0020_0023486_003e=adder.common.Symbol('mk-list')
    _adder__0023_003cgensym_002dscratch_0020_0023487_003e=adder.common.Symbol('iter')
    _adder__0023_003cgensym_002dscratch_0020_0023488_003e=[_adder__0023_003cgensym_002dscratch_0020_0023487_003e, _adder_subseq_002d1656834598]
    _adder__0023_003cgensym_002dscratch_0020_0023489_003e=[_adder__0023_003cgensym_002dscratch_0020_0023486_003e, _adder__0023_003cgensym_002dscratch_0020_0023488_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023490_003e=[_adder_stack_002d1651421973, _adder__0023_003cgensym_002dscratch_0020_0023489_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023491_003e=[_adder__0023_003cgensym_002dscratch_0020_0023490_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023492_003e=adder.common.Symbol('while')
    _adder__0023_003cgensym_002dscratch_0020_0023493_003e=adder.common.Symbol('let')
    _adder__0023_003cgensym_002dscratch_0020_0023494_003e=adder.common.Symbol('[]')
    _adder__0023_003cgensym_002dscratch_0020_0023495_003e=[_adder__0023_003cgensym_002dscratch_0020_0023494_003e, _adder_stack_002d1651421973, -1]
    _adder__0023_003cgensym_002dscratch_0020_0023496_003e=[_adder_i_002d1651421973, _adder__0023_003cgensym_002dscratch_0020_0023495_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023497_003e=[_adder__0023_003cgensym_002dscratch_0020_0023496_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023498_003e=adder.common.Symbol('while')
    _adder__0023_003cgensym_002dscratch_0020_0023499_003e=adder.common.Symbol('true')
    _adder__0023_003cgensym_002dscratch_0020_0023500_003e=adder.common.Symbol('let')
    _adder__0023_003cgensym_002dscratch_0020_0023501_003e=adder.common.Symbol('try')
    _adder__0023_003cgensym_002dscratch_0020_0023502_003e=adder.common.Symbol('next')
    _adder__0023_003cgensym_002dscratch_0020_0023503_003e=[_adder__0023_003cgensym_002dscratch_0020_0023502_003e, _adder_i_002d1651421973]
    _adder__0023_003cgensym_002dscratch_0020_0023504_003e=adder.common.Symbol(':StopIteration')
    _adder__0023_003cgensym_002dscratch_0020_0023505_003e=adder.common.Symbol('.')
    _adder__0023_003cgensym_002dscratch_0020_0023506_003e=adder.common.Symbol('pop')
    _adder__0023_003cgensym_002dscratch_0020_0023507_003e=[_adder__0023_003cgensym_002dscratch_0020_0023505_003e, _adder_stack_002d1651421973, _adder__0023_003cgensym_002dscratch_0020_0023506_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023508_003e=[_adder__0023_003cgensym_002dscratch_0020_0023507_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023509_003e=adder.common.Symbol('break')
    _adder__0023_003cgensym_002dscratch_0020_0023510_003e=[_adder__0023_003cgensym_002dscratch_0020_0023509_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023511_003e=[_adder__0023_003cgensym_002dscratch_0020_0023504_003e, _adder_stop_002d1651421973, _adder__0023_003cgensym_002dscratch_0020_0023508_003e, _adder__0023_003cgensym_002dscratch_0020_0023510_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023512_003e=[_adder__0023_003cgensym_002dscratch_0020_0023501_003e, _adder__0023_003cgensym_002dscratch_0020_0023503_003e, _adder__0023_003cgensym_002dscratch_0020_0023511_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023513_003e=[_adder_x_002d1651421973, _adder__0023_003cgensym_002dscratch_0020_0023512_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023514_003e=[_adder__0023_003cgensym_002dscratch_0020_0023513_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023515_003e=adder.common.Symbol('if')
    _adder__0023_003cgensym_002dscratch_0020_0023516_003e=adder.common.Symbol('generator?')
    _adder__0023_003cgensym_002dscratch_0020_0023517_003e=[_adder__0023_003cgensym_002dscratch_0020_0023516_003e, _adder_x_002d1651421973]
    _adder__0023_003cgensym_002dscratch_0020_0023518_003e=adder.common.Symbol('begin')
    _adder__0023_003cgensym_002dscratch_0020_0023519_003e=adder.common.Symbol('.')
    _adder__0023_003cgensym_002dscratch_0020_0023520_003e=adder.common.Symbol('append')
    _adder__0023_003cgensym_002dscratch_0020_0023521_003e=[_adder__0023_003cgensym_002dscratch_0020_0023519_003e, _adder_stack_002d1651421973, _adder__0023_003cgensym_002dscratch_0020_0023520_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023522_003e=[_adder__0023_003cgensym_002dscratch_0020_0023521_003e, _adder_x_002d1651421973]
    _adder__0023_003cgensym_002dscratch_0020_0023523_003e=adder.common.Symbol('break')
    _adder__0023_003cgensym_002dscratch_0020_0023524_003e=[_adder__0023_003cgensym_002dscratch_0020_0023523_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023525_003e=[_adder__0023_003cgensym_002dscratch_0020_0023518_003e, _adder__0023_003cgensym_002dscratch_0020_0023522_003e, _adder__0023_003cgensym_002dscratch_0020_0023524_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023526_003e=adder.common.Symbol('yield')
    _adder__0023_003cgensym_002dscratch_0020_0023527_003e=[_adder__0023_003cgensym_002dscratch_0020_0023526_003e, _adder_x_002d1651421973]
    _adder__0023_003cgensym_002dscratch_0020_0023528_003e=[_adder__0023_003cgensym_002dscratch_0020_0023515_003e, _adder__0023_003cgensym_002dscratch_0020_0023517_003e, _adder__0023_003cgensym_002dscratch_0020_0023525_003e, _adder__0023_003cgensym_002dscratch_0020_0023527_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023529_003e=[_adder__0023_003cgensym_002dscratch_0020_0023500_003e, _adder__0023_003cgensym_002dscratch_0020_0023514_003e, _adder__0023_003cgensym_002dscratch_0020_0023528_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023530_003e=[_adder__0023_003cgensym_002dscratch_0020_0023498_003e, _adder__0023_003cgensym_002dscratch_0020_0023499_003e, _adder__0023_003cgensym_002dscratch_0020_0023529_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023531_003e=[_adder__0023_003cgensym_002dscratch_0020_0023493_003e, _adder__0023_003cgensym_002dscratch_0020_0023497_003e, _adder__0023_003cgensym_002dscratch_0020_0023530_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023532_003e=[_adder__0023_003cgensym_002dscratch_0020_0023492_003e, _adder_stack_002d1651421973, _adder__0023_003cgensym_002dscratch_0020_0023531_003e]
    _adder__0023_003cgensym_002dscratch_0020_0023533_003e=[_adder__0023_003cgensym_002dscratch_0020_0023485_003e, _adder__0023_003cgensym_002dscratch_0020_0023491_003e, _adder__0023_003cgensym_002dscratch_0020_0023532_003e]
    return _adder__0023_003cgensym_002dscratch_0020_0023533_003e
__adder__last__=_adder__0023_003cgensym_002dmacro_002dyield_002a_0020_0023448_003e_002d1596213198
_adder__0023_003cgensym_002dres_0020_0023534_003e=__adder__last__
import cgi
_adder__0023_003cgensym_002dres_0020_0023535_003e=cgi
import os
_adder__0023_003cgensym_002dres_0020_0023536_003e=os
_adder__0023_003cgensym_002dscratch_0020_0023537_003e=cgi.FieldStorage
_adder_cgi_002dfields_002d1596213198=_adder__0023_003cgensym_002dscratch_0020_0023537_003e()
_adder__0023_003cgensym_002dres_0020_0023538_003e=_adder_cgi_002dfields_002d1596213198
def _adder_field_002d1596213198(_adder_name_002d1650339448,_adder_default_002dvalue_002d1650339448=None):
    _adder__0023_003cgensym_002dscratch_0020_0023573_003e=_adder_name_002d1650339448 in _adder_cgi_002dfields_002d1596213198
    if _adder__0023_003cgensym_002dscratch_0020_0023573_003e:
        _adder__0023_003cgensym_002df_0020_0023547_003e_002d1647091873=_adder_cgi_002dfields_002d1596213198[_adder_name_002d1650339448]
        _adder_f_002d1647091873=_adder__0023_003cgensym_002df_0020_0023547_003e_002d1647091873
        _adder__0023_003cgensym_002dscratch_0020_0023574_003e=not(_adder_f_002d1647091873)
        if _adder__0023_003cgensym_002dscratch_0020_0023574_003e:
            _adder__0023_003cgensym_002dif_0020_0023575_003e=_adder_default_002dvalue_002d1650339448
        else:
            _adder__0023_003cgensym_002dscratch_0020_0023576_003e=python.isinstance(_adder_f_002d1647091873,_adder_type_002dlist_002d1596213198)
            if _adder__0023_003cgensym_002dscratch_0020_0023576_003e:
                def _adder__0023_003cgensym_002dlambda_0020_0023577_003e(_adder_obj_002d1640596723):
                    _adder__0023_003cgensym_002dscratch_0020_0023578_003e=_adder_obj_002d1640596723.value
                    return _adder__0023_003cgensym_002dscratch_0020_0023578_003e
                _adder__0023_003cgensym_002dscratch_0020_0023579_003e=_adder_f_002d1647091873[0]
                _adder__0023_003cgensym_002dscratch_0020_0023580_003e=_adder__0023_003cgensym_002dlambda_0020_0023577_003e(_adder__0023_003cgensym_002dscratch_0020_0023579_003e)
                _adder__0023_003cgensym_002dif_0020_0023581_003e=_adder__0023_003cgensym_002dscratch_0020_0023580_003e
            else:
                if True:
                    def _adder__0023_003cgensym_002dlambda_0020_0023582_003e(_adder_obj_002d1642761773):
                        _adder__0023_003cgensym_002dscratch_0020_0023583_003e=_adder_obj_002d1642761773.value
                        return _adder__0023_003cgensym_002dscratch_0020_0023583_003e
                    _adder__0023_003cgensym_002dscratch_0020_0023584_003e=_adder__0023_003cgensym_002dlambda_0020_0023582_003e(_adder_f_002d1647091873)
                    _adder__0023_003cgensym_002dif_0020_0023585_003e=_adder__0023_003cgensym_002dscratch_0020_0023584_003e
                else:
                    _adder__0023_003cgensym_002dif_0020_0023585_003e=None
                _adder__0023_003cgensym_002dif_0020_0023581_003e=_adder__0023_003cgensym_002dif_0020_0023585_003e
            _adder__0023_003cgensym_002dif_0020_0023575_003e=_adder__0023_003cgensym_002dif_0020_0023581_003e
        _adder__0023_003cgensym_002dif_0020_0023586_003e=_adder__0023_003cgensym_002dif_0020_0023575_003e
    else:
        _adder__0023_003cgensym_002dif_0020_0023586_003e=_adder_default_002dvalue_002d1650339448
    return _adder__0023_003cgensym_002dif_0020_0023586_003e
_adder__0023_003cgensym_002dres_0020_0023587_003e=_adder_field_002d1596213198
def _adder_fields_002d1596213198(_adder_name_002d1641679248):
    _adder__0023_003cgensym_002dscratch_0020_0023619_003e=_adder_name_002d1641679248 in _adder_cgi_002dfields_002d1596213198
    if _adder__0023_003cgensym_002dscratch_0020_0023619_003e:
        _adder__0023_003cgensym_002df_0020_0023596_003e_002d1638431673=_adder_cgi_002dfields_002d1596213198[_adder_name_002d1641679248]
        _adder_f_002d1638431673=_adder__0023_003cgensym_002df_0020_0023596_003e_002d1638431673
        _adder__0023_003cgensym_002dscratch_0020_0023620_003e=not(_adder_f_002d1638431673)
        if _adder__0023_003cgensym_002dscratch_0020_0023620_003e:
            _adder__0023_003cgensym_002dscratch_0020_0023621_003e=[]
            _adder__0023_003cgensym_002dif_0020_0023622_003e=_adder__0023_003cgensym_002dscratch_0020_0023621_003e
        else:
            _adder__0023_003cgensym_002dscratch_0020_0023623_003e=python.isinstance(_adder_f_002d1638431673,_adder_type_002dlist_002d1596213198)
            if _adder__0023_003cgensym_002dscratch_0020_0023623_003e:
                def _adder__0023_003cgensym_002dlambda_0020_0023624_003e(_adder_obj_002d1637349148):
                    _adder__0023_003cgensym_002dscratch_0020_0023625_003e=_adder_obj_002d1637349148.value
                    return _adder__0023_003cgensym_002dscratch_0020_0023625_003e
                _adder__0023_003cgensym_002dscratch_0020_0023626_003e=_adder_map_002d1596213198(_adder__0023_003cgensym_002dlambda_0020_0023624_003e,_adder_f_002d1638431673)
                _adder__0023_003cgensym_002dscratch_0020_0023627_003e=list(_adder__0023_003cgensym_002dscratch_0020_0023626_003e)
                _adder__0023_003cgensym_002dif_0020_0023628_003e=_adder__0023_003cgensym_002dscratch_0020_0023627_003e
            else:
                if True:
                    def _adder__0023_003cgensym_002dlambda_0020_0023629_003e(_adder_obj_002d1700135598):
                        _adder__0023_003cgensym_002dscratch_0020_0023630_003e=_adder_obj_002d1700135598.value
                        return _adder__0023_003cgensym_002dscratch_0020_0023630_003e
                    _adder__0023_003cgensym_002dscratch_0020_0023631_003e=_adder__0023_003cgensym_002dlambda_0020_0023629_003e(_adder_f_002d1638431673)
                    _adder__0023_003cgensym_002dscratch_0020_0023632_003e=[_adder__0023_003cgensym_002dscratch_0020_0023631_003e]
                    _adder__0023_003cgensym_002dif_0020_0023633_003e=_adder__0023_003cgensym_002dscratch_0020_0023632_003e
                else:
                    _adder__0023_003cgensym_002dif_0020_0023633_003e=None
                _adder__0023_003cgensym_002dif_0020_0023628_003e=_adder__0023_003cgensym_002dif_0020_0023633_003e
            _adder__0023_003cgensym_002dif_0020_0023622_003e=_adder__0023_003cgensym_002dif_0020_0023628_003e
        _adder__0023_003cgensym_002dif_0020_0023634_003e=_adder__0023_003cgensym_002dif_0020_0023622_003e
    else:
        _adder__0023_003cgensym_002dscratch_0020_0023635_003e=[]
        _adder__0023_003cgensym_002dif_0020_0023634_003e=_adder__0023_003cgensym_002dscratch_0020_0023635_003e
    return _adder__0023_003cgensym_002dif_0020_0023634_003e
_adder__0023_003cgensym_002dres_0020_0023636_003e=_adder_fields_002d1596213198
def _adder_field_002dnames_002d1596213198():
    def _adder__0023_003cgensym_002dlambda_0020_0023647_003e(_adder_obj_002d1696888023):
        _adder__0023_003cgensym_002dscratch_0020_0023648_003e=_adder_obj_002d1696888023.keys
        return _adder__0023_003cgensym_002dscratch_0020_0023648_003e
    _adder__0023_003cgensym_002dscratch_0020_0023649_003e=_adder__0023_003cgensym_002dlambda_0020_0023647_003e(_adder_cgi_002dfields_002d1596213198)
    _adder__0023_003cgensym_002dscratch_0020_0023650_003e=_adder__0023_003cgensym_002dscratch_0020_0023649_003e()
    _adder__0023_003cgensym_002dscratch_0020_0023651_003e=list(_adder__0023_003cgensym_002dscratch_0020_0023650_003e)
    return _adder__0023_003cgensym_002dscratch_0020_0023651_003e
_adder__0023_003cgensym_002dres_0020_0023652_003e=_adder_field_002dnames_002d1596213198
def _adder_file_002dto_002dload_002d1596213198():
    def _adder_path_002d1695805498():
        _adder__0023_003cgensym_002dscratch_0020_0023688_003e=os.getenv
        _adder__0023_003cgensym_002dscratch_0020_0023689_003e=_adder__0023_003cgensym_002dscratch_0020_0023688_003e('PATH_INFO')
        if _adder__0023_003cgensym_002dscratch_0020_0023689_003e:
            _adder__0023_003cgensym_002dif_0020_0023690_003e=_adder__0023_003cgensym_002dscratch_0020_0023689_003e
        else:
            _adder__0023_003cgensym_002dif_0020_0023690_003e='/'
        _adder__0023_003cgensym_002dp_0020_0023666_003e_002d1691475398='./pages'+_adder__0023_003cgensym_002dif_0020_0023690_003e
        _adder_p_002d1691475398=_adder__0023_003cgensym_002dp_0020_0023666_003e_002d1691475398
        _adder__0023_003cgensym_002dscratch_0020_0023691_003e=os.path.exists
        _adder__0023_003cgensym_002dscratch_0020_0023692_003e=_adder__0023_003cgensym_002dscratch_0020_0023691_003e(_adder_p_002d1691475398)
        if _adder__0023_003cgensym_002dscratch_0020_0023692_003e:
            _adder__0023_003cgensym_002dscratch_0020_0023693_003e=os.path.isdir
            _adder__0023_003cgensym_002dscratch_0020_0023694_003e=_adder__0023_003cgensym_002dscratch_0020_0023693_003e(_adder_p_002d1691475398)
            _adder__0023_003cgensym_002dif_0020_0023695_003e=_adder__0023_003cgensym_002dscratch_0020_0023694_003e
        else:
            _adder__0023_003cgensym_002dif_0020_0023695_003e=_adder__0023_003cgensym_002dscratch_0020_0023692_003e
        if _adder__0023_003cgensym_002dif_0020_0023695_003e:
            _adder__0023_003cgensym_002dscratch_0020_0023696_003e=_adder_p_002d1691475398.endswith
            _adder__0023_003cgensym_002dscratch_0020_0023697_003e=_adder__0023_003cgensym_002dscratch_0020_0023696_003e('/')
            if _adder__0023_003cgensym_002dscratch_0020_0023697_003e:
                _adder__0023_003cgensym_002dif_0020_0023698_003e=''
            else:
                _adder__0023_003cgensym_002dif_0020_0023698_003e='/'
            _adder__0023_003cgensym_002dscratch_0020_0023699_003e=_adder__0023_003cgensym_002dif_0020_0023698_003e+'index.+'
            _adder__0023_003cgensym_002dscratch_0020_0023700_003e=_adder_p_002d1691475398+_adder__0023_003cgensym_002dscratch_0020_0023699_003e
            _adder__0023_003cgensym_002dif_0020_0023701_003e=_adder__0023_003cgensym_002dscratch_0020_0023700_003e
        else:
            _adder__0023_003cgensym_002dif_0020_0023701_003e=_adder_p_002d1691475398
        return _adder__0023_003cgensym_002dif_0020_0023701_003e
    _adder__0023_003cgensym_002dp_0020_0023679_003e_002d1688227823=_adder_path_002d1695805498()
    _adder_p_002d1688227823=_adder__0023_003cgensym_002dp_0020_0023679_003e_002d1688227823
    _adder__0023_003cgensym_002dscratch_0020_0023702_003e=os.path.exists
    _adder__0023_003cgensym_002dscratch_0020_0023703_003e=_adder__0023_003cgensym_002dscratch_0020_0023702_003e(_adder_p_002d1688227823)
    if _adder__0023_003cgensym_002dscratch_0020_0023703_003e:
        _adder__0023_003cgensym_002dif_0020_0023704_003e=_adder_p_002d1688227823
    else:
        _adder__0023_003cgensym_002dif_0020_0023704_003e='404.+'
    return _adder__0023_003cgensym_002dif_0020_0023704_003e
_adder__0023_003cgensym_002dres_0020_0023705_003e=_adder_file_002dto_002dload_002d1596213198
print('Content-Type: text/html')
_adder__0023_003cgensym_002dres_0020_0023706_003e='Content-Type: text/html'
print('')
_adder__0023_003cgensym_002dres_0020_0023707_003e=''
import sys
_adder__0023_003cgensym_002dres_0020_0023708_003e=sys
_adder_page_002denv_002d1596213198=globals()
_adder__0023_003cgensym_002dres_0020_0023713_003e=_adder_page_002denv_002d1596213198
class _adder_O_002d1596213198:
    pass
_adder__0023_003cgensym_002dres_0020_0023714_003e=_adder_O_002d1596213198
_adder__0040_002d1596213198=_adder_O_002d1596213198()
_adder__0023_003cgensym_002dres_0020_0023719_003e=_adder__0040_002d1596213198
_adder__0023_003cgensym_002dscratch_0020_0023753_003e=_adder_field_002dnames_002d1596213198()
_adder__0023_003cgensym_002d_0023_003cgensym_002di_0020_0023334_003e_0020_0023729_003e_002d1683897723=_adder_iter_002d1596213198(_adder__0023_003cgensym_002dscratch_0020_0023753_003e)
_adder__0023_003cgensym_002di_0020_0023334_003e_002d1683897723=_adder__0023_003cgensym_002d_0023_003cgensym_002di_0020_0023334_003e_0020_0023729_003e_002d1683897723
_adder__0023_003cgensym_002dwhile_0020_0023754_003e=None
while True:
    try:
        _adder__0023_003cgensym_002dscratch_0020_0023756_003e=_adder_next_002d1596213198(_adder__0023_003cgensym_002di_0020_0023334_003e_002d1683897723)
        _adder__0023_003cgensym_002dscratch_0020_0023755_003e=_adder__0023_003cgensym_002dscratch_0020_0023756_003e
    except StopIteration as _adder__0023_003cgensym_002de_0020_0023335_003e_002d1679567623:
        _adder__0023_003cgensym_002dwhile_0020_0023754_003e=None
        break
        _adder__0023_003cgensym_002dscratch_0020_0023755_003e=None
    _adder__0023_003cgensym_002dname_0020_0023743_003e_002d1684980248=_adder__0023_003cgensym_002dscratch_0020_0023755_003e
    _adder_name_002d1684980248=_adder__0023_003cgensym_002dname_0020_0023743_003e_002d1684980248
    _adder__0023_003cgensym_002dscratch_0020_0023757_003e=python.setattr
    _adder__0023_003cgensym_002dscratch_0020_0023758_003e=_adder_field_002d1596213198(_adder_name_002d1684980248)
    _adder__0023_003cgensym_002dscratch_0020_0023757_003e(_adder__0040_002d1596213198,_adder_name_002d1684980248,_adder__0023_003cgensym_002dscratch_0020_0023758_003e)
    _adder__0023_003cgensym_002dscratch_0020_0023759_003e=python.setattr
    _adder__0023_003cgensym_002dscratch_0020_0023760_003e=_adder_name_002d1684980248+'[]'
    _adder__0023_003cgensym_002dscratch_0020_0023761_003e=_adder_fields_002d1596213198(_adder_name_002d1684980248)
    _adder__0023_003cgensym_002dscratch_0020_0023762_003e=_adder__0023_003cgensym_002dscratch_0020_0023759_003e(_adder__0040_002d1596213198,_adder__0023_003cgensym_002dscratch_0020_0023760_003e,_adder__0023_003cgensym_002dscratch_0020_0023761_003e)
    _adder__0023_003cgensym_002dwhile_0020_0023754_003e=_adder__0023_003cgensym_002dscratch_0020_0023762_003e
_adder__0023_003cgensym_002dres_0020_0023763_003e=_adder__0023_003cgensym_002dwhile_0020_0023754_003e
def _adder__0023_003cgensym_002dlambda_0020_0023770_003e(_adder_obj_002d1681732673):
    _adder__0023_003cgensym_002dscratch_0020_0023771_003e=_adder_obj_002d1681732673.toPython
    return _adder__0023_003cgensym_002dscratch_0020_0023771_003e
_adder__0023_003cgensym_002dscratch_0020_0023772_003e=adder.common.Symbol('@')
_adder_page_002denv_002d1596213198[_adder__0023_003cgensym_002dlambda_0020_0023770_003e(_adder__0023_003cgensym_002dscratch_0020_0023772_003e)]=_adder__0040_002d1596213198
_adder__0023_003cgensym_002dscratch_0020_0023773_003e=_adder_page_002denv_002d1596213198[_adder__0023_003cgensym_002dlambda_0020_0023770_003e(_adder__0023_003cgensym_002dscratch_0020_0023772_003e)]
_adder__0023_003cgensym_002dres_0020_0023774_003e=_adder__0023_003cgensym_002dscratch_0020_0023773_003e
_adder__0023_003cgensym_002dscratch_0020_0023775_003e=_adder_file_002dto_002dload_002d1596213198()
_adder__0023_003cgensym_002dscratch_0020_0023776_003e=getScopeById(1596213198)
__adder__last__=load(_adder__0023_003cgensym_002dscratch_0020_0023775_003e,_adder__0023_003cgensym_002dscratch_0020_0023776_003e,_adder_page_002denv_002d1596213198,True)
_adder__0023_003cgensym_002dres_0020_0023777_003e=__adder__last__



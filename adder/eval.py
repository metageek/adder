from adder.env import Env
from adder.symbol import Symbol, intern

def evaluate(exprAndLine, env):
    (expr, line) = exprAndLine
    if isinstance(expr, Symbol):
        path=expr.name.split('.')
        if not path:
            raise KeyError(expr.name)
        res=env[path[0]]
        for p in path[1:]:
            res=getattr(res, p)
        return res
    if type(expr) in [str, int, float]:
        return expr
    if isinstance(expr, list):
        if not expr:
            return []
        f=evaluate(expr[0], env)
        args=list(map(lambda x: evaluate(x, env), expr[1:]))
        return f(*args)

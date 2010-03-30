import adder.gomer

def reverse(l):
    l2=list(l)
    l2.reverse()
    return l2

def stdenv():
    return adder.gomer.Env(adder.gomer.Scope(None),None)

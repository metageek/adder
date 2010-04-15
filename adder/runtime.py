import adder.gomer

def reverse(l):
    l2=list(l)
    l2.reverse()
    return l2

def stdenv():
    return adder.gomer.Env(adder.gomer.Scope(None),None)

class ReturnValue(Exception):
    def __init__(self,block,value):
        self.block=block
        self.value=value

    def __str__(self):
        return 'Block %s shall return %s' % (self.block,
                                            str(self.value))

class YieldValue(Exception):
    def __init__(self,block,value):
        self.block=block
        self.value=value

    def __str__(self):
        return 'Block %s shall yield %s' % (self.block,
                                            str(self.value))

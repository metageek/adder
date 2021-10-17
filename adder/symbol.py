class Symbol:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

table={}

def intern(name):
    if name in table:
        return table[name]
    else:
        sym = Symbol(name)
        table[name] = sym
        return sym

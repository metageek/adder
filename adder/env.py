class Env:
    def __init__(self, parent = None):
        self.parent = parent
        self.d = {}

    def __getitem__(self, key):
        if key in self.d:
            return self.d[key]
        if self.parent is not None:
            return self.parent[key]
        raise KeyError(key)

    def __contains__(self, key):
        if key in self.d:
            return True
        if self.parent is None:
            return False
        return key in self.parent

    def __setitem__(self, key, value):
        if key in self.d:
            self.d[key] = value
            return value
        else:
            cur = self.parent
            while cur is not None:
                if key in cur:
                    cur[key] = value
                    return value
                if isinstance(cur, Env):
                    cur = cur.parent
                else:
                    break
            raise KeyError(key)

    def bind(self, key, value):
        if key in self.d:
            raise KeyError(key)
        self.d[key] = value
        return value

    def __delitem__(self, key):
        del self.d[key]

    def keys(self):
        res=set(self.d.keys())
        if self.parent is not None:
            res.update(self.parent.keys())
        return res

    def items(self):
        for k in self.keys():
            yield (k, self[k])

    def values(self):
        return map(lambda kv: kv[1], self.items())

    def __len__(self):
        res=0
        for k in self.keys():
            res += 1
        return res

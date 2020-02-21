#!/usr/bin/env python3

import itertools

def fib():
    n1=1
    n2=1
    tmp=None
    yield n1
    yield n2
    while True:
        tmp=n1+n2
        yield tmp
        n1=n2
        n2=tmp

print(list(itertools.islice(fib(), 500)))

#!/usr/bin/env python3

import sys,adder

#print(sys.path_hooks)
#i=sys.path_hooks[1]('/home/francis/github/metageek/adder/+modules+')
#i.load_module('foo')
import foo

assert foo.fact(7)==5040

import bar.baz
assert bar.baz.fib(7)==13

#!/usr/bin/env python3

import sys,os

progDir=os.path.dirname(__file__)
pkgDir=os.path.join(progDir,'adder')
sys.path.append(pkgDir)

import adder.repl

adder.repl.repl()

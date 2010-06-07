#!/usr/bin/env python3

import sys,os,getopt

interactive=True
(opts,args)=getopt.getopt(sys.argv[1:],"h?",["help"])
for (opt,optval) in opts:
    if opt in ["-h","-?","--help"]:
        print("""Usage: %s [FILE]...
FILEs are Adder source files to load.  If none specified, will run
in interactive mode.""" % sys.argv[0])
        sys.exit()

progDir=os.path.dirname(__file__)
pkgDir=os.path.join(progDir,'adder')
sys.path.append(pkgDir)

import adder.repl
repl=adder.repl.Repl()

for f in args:
    interactive=False
    repl.load(f)

if interactive:
    repl.run()

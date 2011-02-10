#!/usr/bin/env python3

import sys,os,getopt

interactive=False
profile=False
cache=False

(opts,args)=getopt.getopt(sys.argv[1:],"h?i",
                          ["help","interactive","profile","cache"])
for (opt,optval) in opts:
    if opt in ["-h","-?","--help"]:
        print("""Usage: %s [OPTIONS] [FILE]...
FILEs are Adder source files to load.  If none specified, will run
in interactive mode.

Options:
  -i, --interactive    Run in interactive mode after loading files (if any).
  -h, -?, --help       This help.
""" % sys.argv[0])
        sys.exit()
    if opt in ["-i","--interactive"]:
        interactive=True
        continue
    if opt=='--profile':
        profile=True
        continue
    if opt=='--cache':
        cache=True
        continue

progDir=os.path.dirname(__file__)
pkgDir=os.path.join(progDir,'adder')
sys.path.append(pkgDir)
sys.path.append('%s/+modules+' % progDir)

if not args:
    interactive=True

import adder.repl
repl=adder.repl.Repl(interactive=interactive)

def doIt():
    if cache:
        assert len(args)==1

    for f in args:
        repl.load(f,cache=cache)

    if interactive:
        repl.run()

if profile:
    import cProfile
    cProfile.run('doIt()','adderprof')
else:
    doIt()

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
  --cache              Cache the script.  Works only with one script;
                         not compatible with interactive mode.
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

if cache:
    assert (not interactive) and len(args)==1 and args[0].endswith('.+')


def doIt():
    if cache:
        import adder.compiler,adder.util,adder.gomer
        f=args[0]
        cacheOutputFileName=f[:-2]+'.py'
        if (os.path.exists(cacheOutputFileName)
            and adder.util.isNewer(cacheOutputFileName,f)):
            code=open(cacheOutputFileName,'r').read()
            exec(code,adder.gomer.mkGlobals())
        else:
            context=adder.compiler.Context(cacheOutputFileName=
                                           cacheOutputFileName)
            context.load(args[0])
            context.close(cacheSymbols=False)

    else:
        import adder.repl
        repl=adder.repl.Repl(interactive=interactive)
        for f in args:
            repl.load(f)

        if interactive:
            repl.run()

if profile:
    import cProfile
    cProfile.run('doIt()','adderprof')
else:
    doIt()

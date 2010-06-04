from adder.parser import parseStream
from adder.compiler import Context
import sys,pdb

def readEvalGenerator(context,instream,exceptionHandler):
    for parsedExpr in parseStream(instream):
        try:
            yield context.eval(parsedExpr,hasLines=True)
        except Exception as e:
            if exceptionHandler:
                exceptionHandler(e)
            else:
                raise

def repl(*,context=None,
           instream=None,
           outstream=None,
           prompt='> '):
    if instream is None:
        instream=sys.stdin
    if outstream is None:
        outstream=sys.stdout
    if context is None:
        outstream.write('Loading prelude...')
        outstream.flush()
        context=Context()
        outstream.write('done.\n')
    def exceptionHandler(e):
        outstream.write('Exception: %s\n' % str(e))

    outstream.write(prompt)
    outstream.flush()
    for val in readEvalGenerator(context,instream,exceptionHandler):
        outstream.write('%s\n' % repr(val))
        outstream.write(prompt)
        outstream.flush()

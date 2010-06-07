from adder.parser import parseStream
from adder.compiler import Context
import adder.common
import sys,pdb,readline

def readEvalGenerator(context,instream,exceptionHandler):
    for parsedExpr in parseStream(instream):
        try:
            yield context.eval(parsedExpr,hasLines=True)
        except Exception as e:
            if exceptionHandler:
                exceptionHandler(e)
            else:
                raise

class Repl:
    def __init__(self,*,context=None,prompt='> ',
                 instream=None,outstream=None,
                 interactive=True):
        self.context=context
        self.prompt=prompt
        self.instream=instream
        self.outstream=outstream
        if self.instream is None:
            if interactive:
                def readlines():
                    while True:
                        try:
                            line=input()
                        except EOFError:
                            break
                        yield line+'\n'
                self.instream=readlines()
            else:
                self.instream=sys.stdin
        if self.outstream is None:
            self.outstream=sys.stdout
        if self.context is None:
            if interactive:
                self.outstream.write('Loading prelude...')
                self.outstream.flush()
            self.context=Context()
            if interactive:
                self.outstream.write('done.\n')

    def load(self,f):
        self.context.load(f)

    def run(self):
        def exceptionHandler(e):
            self.outstream.write('Exception: %s\n%s' % (str(e),self.prompt))

        self.outstream.write(self.prompt)
        self.outstream.flush()
        for val in readEvalGenerator(self.context,
                                     self.instream,
                                     exceptionHandler):
            self.outstream.write('%s\n' % adder.common.adderStr(val))
            self.outstream.write(self.prompt)
            self.outstream.flush()

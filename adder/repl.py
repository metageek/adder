from adder.parser import parseStream
from adder.eval import evaluate
import adder.prelude
import sys

try:
    import readline
except ImportError:
    pass

def readEvalGenerator(instream, exceptionHandler, env):
    for parsedExpr in parseStream(instream):
        try:
            yield evaluate(parsedExpr, env)
        except Exception as e:
            if exceptionHandler:
                exceptionHandler(e)
            raise

class Repl:
    def __init__(self,*,prompt='> ',
                 instream=None,outstream=None,
                 interactive=True):
        self.root=adder.prelude.make()
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

    def run(self):
        def exceptionHandler(e):
            self.outstream.write('Exception: %s\n%s' % (str(e),self.prompt))

        self.outstream.write(self.prompt)
        self.outstream.flush()
        for val in readEvalGenerator(self.instream,
                                     exceptionHandler,
                                     self.root):
            self.outstream.write('%s\n' % val)
            self.outstream.write(self.prompt)
            self.outstream.flush()

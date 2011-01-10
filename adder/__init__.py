import sys,re,os.path,imp
import adder.compiler

class Importer:
    def __init__(self,pathItem):
        m=Importer.adderDirRe.match(pathItem)
        if not m:
            raise ImportError()

        (dirname,_,basename)=m.groups()
        self.path=dirname+basename

    adderDirRe=re.compile('(^|(.*/))\+([^/]+)\+$')

    def load_module(self,fullname):
        relative=fullname.replace('.',os.path.sep)
        absolute=os.path.join(self.path,relative)
        adderSource=absolute+'.+'
        if os.path.isfile(adderSource):
            print('Found:',adderSource)
            pySource=absolute+'.py'
            if os.path.isfile(pySource):
                print('Already compiled:',pySource)
            else:
                context=adder.compiler.Context(cacheOutputFileName=pySource)
                context.load(adderSource)
                context.close()
            code = open(pySource,'r').read()
            mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
            mod.__file__ = adderSource
            mod.__loader__ = self
            exec(code,mod.__dict__)
            return mod

        raise ImportError

1

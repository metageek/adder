import sys,re,os,os.path,imp
import adder.compiler

class Importer:
    def __init__(self,pathItem):
        m=Importer.adderDirRe.match(pathItem)
        if not m:
            raise ImportError()

        (dirname,_,basename)=m.groups()
        self.path=dirname+basename

    adderDirRe=re.compile('(^|(.*/))\+([^/]+)\+$')

    def isNewer(f1,f2):
        stat1=os.stat(f1)
        stat2=os.stat(f2)
        return stat1.st_atime>stat2.st_atime

    def find_module(self,fullname,path=None):
        relative=fullname.replace('.',os.path.sep)
        absolute=os.path.join(self.path,relative)
        adderSource=absolute+'.+'
        if os.path.isfile(adderSource):
            return self

    def load_module(self,fullname):
        relative=fullname.replace('.',os.path.sep)
        absolute=os.path.join(self.path,relative)
        adderSource=absolute+'.+'
        if os.path.isfile(adderSource):
            print('Found:',adderSource)
            pySource=absolute+'.py'
            if os.path.isfile(pySource) and Importer.isNewer(pySource,
                                                             adderSource):
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

sys.path_hooks.append(Importer)
sys.path_importer_cache.clear()
1

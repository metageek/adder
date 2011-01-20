import sys,re,os,os.path,imp,pdb
import adder.compiler

class Importer:
    def __init__(self,pathItem):
        self.pathItem=pathItem
        if os.path.exists(pathItem):
            raise ImportError()
        (dirname,basename)=os.path.split(pathItem)
        if not (basename.startswith('+') and basename.endswith('+')):
            raise ImportError()
        basename=basename[1:-1]
        self.path=os.path.join(dirname,basename)

    def __str__(self):
        return '<%s for "%s">' % (self.__class__.__name__, self.path)

    def isNewer(f1,f2):
        stat1=os.stat(f1)
        stat2=os.stat(f2)
        return stat1.st_atime>stat2.st_atime

    def absolute_path(self,fullname,path=None):
        if not path:
            path=self.path
        relative=fullname.replace('.',os.path.sep)
        absolute=os.path.join(path,relative)
        isPkg=os.path.isdir(absolute)
        if isPkg:
            absolute+='/__init__'
        adderSource=absolute+'.+'
        if os.path.isfile(adderSource):
            return (adderSource,absolute+'.py',isPkg)

    def find_module(self,fullname,path=None):
        if self.absolute_path(fullname,path):
            return self

    def load_module(self,fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]

        found=self.absolute_path(fullname)
        if not found:
            raise ImportError

        (adderSource,pySource,isPkg)=found
        if not (os.path.isfile(pySource)
                and Importer.isNewer(pySource,
                                     adderSource)
                ):
            context=adder.compiler.Context(cacheOutputFileName=pySource)
            context.load(adderSource)
            context.close()
        code = open(pySource,'r').read()
        mod = imp.new_module(fullname)
        sys.modules[fullname]=mod
        try:
            mod.__file__ = adderSource
            mod.__loader__ = self
            if isPkg:
                mod.__path__ = [self.pathItem]
            exec(code,mod.__dict__)
            return mod
        except Exception:
            del sys.modules[fullname]
            raise

sys.path_hooks.append(Importer)
sys.path_importer_cache.clear()
1

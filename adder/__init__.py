import sys,re,os,os.path,imp,pdb
import adder.compiler

class Importer:
    def __init__(self,pathItem):
        m=Importer.adderDirRe.match(pathItem)
        if not m:
            raise ImportError()

        (dirname,_,basename)=m.groups()
        self.path=dirname+basename
        print('Importer(%s): %s' % (pathItem,self.path))

    def __str__(self):
        return '<%s for "%s">' % (self.__class__.__name__, self.path)

    adderDirRe=re.compile('(^|(.*/))\+([^/]+)\+$')

    def isNewer(f1,f2):
        stat1=os.stat(f1)
        stat2=os.stat(f2)
        return stat1.st_atime>stat2.st_atime

    def absolute_path(self,fullname,path=None):
        relative=fullname.replace('.',os.path.sep)
        absolute=os.path.join(self.path,relative)
        isPkg=os.path.isdir(absolute)
        if isPkg:
            absolute+='/__init__'
        adderSource=absolute+'.+'
        if os.path.isfile(adderSource):
            return (adderSource,absolute+'.py',isPkg)

    def find_module(self,fullname,path=None):
        print('Importer<%s>.find_module(%s,%s)' % (self.path,
                                                   fullname,
                                                   str(path)))
        if self.absolute_path(fullname,path):
            return self

    def load_module(self,fullname):
        print('Importer<%s>.load_module(%s)' % (self.path,fullname))
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
                mod.__path__ = [fullname]
            exec(code,mod.__dict__)
            print('\tloaded %s' % repr(mod))
            return mod
        except Exception:
            del sys.modules[fullname]
            raise

sys.path_hooks.append(Importer)
sys.path_importer_cache.clear()
1

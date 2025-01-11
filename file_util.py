import ast, sys, os
try:
    from tokenize import open as fopen
except ImportError:
    fopen = open
class CodeToAst(object):
    @staticmethod
    def find_py_files(srctree, ignore=None):
        if not os.path.isdir(srctree):
            yield os.path.split(srctree)
        for srcpath, _, fnames in os.walk(srctree):
            if ignore is not None and ignore in srcpath:
                continue
            for fname in (x for x in fnames if x.endswith('.py')):
                yield srcpath, fname
    @staticmethod
    def parse_file(fname):
        try:
            with fopen(fname) as f:
                fstr = f.read()
        except IOError:
            if fname != 'stdin':
                raise
            sys.stdout.write('\nReading from stdin:\n\n')
            fstr = sys.stdin.read()
        fstr = fstr.replace('\r\n', '\n').replace('\r', '\n')
        if not fstr.endswith('\n'):
            fstr += '\n'
        return ast.parse(fstr, filename=fname)
    @staticmethod
    def get_file_info(codeobj):
        fname = getattr(codeobj, '__file__', None)
        linenum = 0
        if fname is None:
            func_code = codeobj.__code__
            fname = func_code.co_filename
            linenum = func_code.co_firstlineno
        fname = fname.replace('.pyc', '.py')
        return fname, linenum
    def __init__(self, cache=None):
        self.cache = cache or {}
    def __call__(self, codeobj):
        cache = self.cache
        key = self.get_file_info(codeobj)
        result = cache.get(key)
        if result is not None:
            return result
        fname = key[0]
        cache[fname, 0] = mod_ast = self.parse_file(fname)
        for obj in mod_ast.body:
            if not isinstance(obj, ast.FunctionDef):
                continue
            cache[fname, obj.lineno] = obj
        return cache[key]
code_to_ast = CodeToAst()

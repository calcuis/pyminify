import ast, itertools
try:
    zip_longest = itertools.zip_longest
except AttributeError:
    zip_longest = itertools.izip_longest
class NonExistent(object):
    pass
def iter_node(node, name='', unknown=None, list=list, getattr=getattr,
    isinstance=isinstance, enumerate=enumerate, missing=NonExistent):
    fields = getattr(node, '_fields', None)
    if fields is not None:
        for name in fields:
            value = getattr(node, name, missing)
            if value is not missing:
                yield value, name
        if unknown is not None:
            unknown.update(set(vars(node)) - set(fields))
    elif isinstance(node, list):
        for value in node:
            yield value, name
def dump_tree(node, name=None, initial_indent='', indentation='    ',
    maxline=120, maxmerged=80, iter_node=iter_node, special=ast.AST, list=
    list, isinstance=isinstance, type=type, len=len):
    def dump(node, name=None, indent=''):
        level = indent + indentation
        name = name and name + '=' or ''
        values = list(iter_node(node))
        if isinstance(node, list):
            prefix, suffix = '%s[' % name, ']'
        elif values:
            prefix, suffix = '%s%s(' % (name, type(node).__name__), ')'
        elif isinstance(node, special):
            prefix, suffix = name + type(node).__name__, ''
        else:
            return '%s%s' % (name, repr(node))
        node = [dump(a, b, level) for a, b in values if b != 'ctx']
        oneline = '%s%s%s' % (prefix, ', '.join(node), suffix)
        if len(oneline) + len(indent) < maxline:
            return '%s' % oneline
        if node and len(prefix) + len(node[0]) < maxmerged:
            prefix = '%s%s,' % (prefix, node.pop(0))
        node = (',\n%s' % level).join(node).lstrip()
        return '%s\n%s%s%s' % (prefix, level, node, suffix)
    return dump(node, name, initial_indent)
def strip_tree(node, iter_node=iter_node, special=ast.AST, list=list,
    isinstance=isinstance, type=type, len=len):
    stripped = set()
    def strip(node, indent):
        unknown = set()
        leaf = True
        for subnode, _ in iter_node(node, unknown=unknown):
            leaf = False
            strip(subnode, indent + '    ')
        if leaf:
            if isinstance(node, special):
                unknown = set(vars(node))
        stripped.update(unknown)
        for name in unknown:
            delattr(node, name)
        if hasattr(node, 'ctx'):
            delattr(node, 'ctx')
            if 'ctx' in node._fields:
                mylist = list(node._fields)
                mylist.remove('ctx')
                node._fields = mylist
    strip(node, '')
    return stripped
class ExplicitNodeVisitor(ast.NodeVisitor):
    def abort_visit(node):
        msg = 'No defined handler for node of type %s'
        raise AttributeError(msg % node.__class__.__name__)
    def visit(self, node, abort=abort_visit):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, abort)
        return visitor(node)
def allow_ast_comparison():
    class CompareHelper(object):
        def __eq__(self, other):
            return type(self) == type(other) and vars(self) == vars(other)
        def __ne__(self, other):
            return type(self) != type(other) or vars(self) != vars(other)
    for item in vars(ast).values():
        if type(item) != type:
            continue
        if issubclass(item, ast.AST):
            try:
                item.__bases__ = tuple(list(item.__bases__) + [CompareHelper])
            except TypeError:
                pass
def fast_compare(tree1, tree2):
    geta = ast.AST.__getattribute__
    work = [(tree1, tree2)]
    pop = work.pop
    extend = work.extend
    exception = TypeError, AttributeError
    zipl = zip_longest
    type_ = type
    list_ = list
    while work:
        n1, n2 = pop()
        try:
            f1 = geta(n1, '_fields')
            f2 = geta(n2, '_fields')
        except exception:
            if type_(n1) is list_:
                extend(zipl(n1, n2))
                continue
            if n1 == n2:
                continue
            return False
        else:
            f1 = [x for x in f1 if x != 'ctx']
            if f1 != [x for x in f2 if x != 'ctx']:
                return False
            extend((geta(n1, fname), geta(n2, fname)) for fname in f1)
    return True

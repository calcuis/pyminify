from .node_util import iter_node
class MetaFlatten(type):
    def __new__(clstype, name, bases, clsdict):
        newbases = object,
        newdict = {}
        for base in reversed(bases):
            if base not in newbases:
                newdict.update(vars(base))
        newdict.update(clsdict)
        newdict.pop('__dict__', None)
        newdict.pop('__weakref__', None)
        return type.__new__(clstype, name, newbases, newdict)
MetaFlatten = MetaFlatten('MetaFlatten', (object,), {})
class TreeWalk(MetaFlatten):
    def __init__(self, node=None):
        self.nodestack = []
        self.setup()
        if node is not None:
            self.walk(node)
    def setup(self):
        self.pre_handlers = pre_handlers = {}
        self.post_handlers = post_handlers = {}
        for name in sorted(vars(type(self))):
            if name.startswith('init_'):
                getattr(self, name)()
            elif name.startswith('pre_'):
                pre_handlers[name[4:]] = getattr(self, name)
            elif name.startswith('post_'):
                post_handlers[name[5:]] = getattr(self, name)
    def walk(self, node, name='', list=list, len=len, type=type):
        pre_handlers = self.pre_handlers.get
        post_handlers = self.post_handlers.get
        nodestack = self.nodestack
        emptystack = len(nodestack)
        append, pop = nodestack.append, nodestack.pop
        append([node, name, list(iter_node(node, name + '_item')), -1])
        while len(nodestack) > emptystack:
            node, name, subnodes, index = nodestack[-1]
            if index >= len(subnodes):
                handler = post_handlers(type(node).__name__) or post_handlers(
                    name + '_name')
                if handler is None:
                    pop()
                    continue
                self.cur_node = node
                self.cur_name = name
                handler()
                current = nodestack and nodestack[-1]
                popstack = current and current[0] is node
                if popstack and current[-1] >= len(current[-2]):
                    pop()
                continue
            nodestack[-1][-1] = index + 1
            if index < 0:
                handler = pre_handlers(type(node).__name__) or pre_handlers(
                    name + '_name')
                if handler is not None:
                    self.cur_node = node
                    self.cur_name = name
                    if handler():
                        pop()
            else:
                node, name = subnodes[index]
                append([node, name, list(iter_node(node, name + '_item')), -1])
    @property
    def parent(self):
        nodestack = self.nodestack
        if len(nodestack) < 2:
            return None
        return nodestack[-2][0]
    @property
    def parent_name(self):
        nodestack = self.nodestack
        if len(nodestack) < 2:
            return None
        return nodestack[-2][:2]
    def replace(self, new_node):
        cur_node = self.cur_node
        nodestack = self.nodestack
        cur = nodestack.pop()
        prev = nodestack[-1]
        index = prev[-1] - 1
        oldnode, name = prev[-2][index]
        assert cur[0] is cur_node is oldnode, (cur[0], cur_node, prev[-2],
            index)
        parent = prev[0]
        if isinstance(parent, list):
            parent[index] = new_node
        else:
            setattr(parent, name, new_node)

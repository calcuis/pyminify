def pretty_source(source):
    return ''.join(split_lines(source))
def split_lines(source, maxline=79):
    result = []
    extend = result.extend
    append = result.append
    line = []
    multiline = False
    count = 0
    for item in source:
        newline = type(item)('\n')
        index = item.find(newline)
        if index:
            line.append(item)
            multiline = index > 0
            count += len(item)
        else:
            if line:
                if count <= maxline or multiline:
                    extend(line)
                else:
                    wrap_line(line, maxline, result)
                count = 0
                multiline = False
                line = []
            append(item)
    return result
def count(group, slen=str.__len__):
    return sum([slen(x) for x in group])
def wrap_line(line, maxline=79, result=[], count=count):
    append = result.append
    extend = result.extend
    indentation = line[0]
    lenfirst = len(indentation)
    indent = lenfirst - len(indentation.lstrip())
    assert indent in (0, lenfirst)
    indentation = line.pop(0) if indent else ''
    dgroups = list(delimiter_groups(line))
    unsplittable = dgroups[::2]
    splittable = dgroups[1::2]
    if max(count(x) for x in unsplittable) > maxline - indent:
        line = add_parens(line, maxline, indent)
        dgroups = list(delimiter_groups(line))
        unsplittable = dgroups[::2]
        splittable = dgroups[1::2]
    first = unsplittable[0]
    append(indentation)
    extend(first)
    if not splittable:
        return result
    pos = indent + count(first)
    indentation += '    '
    indent += 4
    if indent >= maxline / 2:
        maxline = maxline / 2 + indent
    for sg, nsg in zip(splittable, unsplittable[1:]):
        if sg:
            if pos > indent and pos + len(sg[0]) > maxline:
                append('\n')
                append(indentation)
                pos = indent
            csg = count(sg)
            while pos + csg > maxline:
                ready, sg = split_group(sg, pos, maxline)
                if ready[-1].endswith(' '):
                    ready[-1] = ready[-1][:-1]
                extend(ready)
                append('\n')
                append(indentation)
                pos = indent
                csg = count(sg)
            if sg:
                extend(sg)
                pos += csg
        cnsg = count(nsg)
        if pos > indent and pos + cnsg > maxline:
            append('\n')
            append(indentation)
            pos = indent
        extend(nsg)
        pos += cnsg
def split_group(source, pos, maxline):
    first = []
    source.reverse()
    while source:
        tok = source.pop()
        first.append(tok)
        pos += len(tok)
        if source:
            tok = source[-1]
            allowed = maxline + 1 if tok.endswith(' ') else maxline - 4
            if pos + len(tok) > allowed:
                break
    source.reverse()
    return first, source
begin_delim = set('([{')
end_delim = set(')]}')
end_delim.add('):')
def delimiter_groups(line, begin_delim=begin_delim, end_delim=end_delim):
    text = []
    line = iter(line)
    while True:
        for item in line:
            text.append(item)
            if item in begin_delim:
                break
        if not text:
            break
        yield text
        level = 0
        text = []
        for item in line:
            if item in begin_delim:
                level += 1
            elif item in end_delim:
                level -= 1
                if level < 0:
                    yield text
                    text = [item]
                    break
            text.append(item)
        else:
            assert not text, text
            break
statements = set(['del ', 'return', 'yield ', 'if ', 'while '])
def add_parens(line, maxline, indent, statements=statements, count=count):
    if line[0] in statements:
        index = 1
        if not line[0].endswith(' '):
            index = 2
            assert line[1] == ' '
        line.insert(index, '(')
        if line[-1] == ':':
            line.insert(-1, ')')
        else:
            line.append(')')
    groups = list(get_assign_groups(line))
    if len(groups) == 1:
        return line
    counts = list(count(x) for x in groups)
    didwrap = False
    if sum(counts[:-1]) >= maxline - indent - 4:
        for group in groups[:-1]:
            didwrap = False
            if len(group) > 1:
                group.insert(0, '(')
                group.insert(-1, ')')
                didwrap = True
    if not didwrap or counts[-1] > maxline - indent - 10:
        groups[-1].insert(0, '(')
        groups[-1].append(')')
    return [item for group in groups for item in group]
ops = list('|^&+-*/%@~') + '<< >> // **'.split() + ['']
ops = set(' %s= ' % x for x in ops)
def get_assign_groups(line, ops=ops):
    group = []
    for item in line:
        group.append(item)
        if item in ops:
            yield group
            group = []
    yield group

import re
# from numpy import unicode_
basestring = str
# unicode = unicode_
# try:
#     special_unicode = unicode
# except NameError:
#     class special_unicode(object):
#         pass
try:
    basestring = basestring
except NameError:
    basestring = str
def _properly_indented(s, line_indent):
    mylist = s.split('\n')[1:]
    mylist = [x.rstrip() for x in mylist]
    mylist = [x for x in mylist if x]
    if not s:
        return False
    counts = [(len(x) - len(x.lstrip())) for x in mylist]
    return counts and min(counts) >= line_indent
mysplit = re.compile('(\\\\|\\"\\"\\"|\\"$)').split
replacements = {'\\': '\\\\', '"""': '""\\"', '"': '\\"'}
def _prep_triple_quotes(s, mysplit=mysplit, replacements=replacements):
    """ Split the string up and force-feed some replacements
        to make sure it will round-trip OK
    """
    s = mysplit(s)
    s[1::2] = (replacements[x] for x in s[1::2])
    return ''.join(s)
def string_triplequote_repr(s):
    """Return string's python representation in triple quotes.
    """
    return '"""%s"""' % _prep_triple_quotes(s)
def pretty_string(s, embedded, current_line, uni_lit=False, min_trip_str=20,
    max_line=100):
    default = repr(s)
    # if isinstance(s, special_unicode) or not isinstance(s, basestring):
    #     return default
    if uni_lit and isinstance(s, bytes):
        return 'b' + default
    len_s = len(default)
    if current_line.strip():
        len_current = len(current_line)
        second_line_start = s.find('\n') + 1
        if embedded > 1 and not second_line_start:
            return default
        if len_s < min_trip_str:
            return default
        line_indent = len_current - len(current_line.lstrip())
        if embedded and not second_line_start:
            return default
        total_len = len_current + len_s
        if total_len < max_line and not _properly_indented(s, line_indent):
            return default
    fancy = string_triplequote_repr(s)
    try:
        if eval(fancy) == s and '\r' not in fancy:
            return fancy
    except Exception:
        pass
    return default

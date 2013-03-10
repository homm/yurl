import re
from collections import deque


def _restore(cls, args):
    return tuple.__new__(cls, args)


# This is not validating regexp.
# It splits url to unambiguous parts according RFC.
_split_re = re.compile(r'''
    (?:([^:/?#]+):)?            # scheme
    (?://                       # authority
        (?:([^/?\#@]*)@)?       # userinfo
        ([^/?\#]*)()            # host:port
    )?
    ([^?\#]*)                   # path
    \??([^\#]*)                 # query
    \#?(.*)                     # fragment
    ''', re.VERBOSE | re.DOTALL).match


def split_url(url):
    # All other arguments are ignored.
    groups = _split_re(url).groups('')

    # Host itself can contain digits and ':', so we cant use regexp.
    # It is bit different from other behaviors: instead of splitting
    # as is, and raise on validate, we split port only with digits.
    # I believe this is expected behavior.
    host = groups[2]
    port_idx = host.rfind(':')
    if port_idx >= 0:
        port = host[port_idx + 1:]
        if not port or port.isdigit():
            return groups[0:2] + (host[:port_idx], port) + groups[4:7]

    return groups


def decode_url(url, encoding='utf-8'):
    raise NotImplementedError
    return url


def decode_url_component(url, encoding=None):
    """Decode percent-encoded reserved chars. Do not escape all other
    percent-encoded chars until encoding argument is given.
    Should be applied on last stage of parsing.
    """
    global _hexmap
    try:
        hexmap = _hexmap
    except NameError:
        hexmap = _hexmap = {}
        for char in ":/?#[]@!$&'()*+,;=":
            a, b = hex(ord(char))[2:]
            hexmap[a + b] = hexmap[a.upper() + b.upper()] = char
            hexmap[a.upper() + b] = hexmap[b + b.upper()] = char

    if encoding is not None:
        url = decode_url(url, encoding)

    # This implementation minimize string copying and concatenations.
    # Concatenation to result is used insted of joining parts because it is
    # faster on current python implementations include pypy.
    result = ''
    last = 0
    pct = url.find('%')
    while pct >= 0:
        try:
            char = hexmap[url[pct+1:pct+3]]
        except KeyError:
            # just skip
            pass
        else:
            result += url[last:pct]
            result += char
            last = pct + 3
        pct = url.find('%', pct + 1)
    return result + url[last:]


def remove_dot_segments(path):
    stack = deque()
    last = 0
    for segment in path.split('/'):
        if segment == '.':
            pass
        elif segment == '..':
            if len(stack):
                stack.pop()
        else:
            stack.append(segment)
    if path.endswith(('/.', '/..')):
        stack.append('')
    return '/'.join(stack)

from __future__ import print_function, unicode_literals
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


def decode_url(url, encoding='utf-8', errors='replace'):
    """Decode percent-encoded unreserved chars.
    Can be applied on anytime before or after parsing.
    """
    global _all_hexmap
    try:
        hexmap = _all_hexmap
    except NameError:
        _hexdig = '0123456789ABCDEFabcdef'
        _skip = set(map(ord, ":/?#[]@!$&'()*+,;="))
        hexmap = _all_hexmap = dict((a + b, int(a + b, 16))
                                    for a in _hexdig for b in _hexdig
                                    if int(a + b, 16) not in _skip)

    result = ''
    last = 0
    encoded = bytearray()
    pct = url.find('%')
    while pct >= 0:
        stop = pct
        try:
            while True:
                encoded.append(hexmap[url[pct+1:pct+3]])
                pct += 3
                if url[pct] != '%':
                    break
        except (KeyError, IndexError):
            pass
        if encoded:
            result += url[last:stop]
            result += encoded.decode(encoding, errors)
            last = pct
            del encoded[:]
        pct = url.find('%', pct + 1)
    return result + url[last:]


def decode_url_component(url, encoding=None, errors='replace'):
    """Decode percent-encoded reserved chars. Do not unquote all other
    percent-encoded chars until encoding argument is given.
    Should be applied on last stage of parsing.
    """
    global _reserved_hexmap
    try:
        hexmap = _reserved_hexmap
    except NameError:
        hexmap = _reserved_hexmap = {}
        for char in ":/?#[]@!$&'()*+,;=":
            a, b = hex(ord(char))[2:]
            hexmap[a + b] = hexmap[a + b.upper()] = char

    if encoding is not None:
        url = decode_url(url, encoding, errors)

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

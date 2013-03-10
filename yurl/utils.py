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

import re
from collections import namedtuple, deque

# This module based on rfc3986.


# Validation errors.

class InvalidScheme(ValueError): pass
class InvalidAuthority(ValueError): pass
class InvalidUserinfo(InvalidAuthority): pass
class InvalidHost(InvalidAuthority): pass
class InvalidPath(ValueError): pass
class InvalidQuery(ValueError): pass


URLTuple = namedtuple('URLBase', 'scheme host path query fragment '
                                 'userinfo port')


class URL(URLTuple):
    """
    Class for manipulation with escaped parts of url.
    It can parse any url from string or can be constructed with provided parts.
    If source of url not trusted, method validate() can be used to check url.
    """
    __slots__ = ()

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

    def __new__(cls, url=None, scheme='', host='', path='', query='',
                fragment='', userinfo='', port=''):
        if url is not None:
            # All other arguments are ignored.
            (scheme, userinfo, host, port,
             path, query, fragment) = cls._split_re(url).groups('')

            # Host itself can contain digits and ':', so we cant use regexp.
            # It is bit different from other behaviors: instead of splitting
            # as is, and raise on validate, we split port only with digits.
            # I believe this is expected behavior.
            _port_idx = host.rfind(':')
            if _port_idx >= 0:
                _port = host[_port_idx + 1:]
                if not _port or _port.isdigit():
                    host, port = host[:_port_idx], _port
        else:
            if (userinfo or host or port) and path and path[0] != '/':
                path = '/' + path

        # | Although schemes are case-insensitive, the canonical form
        # | is lowercase. An implementation should only produce lowercase
        # | scheme names for consistency.

        # | Although host is case-insensitive, producers and normalizers
        # | should use lowercase for registered names and hexadecimal
        # | addresses for the sake of uniformity.

        return tuple.__new__(cls, (scheme.lower(), host.lower(), path, query,
                                   fragment, userinfo, str(port)))

    ### Serialization

    def __unicode__(self):
        base = self.authority
        path = self[2]

        if base:
            base = '//' + base

        # Escape path with slashes by adding explicit empty host.
        elif path[0:2] == '//':
            base = '//'

        # scheme
        if self[0]:
            base = self[0] + ':' + base

        # if url starts with path
        elif not base and ':' in path.partition('/')[0]:
            base = './'

        return base + self.full_path

    as_string = __unicode__

    def __reduce__(self):
        return type(self), (None,) + tuple(self)

    ### Missing properties

    @property
    def authority(self):
        authority = self[1]
        userinfo, port = self[5:7]
        if port:
            authority += ':' + port
        if userinfo:
            return userinfo + '@' + authority
        return authority

    @property
    def full_path(self):
        path, query, fragment = self[2:5]
        if query:
            path += '?' + query
        if fragment:
            path += '#' + fragment
        return path

    ### Information

    def __nonzero__(self):
        return any(self)

    def has_authority(self):
        return bool(self[1] or self[5] or self[6])

    def is_relative(self):
        # In terms of rfc relative url have no scheme.
        # See is_relative_path().
        return not self[0]

    def is_relative_path(self):
        # Absolute path always starts with slash. Also paths with authority
        # can not be relative.
        return not self[2][:1] == '/' and not (
            self[0] or self.has_authority())

    def is_host_ipv4(self):
        if self[1][:1] != '[':
            parts = self[1].split('.')
            if len(parts) == 4 and all(part.isdigit() for part in parts):
                if all(int(part, 10) < 256 for part in parts):
                    return True
        return False

    def is_host_ip(self):
        if self.is_host_ipv4():
            return True

        if self[1][:1] == '[' and self[1][-1:] == ']':
            return True

        return False

    ### Validation

    _valid_scheme_re = re.compile(r'^[a-z][a-z0-9+\-.]*$').match
    # '[' and ']' the only chars not allowed in userinfo and not delimiters
    _valid_userinfo_re = re.compile(r'^[^/?\#@\[\]]+$').match
    _valid_reg_name_re = re.compile(r'^[^/?\#@\[\]:]+$').match
    _valid_path_re = re.compile(r'^[^?\#]+$').match
    _valid_query_re = re.compile(r'^[^\#]+$').match
    # This primitive regular expression not match complicated ip literal.
    _valid_ip_literal_re = re.compile(r'''
        ^(?:
            v[a-f0-9]+\.[a-z0-9\-._~!$&'()*,;=:]+
            |
            [a-f0-9:\.]+
        )$
        ''', re.VERBOSE | re.IGNORECASE).match

    def validate(self):
        if self[0]:
            if not self._valid_scheme_re(self[0]):
                raise InvalidScheme()

        if self[5]:
            if not self._valid_userinfo_re(self[5]):
                raise InvalidUserinfo()

        host = self[1]
        if host:
            if host[:1] == '[' and host[-1:] == ']':
                if not self._valid_ip_literal_re(host[1:-1]):
                    raise InvalidHost()

            # valid ipv4 is also valid reg_name
            elif not self._valid_reg_name_re(host):
                raise InvalidHost()

        # Acording rfc there is two cases when path can be invalid:
        # There should be no scheme and authority and first segment of path
        # should contain ':' or starts with '//'. But this library not about
        # punish user. We can escape this paths when formatting string.
        if self[2]:
            if not self._valid_path_re(self[2]):
                raise InvalidPath()

        if self[3]:
            if not self._valid_query_re(self[3]):
                raise InvalidQuery()

        return self

    ### Manipulation

    def __add__(self, other):
        # This method designed with one issue. By rfc delimeters without
        # following values are matter. For example:
        # 'http://ya.ru/page' + '//?none' = 'http:'
        # 'http://ya.ru/page?param' + '?' = 'http://ya.ru/page'
        # But the parser makes no distinction between empty and undefined part.
        # 'http://ya.ru/page' + '//?none' = 'http://ya.ru/page?none'
        # 'http://ya.ru/page?param' + '?' = 'http://ya.ru/page?param'
        # Same bug also present in urllib.parse.urljoin.
        # I hope it will be fixed in future yurls.
        # TODO: call remove_dot_segments() when path not modified.

        if not isinstance(other, URLTuple):
            raise NotImplementedError()

        scheme, host, path, query, fragment, userinfo, port = other

        if not scheme:
            scheme = self[0]

            if not (host or userinfo or port):
                host, userinfo, port = self[1], self[5], self[6]

                if not path:
                    path = self[2]

                    if not query:
                        query = self[3]

                else:
                    if path[0] != '/':
                        parts = self[2].rpartition('/')
                        path = parts[0] + parts[1] + path

        return URL.__new__(type(self), None, scheme, host,
                           self.remove_dot_segments(path),
                           query, fragment, userinfo, port)

    def __radd__(self, left):
        # if other is instance of URL(), __radd__() should not be called.
        if type(left) == URLTuple:
            return URL.__add__(left, self)

        raise NotImplementedError()

    def replace(self, scheme=None, host=None, path=None, query=None,
                fragment=None, userinfo=None, port=None, authority=None,
                full_path=None):
        if authority is not None:
            if host or userinfo or port:
                raise TypeError()

            # Use original URL just for parse.
            _, host, _, _, _, userinfo, port = URL('//' + authority)

        if full_path is not None:
            if path or query or fragment:
                raise TypeError()

            # Use original URL just for parse.
            path, query, fragment = URL(full_path)[2:5]

        return URL.__new__(type(self), None,
            self[0] if scheme is None else scheme,
            self[1] if host is None else host,
            self[2] if path is None else path,
            self[3] if query is None else query,
            self[4] if fragment is None else fragment,
            self[5] if userinfo is None else userinfo,
            self[6] if port is None else port,
        )

    def setdefault(self, scheme='', host='', path='', query='', fragment='',
                   userinfo='', port=''):
        return URL.__new__(type(self), None,
            self[0] or scheme,
            self[1] or host,
            self[2] or path,
            self[3] or query,
            self[4] or fragment,
            self[5] or userinfo,
            self[6] or port,
        )

    ### Utils

    @classmethod
    def remove_dot_segments(cls, path):
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

    ### Python 2 to 3 compatibility

    import sys
    if sys.version_info > (3, 0):
        # Rename __unicode__ function to __str__ in python 3.
        __str__ = __unicode__
        del __unicode__
        # Rename __nonzero__ function to __bool__ in python 3.
        __bool__ = __nonzero__
        del __nonzero__
    else:
        # Convert unicode to bytes in python 2.
        __str__ = lambda self: self.__unicode__().encode('utf-8')
    del sys


class CachedURL(URL):
    __slots__ = ()
    _cache = {}
    _cache_size = 20

    def __new__(cls, url=None, *args, **kwargs):
        # Cache only when parsing.
        if url is None:
            return URL.__new__(cls, None, *args, **kwargs)

        self = cls._cache.get(url)

        if self is None:
            if len(cls._cache) >= cls._cache_size:
                cls._cache.clear()

            # Construct and store.
            self = URL.__new__(cls, url)
            cls._cache[url] = self

        return self

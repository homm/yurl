import re
from collections import namedtuple

# This module based on rfc3986.

# Section 3.1. Scheme
# | URI scheme specifications must define their own syntax so that
# | all strings matching their scheme-specific syntax will also match
# | the <absolute-URI> grammar:
#
# | absolute-URI  = scheme ":" hier-part [ "?" query ]
#
# As we can see, <absolute-URI> not require all scheme-specific
# syntaxis to have fragment part. But as defined in section 2.2.,
# "#" one of the generic delimiters. It also defined as delimeter
# in many parts of rfc. As a result url can not contain char "#"
# without quoting even if it scheme-specific syntax not use "#":
#
# | If data for a URI component would conflict with a reserved
# | character's purpose as a delimiter, then the conflicting data
# | must be percent-encoded before the URI is formed.
#
_split_re = re.compile(r'''
    (?:([a-z][a-z0-9+\-.]*):)?  # scheme
    (?://                       # authority
        (?:([^/?\#@\[\]]*)@)?   # userinfo
        ([^/?\#]*)()            # host:port
    )?
    ([^?\#]*)                   # path
    \??([^\#]*)                 # query
    \#?(.*)                     # fragment
    ''', re.VERBOSE | re.IGNORECASE | re.DOTALL).match

URLTuple = namedtuple('URLBase', 'scheme host path query fragment userinfo port')

class URL(URLTuple):
    __slots__ = ()

    def __new__(cls, url=None, scheme='', host='', path='', query='',
                fragment='', userinfo='', port=''):
        if url is not None:
            # All other arguments are ignored.
            (scheme, userinfo, host, port,
             path, query, fragment) = _split_re(url).groups('')

            # We can not match port number in regexp. Host itself can contain
            # digits and ":"
            _port_idx = host.rfind(':')
            if _port_idx >= 0:
                _port = host[_port_idx + 1:]
                if not _port or _port.isdigit():
                    host, port = host[:_port_idx], _port

        # | Although schemes are case-insensitive, the canonical form
        # | is lowercase. An implementation should only produce lowercase
        # | scheme names for consistency.
        scheme = scheme.lower()

        # | Although host is case-insensitive, producers and normalizers
        # | should use lowercase for registered names and hexadecimal
        # | addresses for the sake of uniformity.
        # TODO: while only using uppercase letters for percent-encodings
        host = host.lower()

        return tuple.__new__(cls, (scheme, host, path, query, fragment,
                                   userinfo, str(port)))

    def __unicode__(self):
        base = self.authority

        if base:
            base = '//' + base
            if self.path and not self.path.startswith('/'):
                base += '/'

        if self.scheme:
            base = self.scheme + ':' + base

        return base + self.full_path

    as_string = __unicode__

    def __reduce__(self):
        return type(self), (None,) + tuple(self)

    def __add__(self, other):
        if not isinstance(other, URLTuple):
            other = type(self)(other)

    @property
    def authority(self):
        authority = self.host
        if self.port:
            authority += ':' + self.port
        if self.userinfo:
            return self.userinfo + '@' + authority
        return authority

    @property
    def full_path(self):
        path = self.path
        if self.query:
            path += '?' + self.query
        if self.fragment:
            path += '#' + self.fragment
        return path

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

        return tuple.__new__(type(self), (
            self.scheme if scheme is None else scheme.lower(),
            self.host if host is None else host.lower(),
            self.path if path is None else path,
            self.query if query is None else query,
            self.fragment if fragment is None else fragment,
            self.userinfo if userinfo is None else userinfo,
            self.port if port is None else str(port),
        ))

    def replace_from(self, other):
        if not isinstance(other, URLTuple):
            other = type(self)(other)

        return tuple.__new__(type(self), (
            other.scheme or self.scheme,
            other.host or self.host,
            other.path or self.path,
            other.query or self.query,
            other.fragment or self.fragment,
            other.userinfo or self.userinfo,
            other.port or self.port,
        ))

    def setdefault(self, scheme='', host='', path='', query='', fragment='',
                   userinfo='', port=''):
        return tuple.__new__(type(self), (
            self.scheme or scheme.lower(),
            self.host or host.lower(),
            self.path or path,
            self.query or query,
            self.fragment or fragment,
            self.userinfo or userinfo,
            self.port or str(port),
        ))

    # Python 2 to 3 compatibility.
    # Rename __unicode__ function to __str__ in python 3.
    # Convert unicode to bytes in python 2.
    import sys
    if sys.version_info > (3, 0):
        __str__ = __unicode__
        del __unicode__
    else:
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

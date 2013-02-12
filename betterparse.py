import re

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
        ([^/?\#@\[\]]*@)?       # userinfo
        ([^/?\#]*)              # host
        (?::(\d*))?             # port
    )?
    ([^?\#]*)                   # path
    \??([^\#]*)                 # query
    \#?(.*)                     # fragment
    ''', re.VERBOSE | re.IGNORECASE | re.DOTALL).match

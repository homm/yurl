====================================
Alternative url manipulation library
====================================

Yurl is the replacement of built in python urlparse module.
Key features of yurl are:

* pythonic api
* better compliance with RFC 3986
* nice performance
* support for python 2.6, 2.7, 3.2, 3.3 and pypy 1.9 with single codebase

Yurl inspired by purl — pythonic interface to urlparse.

===
API
===


Parsing
-------

To parse url into parts, pass string as first argument to URL() constructor:

    >>> from yurl import URL
    >>> URL('https://www.google.ru/search?q=yurl')
    URLBase(scheme='https', host='www.google.ru', path='/search',
     query='q=yurl', fragment='', userinfo='', port='')

It also works with relative urls:

    >>> URL('search?rls=en&q=yurl&redir_esc=')
    URLBase(scheme='', host='', path='search',
     query='rls=en&q=yurl&redir_esc=', fragment='', userinfo='', port='')

URL() returns named tuple with scheme, host, path, query, fragment,
userinfo and port properties. All properties is strings, even if they does not
exists in url.

Url also can be constructed from known parts:

    >>> print URL(host='google.com', path='search', query='q=url')
    //google.com/search?q=url


Validation and information
--------------------------

Parsing is always successful, even if some parts have unescaped or
not allowed chars. After parsing you can call validate() method:

    >>> URL('//google:com').validate()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "yurl.py", line 201, in validate
        raise InvalidHost()
    yurl.InvalidHost

Validate() returns object itself or modified version:

    >>> URL('//google.com:80').validate()
    URLBase(scheme='', host='google.com', path='',
     query='', fragment='', userinfo='', port='80')

While host, userinfo and port properties sometimes not useful, url object
have property authority with these joined parts and has_authority method:

    >>> URL('http://google.com:80').authority
    'google.com:80'
    >>> URL('http://google.com:80').has_authority()
    True

Also you can check is url relative:

    >>> URL('http://google.com:80').is_relative()
    False
    >>> URL('//google.com:80').is_relative()
    True

Or have relative path:

    >>> URL('scheme:path').is_relative_path()
    False
    >>> URL('./path').is_relative_path()
    True

You can also chech is url host is ip:

    >>> URL('//127-0-0-1/').is_host_ip()
    False
    >>> URL('//127.0.0.1/').is_host_ip()
    True
    >>> URL('//[::ae21:ad12]/').is_host_ip()
    True
    >>> URL('//[::ae21:ad12]/').is_host_ipv4()
    False

Ip does not validate, so it is recomended to use validate() method:

    >>> URL('//[+ae21:ad12]/').is_host_ip()
    True
    >>> URL('//[+ae21:ad12]/').validate().is_host_ip()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "yurl.py", line 197, in validate
        raise InvalidHost()
    yurl.InvalidHost


Modify urls
-----------

Afert parsing url can be modified in different ways.

replace() method
----------------

You can use replace() method to change whole parts of url:

    >>> print URL('http://ya.ru/').replace(scheme='https')
    https://ya.ru/
    >>> print URL('http://ya.ru/?q=yurl').replace(query='')
    http://ya.ru/

In addition to the usual attributes it takes shortcuts authority and full_path:

    >>> print URL('http://user@ya.ru:80/?q=yurl')\
    ... .replace(authority='google.com', full_path='two')
    http://google.com/two

setdefault() method
-------------------

setdefault() replace parts with given if they don't exists in original url:

    >>> print URL('https://google.com').setdefault(scheme='http', path='q')
    https://google.com/q

Url join
--------

Join is analogue of urljoin() function from urlparse module. You can join two
urls by adding one to another.

    >>> print URL('http://ya.ru/path#chap2') + URL('seqrch?q=some')
    http://ya.ru/seqrch?q=some

Join for relative urls is also supported:

    >>> print URL('path/to/object#chap2') + URL('../from/object')
    path/from/object

Join is not commutative operation:

    >>> print URL('../from/object') + URL('path/to/object#chap2')
    from/path/to/object#chap2

And not associative in general:

    >>> print (URL('//google/path/to') + URL('../../object')) + URL('path')
    //google/path
    >>> print URL('//google/path/to') + (URL('../../object') + URL('path'))
    //google/path/path


Cache url parsing
-----------------

Original urlparse function cache every parsed url. In most cases this is
unnecessary. But if you parse same urls again and again you can use CachedURL:

    >>> CachedURL('http://host') is CachedURL('http://host')
    True

=============
About library
=============


Why you should use yurl instead of urlparse
-------------------------------------------

The short answer is urlparse is broken. If you're interested, here's detailed
response.

*   urlparse module have two functions: urlparse() and urlsplit(). In addition to
    urlsplit(), urlparse() separates params from path. Params is not part of
    most schemas and in last rfc is not part of url at all. Instead of this
    each path segment can have own params. The problem is that most programmers
    use urlparse() and ignore params when extract path:

    >>> import purl
    >>> print purl.URL('/path;with?semicolon')
    /path?semicolon

*   urlsplit() has strange parameters. It takes default addressing scheme.
    But scheme is only can have default value in urlsplit().

*   Another parameter allow_fragments can be used to prevent splitting
    #fragment from path. The problem is we can not say «I do not want this url
    contatin fragment». If url contatin '#', it contatin frаgment. If scheme
    can not contatin fragment, '#' still can not be used in another parts.
    Caller has a choise: it can ignore fragment or raise. But url can not be
    parsed with ignoring '#':

    >>> urlparse('/path#frag:ment?query').query
    ''
    >>> urlparse('/path#frag:ment?query', allow_fragments=False).query
    'query'

*   Module makes no difference between parsing and validating. For example
    urlsplit() check allowed chars in scheme and raise on invalid IP URL:

    >>> urlsplit('not_scheme://google.com').path
    'not_scheme://google.com'
    >>> urlsplit('//ho[st/')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/usr/lib/python2.7/urlparse.py", line 211, in urlsplit
        raise ValueError("Invalid IPv6 URL")
    ValueError: Invalid IPv6 URL

    But ignores other errors:

    >>> urlsplit('//host@with@butterflies').username
    'host@with'
    >>> urlsplit('//butterflies[]:80').port
    80

*   It don't understend my favarite scheme:

    >>> urlsplit('lucky-number:33')[:]
    ('', '', 'lucky-number:33', '', '')

*   It loses path with two slashes:

    >>> urlsplit('////path')[:]
    ('', '', '//path', '', '')
    >>> urlsplit(urlsplit('////path').geturl())[:]
    ('', 'path', '', '', '')

*   Function urljoin() broken sometimes:

    >>> urljoin('http://host/', '../')
    'http://host/../'
    >>> print URL('http://host/') + URL('../')
    http://host

I'm sure the list is not complete.


Why you should use yurl instead of purl
---------------------------------------

Purl built on top of urlparse() and include almost all problems listed above.
And some other:

*   Purl parsing is about 2 times slower then urlparse(), while yurl parsing
    is about 2 times faster then urlparse().

*   Purl manipulations is about 20 times slower then yurl:

    >>> timeit("url.scheme('https')", "import purl; url = purl.URL('http://google.com/')", number=10000)
    0.4427049160003662
    >>> timeit("url.replace(scheme='https')", "import yurl; url = yurl.URL('http://google.com/')", number=10000)
    0.020306110382080078

*   Purl have ugly jquery-like api, when one method returns different objects
    based on arguments.

*   Purl parsing is dangerous:

    >>> purl.URL('//@host')
    ValueError: need more than 1 value to unpack
    >>> purl.URL('//host:/')
    ValueError: invalid literal for int() with base 10: ''
    >>> purl.URL('//user:pa:word@host')
    ValueError: too many values to unpack

*   Purl loses path after ';'. While ';' is valid char in url:

    >>> print purl.URL('/path;with?semicolon')
    /path?semicolon

*   Purl loses host in relative urls:

    >>> print purl.URL('//google.com/path?query')
    google.com/path?query

*   Purl loses username with empty password and password with empty username:

    >>> print purl.URL('http://user:@google.com/')
    http://google.com/


Changelog
---------

v0.9
----

First release.

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
    URLBase(scheme='https', userinfo=u'', host='www.google.ru', port='',
     path='/search', query='q=yurl', fragment='', decoded=False)

It also works with relative urls:

    >>> URL('search?rls=en&q=yurl&redir_esc=')
    URLBase(scheme=u'', userinfo=u'', host=u'', port='', path='search',
     query='rls=en&q=yurl&redir_esc=', fragment='', decoded=False)

Url also can be constructed from known parts:

    >>> print URL(host='google.com', path='search', query='q=url')
    //google.com/search?q=url


Validation
----------

Url parsing is always successful, even if some parts have unescaped or
not allowed chars. After parsing you can call validate() method:

    >>> URL('//google:com').validate()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "yurl.py", line 201, in validate
        raise InvalidHost()
    yurl.InvalidHost

Validate() returns object itself or modified version:

    >>> URL('//google.com:80').validate()
    URLBase(scheme=u'', userinfo=u'', host='google.com', port='80',
     path='', query='', fragment='', decoded=False)


Get information
---------------

URL() returns named tuple with some additional properties. All properties
is strings, even if they does not exists in url.

.scheme .authority .path .query .fragment
    Basic parts of url: *scheme://authority/path?query#fragment*

.userinfo .host .port
    Parts of authority: *userinfo@host:port*
    Port is guaranteed to consist of digits.

.full_path
    Path, query and fragment joined together: *path?query#fragment*

.username .authorization
    Parts of userinfo: *username:authorization*

Url object has method for checking authority existence:

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

Ip does not validated, so it is recommended to use validate() method:

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

After parsing url can be modified in different ways.

replace() method
~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~

setdefault() replace parts with given if they don't exists in original url:

    >>> print URL('https://google.com').setdefault(scheme='http', path='q')
    https://google.com/q

Url join
~~~~~~~~

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


Decode url
----------

All chars in url is divided to three groups: delimeters, subdelimeters and
unreserved chars. Unreserved chars do not affect the parsing and can be encoded
or decoded at any time. To decode unreserved chars you can call decode()
method. Defaul encoding is utf-8.

    >>> url = '%D1%81%D1%85%D0%B5%D0%BC%D0%B0%3A%D0%BF%D1%83%D1%82%D1%8C'
    >>> print URL(url).decode()
    схема%3Aпуть

If you want decode all chars, you should apply decode_url_component()
function to url component:

    >>> from yurl import decode_url_component
    >>> print decode_url_component(URL(url).decode().path)
    схема:путь

You can also omit decode method if you pass encoding in decode_url_component():

    >>> print decode_url_component(url, 'utf-8')
    схема:путь

If you do not pass encoding, only reserved chars will be decoded:

    >>> print decode_url_component(url)
    %D1%81%D1%85%D0%B5%D0%BC%D0%B0:%D0%BF%D1%83%D1%82%D1%8C

Cache url parsing
-----------------

Original urlparse() cache every parsed url. In most cases this is unnecessary.
But if you parse the same link again and again you can use CachedURL:

    >>> CachedURL('http://host') is CachedURL('http://host')
    True

=============
About library
=============


Decisions
---------

Rfc define format of valid url and ways to interact with it. But sometimes we
need to interact invalid urls. And RFC's not much help with it. So this library
has lots of decisions.

*   Many libraries do not allow scheme or authority with invalid chars. Rfc
    unambiguously define format of this parts. So we can say 'sche_me:path'
    can not be scheme because of underscore and should be parsed as path:

    >>> urlsplit('sche_me:path')[:]
    ('', '', 'sche_me:path', '', '')

    The problem is rfc also defines that the first segment of the path can not
    contain colon. I believe the right way is to split url as is and then
    validate if necessary.

    >>> urlsplit('sche_me:path')[:]
    ('sche_me', '', 'path', '', '')

*   Rfc define two operations against url: parse and join. As long as we can
    construct url from parts and replace parts we should sometimes fix
    this parts. For example url with authority can not be relative.
    And relative url can not starts with // or contain : in first path segment.
    These fixes can be done while url constructing or while recomposition.
    First way may be wrong because we can apply unnecessary in future fix:

    >>> # This is example of wrong behavior.
    >>> print URL("//host") + URL(path="//path")
    //host////path  # now path have four slashes

    Second way is wrong when we replace some parts:

    >>> # This is example of wrong behavior.
    >>> print URL("rel/path").replace(host='host').path
    rel/path  # path is relative even if host there

    So I divide all fixes to real fixes:

    >>> # path can not be relative when host present
    >>> print URL("rel/path").replace(host='host').path
    /rel/path

    And escapes which should be applied on recomposition:

    >>> # url starts with path can not contain ':' in first path segment
    >>> print URL(path="rel:path")
    ./rel:path
    >>> print URL(path="rel:path").path
    rel:path


Why you might want to use yurl instead of urlparse
--------------------------------------------------

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
    #fragment from path. The problem is that we can't say «I do not want
    fragment in this url». If url contatin '#', it contatin frаgment. If scheme
    can not contatin fragment, '#' still can not be used in another parts.
    Caller has a choise: he can ignore fragment or raise. But url can not be
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

*   It don't understend my favorite scheme:

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


Why you might want to use yurl instead of purl
----------------------------------------------

Purl built on top of urlparse() and include almost all problems listed above.
And some other:

*   Purl parsing is about 2 times slower then urlparse(), while yurl parsing
    is about 2 times faster then urlparse().

*   Purl manipulations is about 20 times slower then yurl:

    >>> timeit("url.scheme('https')", "import purl; url = purl.URL('http://google.com/')", number=10000)
    0.4427049160003662
    >>> timeit("url.replace(scheme='https')", "import yurl; url = yurl.URL('http://google.com/')", number=10000)
    0.020306110382080078

*   Purl have ugly jquery-like api, when one method may return different
    objects depending on the arguments.

*   Purl parsing is dangerous:

    >>> purl.URL('//@host')
    ValueError: need more than 1 value to unpack
    >>> purl.URL('//host:/')
    ValueError: invalid literal for int() with base 10: ''
    >>> purl.URL('//user:pass:word@host')
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


More about performance
-----------------------

Yurl comes with bunch of performance tests. Results may vary depending on the
Python version and the CPU:

::

    $ python2.7 ./test.py -bench

    === Test as string ===
      yurl usplit uparse   purl
     12.01  9.783  11.94  27.08 !worse  https://user:info@yandex.ru:8080/path/to+the=ar?gum=ent#s
     8.533  21.89  23.82  18.88   scheme:8080/path/to;the=ar?gum=ent#s
     10.12  3.879  9.007  12.21 !worse  re/ative:path;with?query
     5.268   2.39  4.043  10.26 !worse  lucky-number:3456
     4.806  3.662  5.349  13.73 !worse  //host:80
     4.953  3.342  4.885   13.2 !worse  #frag

    === Manipulations speed ===
      noop   yurl
    0.0751  178.9   https://habrahabr.ru:80/a/b/c?d=f#h

    === Test join ===

      = result is string =
      yurl  ujoin
     111.6  127.2   u'http://ya.ru/user/photos/id12324/photo3' + u'../../../mikhail/photos/id6543/photo99?param'
     85.87  71.06 !worse  u'http://ya.ru/user/photos/id12324' + u'#fragment'
     82.12  100.8   u'http://ya.ru/' + u'https://google.com/?q=yurl'

      = result is parsed =
      yurl  ujoin
     102.6  181.3   u'http://ya.ru/user/photos/id12324/photo3' + u'../../../mikhail/photos/id6543/photo99?param'
     73.15  125.7   u'http://ya.ru/user/photos/id12324' + u'#fragment'
     76.26  184.3   u'http://ya.ru/' + u'https://google.com/?q=yurl'

    === Test parse ===

      = dupass cache =
      yurl usplit uparse   purl
     36.25  73.31  85.91  166.5   https://user:info@yandex.ru:8080/path/to+the=ar?gum=ent#s
     20.34  58.84  77.29  138.9   scheme:8080/path/to;the=ar?gum=ent#s
     18.25  33.21  48.72  109.3   re/ative:path;with?query
      19.3  66.77  76.16  135.5   lucky-number:3456
      24.0  35.57  43.36  119.2   //host:80
      18.0  25.57  37.78  114.4   #frag

      = with cache =
      yurl usplit uparse   purl
     9.902  14.43  24.04  95.92   https://user:info@yandex.ru:8080/path/to+the=ar?gum=ent#s
     5.726  7.211  23.14  79.94   scheme:8080/path/to;the=ar?gum=ent#s
     5.497  6.804  22.86  80.93   re/ative:path;with?query
     5.357  6.521  14.72   72.0   lucky-number:3456
     5.076  6.763  14.12  87.39   //host:80
     5.824  7.993  26.78  73.03   #frag

In tests where any of the other libraries beats yurl you can see "!worse"
marker.


Changelog
---------

v0.12
~~~~~

* added URLError exception on top of ValueError

v0.11
~~~~~

* decode() method
* username and authorization properties
* order of tuple members now same as url parts:
  scheme, userinfo, host, port, path, query, fragment
* raw url parsing was moved to split_url() function of utils module

v0.10
~~~~~

* method replace_from() removed
* concatenation with string no longer aliasd with join
* join always remove dots segments (as defined in rfc)

v0.9
~~~~

First release.

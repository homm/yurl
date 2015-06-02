# coding: utf-8

from __future__ import print_function, unicode_literals
import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from yurl import (URL, InvalidScheme as Scheme, InvalidUserinfo as Userinfo,
                  InvalidHost as Host, InvalidPath as Path,
                  InvalidQuery as Query, decode_url, decode_url_component)


class ParseTests(unittest.TestCase):
    def setUp(self):
        try:
            from urllib.parse import urlsplit
        except ImportError:
            from urlparse import urlsplit
        self.split = urlsplit

    def one_try(self, url, scheme='', host='', path='', query='', fragment='',
                userinfo='', port='', invalid=None, urlsplit=True):
        orih_url = url
        url = URL(url)
        splitted = (scheme, userinfo, host, port, path, query, fragment)
        self.assertEqual(url._data, splitted)
        self.assertEqual(URL(None, *splitted)._data, splitted)
        self.assertEqual(URL(None, *url._data)._data, splitted)

        if invalid:
            self.assertRaises(invalid, url.validate)
        else:
            url.validate()

        if urlsplit and '-v' in sys.argv:
            splitted = (scheme, url.authority, path, query, fragment)
            split_result = self.split(orih_url)
            if split_result != splitted:
                print('\n  urllib issue:', orih_url, self.split(orih_url))
            elif (split_result.hostname or '') != host:
                print('\n  urllib issue:', orih_url, 'host is:',
                      split_result.hostname, 'host should:', host)

    def test_scheme(self):
        self.one_try('scheme:path', 'scheme', '', 'path')
        self.one_try('scheme:path:other', 'scheme', '', 'path:other')
        self.one_try('allow+chars-33.:path', 'allow+chars-33.', '', 'path')
        self.one_try('simple:', 'simple', '', '')
        self.one_try('google.com:80', 'google.com', '', '80')
        self.one_try('google.com:80/root', 'google.com', '', '80/root')
        self.one_try('not_cheme:path', 'not_cheme', '', 'path', invalid=Scheme)
        self.one_try('37signals:book', '37signals', '', 'book', invalid=Scheme)
        self.one_try(':relative-path', '', '', ':relative-path')
        self.one_try(':relative/path', '', '', ':relative/path')
        self.one_try('://and-this', '', '', '://and-this')

    def test_host(self):
        self.one_try('scheme://host/path', 'scheme', 'host', '/path')
        self.one_try('//host/path', '', 'host', '/path')
        self.one_try('//host+path', '', 'host+path', '')
        self.one_try('//host', '', 'host', '')
        self.one_try('//this+is$also&host!', '', 'this+is$also&host!', '')
        self.one_try('scheme:/host/path', 'scheme', '', '/host/path')
        self.one_try('scheme:///host/path', 'scheme', '', '/host/path')
        self.one_try('scheme//host/path', '', '', 'scheme//host/path')
        self.one_try('//127.0.0.1/', '', '127.0.0.1', '/')
        self.one_try('//[127.0.0.1]/', '', '[127.0.0.1]', '/')
        self.one_try('//[::1]/', '', '[::1]', '/')
        self.one_try('//[-1]/', '', '[-1]', '/', invalid=Host)
        self.one_try('//[v1.-1]/', '', '[v1.-1]', '/')
        self.one_try('//v1.[::1]/', '', 'v1.[::1]', '/', invalid=Host)

    def test_port(self):
        self.one_try('//host:80/path', '', 'host', '/path', port='80')
        self.one_try('//host:80', '', 'host', port='80')
        self.one_try('//:80', port='80')
        self.one_try('//h:22:80/', '', 'h:22', '/', port='80', invalid=Host)
        self.one_try('//h:no/path', '', 'h:no', '/path', invalid=Host)
        self.one_try('//h:22:no/path', '', 'h:22:no', '/path', invalid=Host)
        self.one_try('//h:-80/path', '', 'h:-80', '/path', invalid=Host)

    def test_userinfo(self):
        self.one_try('sch://user@host/', 'sch', 'host', '/', '', '', 'user')
        self.one_try('//user:pas@', userinfo='user:pas')
        self.one_try('//user:pas:and:more@', userinfo='user:pas:and:more')
        self.one_try('//:user:@', userinfo=':user:')
        self.one_try("//!($&')*+,;=@", userinfo="!($&')*+,;=")
        self.one_try('//user@info@ya.ru', '', 'info@ya.ru', userinfo='user',
                     invalid=Host)
        self.one_try('//[some]@host', '', 'host', userinfo='[some]',
                     invalid=Userinfo)

    @unittest.skip('not ready')
    def test_path(self):
        pass

    def test_query(self):
        self.one_try('?query', '', '', '', 'query')
        self.one_try('http:?query', 'http', '', '', 'query')
        self.one_try('//host?query', '', 'host', '', 'query')
        self.one_try('//host/path?query', '', 'host', '/path', 'query')
        self.one_try('//ho?st/path?query', '', 'ho', '', 'st/path?query')
        self.one_try('?a://b:c@d.e/f?g#h', '', '', '', 'a://b:c@d.e/f?g', 'h')
        self.one_try('#?query', '', '', '', '', '?query')

    def test_fragment(self):
        self.one_try('#frag', '', '', '', '', 'frag')
        self.one_try('http:#frag', 'http', '', '', '', 'frag')
        self.one_try('//host#frag', '', 'host', '', '', 'frag')
        self.one_try('//host/path#frag', '', 'host', '/path', '', 'frag')
        self.one_try('//host?query#frag', '', 'host', '', 'query', 'frag')
        self.one_try('//ho#st/path?query', '', 'ho', '', '', 'st/path?query')
        self.one_try('#a://b:c@d.e/f?g#h', '', '', '', '', 'a://b:c@d.e/f?g#h')

    def test_case_sensitivity(self):
        self.one_try('A://B:C@D.E/F?G#H', 'a', 'd.e', '/F', 'G', 'H', 'B:C',
                     urlsplit=False)

    def test_strip_empty_parts(self):
        self.one_try('//@:?#')
        self.one_try('///path', '', '', '/path')
        self.one_try('//@host', '', 'host')
        self.one_try('//host:', '', 'host')
        self.one_try('//host:/', '', 'host', '/')
        self.one_try('/', '', '', '/')
        self.one_try('path', '', '', 'path')
        self.one_try('/path', '', '', '/path')
        self.one_try('/path?', '', '', '/path')
        self.one_try('?')
        self.one_try('?#frag', fragment='frag')
        self.one_try('/path#', '', '', '/path')
        self.one_try('#')


class InterfaceTests(unittest.TestCase):
    def test_constructor(self):
        # args
        self.assertEqual(URL('a://b:c@d:5/f?g#h'),
                         URL(None, 'a', 'b:c', 'd', '5', '/f', 'g', 'h'))
        # kwargs
        self.assertEqual(URL('a://b:c@d:5/f?g#h'),
                         URL(scheme='a', userinfo='b:c', host='d', port='5',
                             path='/f', query='g', fragment='h'))
        # ignore
        self.assertEqual(URL('//host'), URL('//host', scheme='sh', port='80'))

    def test_fixes(self):
        # port convert
        self.assertEqual(URL(port=80), URL(port='80'))
        self.assertEqual(URL().replace(port=80), URL(port='80'))
        self.assertEqual(URL().setdefault(port=80), URL(port='80'))

        # scheme lowercase
        self.assertEqual(URL(None, 'SCHEME'), URL(None, 'scheme'))
        self.assertEqual(URL().replace('SCHEME'), URL(None, 'scheme'))
        self.assertEqual(URL().setdefault('SCHEME'), URL(None, 'scheme'))

        # host lowercase
        self.assertEqual(URL(None, host='HOST'), URL(None, host='host'))
        self.assertEqual(URL().replace(host='HOST'), URL(None, host='host'))
        self.assertEqual(URL().setdefault(host='HOST'), URL(None, host='host'))

        # relative path without host
        self.assertEqual(URL(path='rel').path, 'rel')
        self.assertEqual(URL().replace(path='rel').path, 'rel')
        self.assertEqual(URL().setdefault(path='rel').path, 'rel')

        # relative path with host
        self.assertEqual(URL(host='host', path='rel').path, '/rel')
        self.assertEqual(URL().replace(host='host', path='rel').path, '/rel')
        self.assertEqual(URL(host='host').replace(path='rel').path, '/rel')
        self.assertEqual(URL(path='rel').replace(host='host').path, '/rel')
        self.assertEqual(URL().setdefault(host='ho', path='rel').path, '/rel')
        self.assertEqual(URL(host='ho').setdefault(path='rel').path, '/rel')
        self.assertEqual(URL(path='rel').setdefault(host='ho').path, '/rel')

        # relative path without ':' in first segment
        self.assertEqual(URL(path='rel/at:ve').path, 'rel/at:ve')
        self.assertEqual(str(URL(path='rel/at:ve')), 'rel/at:ve')
        self.assertEqual(str(URL().replace(path='rel/at:ve')), 'rel/at:ve')
        self.assertEqual(str(URL().setdefault(path='rel/at:ve')), 'rel/at:ve')

        # relative path with ':' in first segment
        self.assertEqual(URL(path='re:at').path, 're:at')
        self.assertEqual(URL(path='re:at/ve').path, 're:at/ve')
        self.assertEqual(URL().replace(path='re:at').path, 're:at')
        self.assertEqual(URL().setdefault(path='re:at').path, 're:at')
        self.assertEqual(str(URL(path='re:at')), './re:at')
        self.assertEqual(str(URL(path='re:at/ve')), './re:at/ve')
        self.assertEqual(str(URL().replace(path='re:at')), './re:at')
        self.assertEqual(str(URL().setdefault(path='re:at')), './re:at')

        # relative path with ':' in first segment and host or scheme
        self.assertEqual(URL(None, 'sc', path='re:at').path, 're:at')
        self.assertEqual(URL(None, 'sc').replace(path='re:at').path, 're:at')
        self.assertEqual(str(URL(path='re:at').replace('sc')), 'sc:re:at')
        self.assertEqual(str(URL(None, 'sc') + URL(path='re:at')), 'sc:re:at')
        self.assertEqual(URL(None, host='ho', path='re:at').path, '/re:at')
        self.assertEqual(URL(None, host='ho').replace(path='re:at').path, '/re:at')
        self.assertEqual(str(URL(path='re:at').replace(host='ho')), '//ho/re:at')
        self.assertEqual(str(URL(None, host='ho') + URL(path='re:at')), '//ho/re:at')

    def test_unicode(self):
        url = (URL('http://пользователь@домен.ком/путь?запрос#фрагмент')
               .replace(path='другой', fragment='третий'))
        # Convert to string.
        '{0}{1}{2}'.format(url.authority, url.full_path, url)

    def test_add(self):
        def test(base, rel, res):
            self.assertEqual(str(URL(base) + URL(rel)), res)
            self.assertEqual(URL(base) + URL(rel), URL(res))

        # Tests from rfc "Normal Exaples"
        for args in [("g:h", "g:h"),
                     ("g", "http://a/b/c/g"),
                     ("./g", "http://a/b/c/g"),
                     ("g/", "http://a/b/c/g/"),
                     ("/g", "http://a/g"),
                     ("//g", "http://g"),
                     ("?y", "http://a/b/c/d;p?y"),
                     ("g?y", "http://a/b/c/g?y"),
                     ("#s", "http://a/b/c/d;p?q#s"),
                     ("g#s", "http://a/b/c/g#s"),
                     ("g?y#s", "http://a/b/c/g?y#s"),
                     (";x", "http://a/b/c/;x"),
                     ("g;x", "http://a/b/c/g;x"),
                     ("g;x?y#s", "http://a/b/c/g;x?y#s"),
                     ("", "http://a/b/c/d;p?q"),
                     (".", "http://a/b/c/"),
                     ("./", "http://a/b/c/"),
                     ("..", "http://a/b/"),
                     ("../", "http://a/b/"),
                     ("../g", "http://a/b/g"),
                     ("../..", "http://a/"),
                     ("../../", "http://a/"),
                     ("../../g", "http://a/g")]:
            test('http://a/b/c/d;p?q', *args)
        # Tests from rfc "Abnormal Examples"
        for args in [("../../../g", "http://a/g"),
                     ("../../../../g", "http://a/g"),
                     ("/./g", "http://a/g"),
                     ("/../g", "http://a/g"),
                     ("g.", "http://a/b/c/g."),
                     (".g", "http://a/b/c/.g"),
                     ("g..", "http://a/b/c/g.."),
                     ("..g", "http://a/b/c/..g"),
                     ("./../g", "http://a/b/g"),
                     ("./g/.", "http://a/b/c/g/"),
                     ("g/./h", "http://a/b/c/g/h"),
                     ("g/../h", "http://a/b/c/h"),
                     ("g;x=1/./y", "http://a/b/c/g;x=1/y"),
                     ("g;x=1/../y", "http://a/b/c/y"),
                     ("g?y/./x", "http://a/b/c/g?y/./x"),
                     ("g?y/../x", "http://a/b/c/g?y/../x"),
                     ("g#s/./x", "http://a/b/c/g#s/./x"),
                     ("g#s/../x", "http://a/b/c/g#s/../x"),
                     ("http:g", "http:g")]:
            test('http://a/b/c/d;p?q', *args)

    def test_hashable(self):
        for url in [URL(), URL('a://b:c@d:5/f?g#h')]:
            hash(url)
            # assertEqual lies
            self.assertTrue(url == tuple(url))
            self.assertEqual(hash(url), hash(tuple(url)))

    def test_pickling(self):
        import pickle
        dump = pickle.dumps(URL('a://b:c@d:5/f?g#h'))
        self.assertEqual(pickle.loads(dump), URL('a://b:c@d:5/f?g#h'))

        global _test_picklingURL
        class _test_picklingURL(URL):
            def __new__(cls, path):
                return super(_test_picklingURL, cls).__new__(cls, path)

        url = _test_picklingURL('a://b:c@d:5/f?g#h')
        self.assertEqual(pickle.loads(pickle.dumps(url)), url)
        self.assertEqual(type(pickle.loads(pickle.dumps(url))), type(url))

    def test_authority(self):
        for url in ['', 'ya.ru', 'ya.ru:80', ':80', 'info@ya.ru',
                    'info@', 'info@:80']:
            self.assertEqual(URL('//' + url).authority, url)

    def test_full_path(self):
        for url in ['', 'path', 'path?query', 'path#fragment',
                    'path?query#fragment', '?query', '#fragment',
                    '?query#fragment']:
            self.assertEqual(URL(url).full_path, url)

    def test_username_and_authorization(self):
        for userinfo, un, az in [('user', 'user', ''),
                                 ('user:', 'user', ''),
                                 ('user:pass', 'user', 'pass'),
                                 ('user:pass:buzz', 'user', 'pass:buzz'),
                                 (':pass', '', 'pass'),
                                 (':pass:buzz', '', 'pass:buzz'),
                                 ('', '', ''), (':', '', ''), ('::', '', ':')]:
            self.assertEqual(URL(userinfo=userinfo).username, un)
            self.assertEqual(URL(userinfo=userinfo).authorization, az)

    def test_str(self):
        for url in ['', '//host', '//host/' 'scheme://host', '//host/path',
                    '?query', 'path?query', 'http:', 'http:?query',
                    '//host?query']:
            self.assertEqual(str(URL(url)), url)
            self.assertEqual(URL(str(URL(url))), URL(url))
        # should append slash to path
        self.assertEqual(str(URL(host='host', path='path')), '//host/path')
        self.assertEqual(str(URL(host='host', path='//path')), '//host//path')
        self.assertEqual(str(URL(path='//path').validate()), '////path')
        self.assertEqual(str(URL(path='//pa:th').validate()), '////pa:th')
        self.assertEqual(str(URL(path='pa:th').validate()), './pa:th')
        self.assertEqual(str(URL(path='not/pa:th').validate()), 'not/pa:th')
        self.assertEqual(str(URL(path='pa:th/not').validate()), './pa:th/not')

    def test_replace(self):
        for url in [URL('htttp://user@google.com:8080/path?query#fragment'),
                    URL(), URL('path'), URL('//host:80')]:
            self.assertFalse(url is url.replace(host='strange'))
            self.assertEqual(url, url.replace())
            for idx, (field, value) in enumerate(zip(url._fields, url._data)):
                # replase to same
                self.assertEqual(url.replace(**{field: value}), url)
                # clear
                self.assertEqual(url.replace(**{field: ''})[idx], '')
                # replace to some
                if url.has_authority() and field == 'path':
                    self.assertEqual(url.replace(**{field: 'an'})[idx], '/an')
                else:
                    self.assertEqual(url.replace(**{field: 'an'})[idx], 'an')

        for url, authority in [(URL('a://b:c@d:5/f?g#h'), 'blah'),
                               (URL('a://blah/f?g#h'), '')]:
            orig_autho = url.authority
            url = url.replace(authority=authority)
            self.assertEqual(url.authority, authority)
            url = url.replace(authority=orig_autho)
            self.assertEqual(url.authority, orig_autho)

        for url, full_path in [(URL('a://b:c@d:5/f?g#h'), ''),
                               (URL('a://b:c@d:5/f?g#h'), '/path'),
                               (URL('a://b:c@d:5/f?g#h'), '/path?qr'),
                               (URL('a://b:c@d:5/f?g#h'), '?qr'),
                               (URL('a://b:c@d:5/f?g#h'), '?qr#fr'),
                               (URL('a://b:c@d:5/f?g#h'), '#fr'),
                               (URL('a://b:c@d:5'), '/path')]:
            orig_path = url.full_path
            url = url.replace(full_path=full_path)
            self.assertEqual(url.full_path, full_path)
            url = url.replace(full_path=orig_path)
            self.assertEqual(url.full_path, orig_path)

        # cannot combine full_path with its components
        url = URL('a://b')
        for component in ['path', 'query', 'fragment']:
            kwargs = {component: 'other'}
            self.assertRaises(TypeError, url.replace, full_path='c?d#e', 
                              **kwargs)

        # the above check applies to the empty string
        self.assertRaises(TypeError, url.replace, full_path='c?d#e',
                          fragment='')

    def test_setdefault(self):
        empty = URL()
        full1 = URL('scheme://user@host:80/path?query#frgment')
        full2 = URL('an://oth@er:33/full?url#!!')

        self.assertEqual(empty.setdefault(*full1._data), full1)
        self.assertEqual(full1.setdefault(*full2._data), full1)

        for idx, (field, value) in enumerate(zip(full1._fields, full1._data)):
            self.assertEqual(empty.setdefault(**{field: value}),
                             empty.replace(**{field: value}))
            self.assertEqual(empty.setdefault(**{field: value})[idx], value)
            self.assertEqual(full2.setdefault(**{field: value})[idx],
                             full2[idx])

    def test_test(self):
        def test_valid(url, relative, relative_path):
            self.assertEqual(URL(url).is_relative(), relative)
            self.assertEqual(URL(url).is_relative_path(), relative_path)
        test_valid('sc:', False, False)
        test_valid('sc:path/', False, False)
        test_valid('//host', True, False)
        test_valid('/path', True, False)
        test_valid('path/', True, True)
        test_valid('./path/', True, True)
        test_valid('?true', True, True)

        def test_ip(url, host_ip, host_ipv4):
            self.assertEqual(URL(url).is_host_ip(), host_ip)
            self.assertEqual(URL(url).is_host_ipv4(), host_ipv4)
        test_ip('', False, False)
        test_ip('//google/', False, False)
        test_ip('//127.0.1', False, False)
        test_ip('//127.0.0.1', True, True)
        test_ip('//[127.0.0.1]', True, False)

        self.assertTrue(URL('/url'))
        self.assertTrue(URL('url:'))
        self.assertTrue(URL('//url'))
        self.assertTrue(URL('?url'))
        self.assertTrue(URL('#url'))
        self.assertFalse(URL('//@:?#'))

    def test_decode(self):
        for enc, dec in [('http://%D0%BF%D1%8C%D0%B5%D1%80@local.com/'
                          '%D0%B7%D0%B0%D0%BF%D0%B8%D1%81%D0%B8',
                          'http://пьер@local.com/записи'),
                         ('/%2525', '/%25')]:
            self.assertEqual(URL(enc).decode()._data, URL(dec)._data)
            self.assertEqual(URL(enc).decode().as_string(), dec)
            self.assertEqual(URL(enc).decode().decode().as_string(), dec)

    def test_stress_authority(self):
        # Authority is most ambiguous part of url. Invalid host can contatin
        # ':' and '@' (path for example can not contain '?'. And query
        # can not contain '#'). The host '//no:99:' will be parsed as 'no:99'
        # and in next recomposition it can be written as '//no:99'. But parsing
        # of '//no:99:' and '//no:99' will be different.

        # # case generation:
        # from re import sub
        # from itertools import permutations
        # cases = set(sub('\d+', '7', ''.join(case))
        #             for case in set(permutations('::@@77777')))

        cases = """7:7:7@7@ 7:7:7@7@7 7:7:7@@ 7:7:7@@7 7:7:@7@ 7:7:@7@7 7:7:@@
            7:7:@@7 7:7@7:7@ 7:7@7:7@7 7:7@7:@ 7:7@7:@7 7:7@7@7: 7:7@7@7:7
            7:7@7@: 7:7@7@:7 7:7@:7@ 7:7@:7@7 7:7@:@ 7:7@:@7 7:7@@7: 7:7@@7:7
            7:7@@: 7:7@@:7 7::7@7@ 7::7@7@7 7::7@@ 7::7@@7 7::@7@ 7::@7@7 7::@@
            7::@@7 7:@7:7@ 7:@7:7@7 7:@7:@ 7:@7:@7 7:@7@7: 7:@7@7:7 7:@7@:
            7:@7@:7 7:@:7@ 7:@:7@7 7:@:@ 7:@:@7 7:@@7: 7:@@7:7 7:@@: 7:@@:7
            7@7:7:7@ 7@7:7:7@7 7@7:7:@ 7@7:7:@7 7@7:7@7: 7@7:7@7:7 7@7:7@:
            7@7:7@:7 7@7::7@ 7@7::7@7 7@7::@ 7@7::@7 7@7:@7: 7@7:@7:7 7@7:@:
            7@7:@:7 7@7@7:7: 7@7@7:7:7 7@7@7:: 7@7@7::7 7@7@:7: 7@7@:7:7 7@7@::
            7@7@::7 7@:7:7@ 7@:7:7@7 7@:7:@ 7@:7:@7 7@:7@7: 7@:7@7:7 7@:7@:
            7@:7@:7 7@::7@ 7@::7@7 7@::@ 7@::@7 7@:@7: 7@:@7:7 7@:@: 7@:@:7
            7@@7:7: 7@@7:7:7 7@@7:: 7@@7::7 7@@:7: 7@@:7:7 7@@:: 7@@::7 :7:7@7@
            :7:7@7@7 :7:7@@ :7:7@@7 :7:@7@ :7:@7@7 :7:@@ :7:@@7 :7@7:7@
            :7@7:7@7 :7@7:@ :7@7:@7 :7@7@7: :7@7@7:7 :7@7@: :7@7@:7 :7@:7@
            :7@:7@7 :7@:@ :7@:@7 :7@@7: :7@@7:7 :7@@: :7@@:7 ::7@7@ ::7@7@7
            ::7@@ ::7@@7 ::@7@ ::@7@7 ::@@7 :@7:7@ :@7:7@7 :@7:@ :@7:@7 :@7@7:
            :@7@7:7 :@7@: :@7@:7 :@:7@ :@:7@7 :@:@7 :@@7: :@@7:7 :@@:7 @7:7:7@
            @7:7:7@7 @7:7:@ @7:7:@7 @7:7@7: @7:7@7:7 @7:7@: @7:7@:7 @7::7@
            @7::7@7 @7::@ @7::@7 @7:@7: @7:@7:7 @7:@: @7:@:7 @7@7:7: @7@7:7:7
            @7@7:: @7@7::7 @7@:7: @7@:7:7 @7@:: @7@::7 @:7:7@ @:7:7@7 @:7:@
            @:7:@7 @:7@7: @:7@7:7 @:7@: @:7@:7 @::7@ @::7@7 @::@7 @:@7: @:@7:7
            @:@:7 @@7:7: @@7:7:7 @@7:: @@7::7 @@:7: @@:7:7 @@::7""".split()

        for case in cases:
            url = URL('//' + case)
            # check is all parts defined in original url is defined in parsed
            self.assertEqual(url, URL(url.as_string()))
            self.assertEqual(url, URL('//' + url.authority))


class UtilsTests(unittest.TestCase):
    def test_decode_url_component(self):
        for src, dst in [('какая-то строка', 'какая-то строка'),
                         ('sch%3a%2f%2fhst%2fph%3bpr', 'sch://hst/ph;pr'),
                         ('%a%2%2fhst%2fph%3b', '%a%2/hst/ph;'),
                         ('%3a%3', ':%3'), ('%3a', ':'),
                         ('%20', '%20'), ('%e2%8c%98', '%e2%8c%98')]:
            self.assertEqual(decode_url_component(src), dst)

    def test_decode_url(self):
        for src, dst in [('какая-то строка', 'какая-то строка'),
                         ('%D1%85%D0%B0%D0%B1%D1%80', 'хабр'),
                         ('sch%3a%2f%2fhst%2fph', 'sch%3a%2f%2fhst%2fph'),
                         ('%25%25', '%%'), ('%25%2', '%%2'), ('%25%', '%%'),
                         ('%2%25', '%2%'), ('%%25', '%%')]:
            self.assertEqual(decode_url(src), dst)
        self.assertEqual(decode_url('%f5%e0%e1%f0ахабр', 'windows-1251'),
                         'хабрахабр')


@unittest.skipUnless('-bench' in sys.argv, "run with -bench arg")
class BenchmarkTests(unittest.TestCase):
    test_urls = ['https://user:info@yandex.ru:8080/path/to+the=ar?gum=ent#s',
                 'scheme:8080/path/to;the=ar?gum=ent#s',
                 're/ative:path;with?query',
                 'lucky-number:3456',
                 '//host:80',
                 '#frag']

    def setUp(self):
        from timeit import repeat
        setup0 = 'from yurl import URL, CachedURL\n'
        try:
            import urllib.parse
            setup0 += 'from urllib.parse import urlparse, urlsplit, urljoin\n'
        except ImportError:
            setup0 += 'from urlparse import urlparse, urlsplit, urljoin\n'

        try:
            import purl
            setup0 += 'import purl\n'
            self.use_purl = True
        except (ImportError, SyntaxError):
            self.use_purl = False

        self.test = lambda stmt, setup='': min(repeat(stmt, setup0 + setup,
                                                      number=5000))

    def one_try(self, url, setup, *tests):
        results = [self.test(test, setup) * 1000 for test in tests]

        print(end=' ', *['{0:6.4}'.format(result) for result in results])
        if results[0] > min(results[1:]):
            print('!worse', end='')
        print(' ', url)

    def test_parse(self):
        print('\n=== Test parse ===')

        print('\n  = dupass cache =')
        if self.use_purl:
            print('  yurl usplit uparse   purl')
        else:
            print('  yurl usplit uparse')
        for url in self.test_urls:
            setup = "i = 0; url = {0}".format(repr(url))
            tests = ["URL(url + str(i)); i+=1",
                     "urlsplit(url + str(i)); i+=1",
                     "urlparse(url + str(i)); i+=1"]
            if self.use_purl:
                tests.append("purl.URL(url + str(i)); i+=1")
            self.one_try(url, setup, *tests)

        print('\n  = with cache =')
        if self.use_purl:
            print('  yurl usplit uparse   purl')
        else:
            print('  yurl usplit uparse')
        for url in self.test_urls:
            setup = "i = 0; url = {0}".format(repr(url))
            tests = ["CachedURL(url + str(i % 20)); i+=1",
                     "urlsplit(url + str(i % 20)); i+=1",
                     "urlparse(url + str(i % 20)); i+=1"]
            if self.use_purl:
                tests.append("purl.URL(url + str(i % 20)); i+=1")
            self.one_try(url, setup, *tests)

    def test_concat(self):
        print('\n=== Test as string ===')
        if self.use_purl:
            print('  yurl usplit uparse   purl')
        else:
            print('  yurl usplit uparse')

        setup = ("yurl = URL({0})\n"
                 "splitted = urlsplit({0})\n"
                 "parsed = urlparse({0})\n")
        if self.use_purl:
            setup += "purl = purl.URL({0})\n"
        for url in self.test_urls:
            tests = ["yurl.as_string()",
                     "splitted.geturl()",
                     "parsed.geturl()"]
            if self.use_purl:
                tests.append("purl.as_string()")
            self.one_try(url, setup.format(repr(url)), *tests)

    def test_join(self):
        join_cases = [('http://ya.ru/user/photos/id12324/photo3',
                       '../../../mikhail/photos/id6543/photo99?param'),
                      ('http://ya.ru/user/photos/id12324', '#fragment'),
                      ('http://ya.ru/', 'https://google.com/?q=yurl')]

        print('\n=== Test join ===')

        print('\n  = result is string =')
        print('  yurl  ujoin')
        for base, rel in join_cases:
            setup = "i = 0; base = {0}; rel = {1}".format(repr(base), repr(rel))
            self.one_try('{0} + {1}'.format(repr(base), repr(rel)), setup,
                         "(CachedURL(base) + URL(rel + str(i))).as_string(); i+=1",
                         "urljoin(base, rel + str(i)); i+=1")

        print('\n  = result is parsed =')
        print('  yurl  ujoin')
        for base, rel in join_cases:
            setup = "i = 0; base = {0}; rel = {1}".format(repr(base), repr(rel))
            self.one_try('{0} + {1}'.format(repr(base), repr(rel)), setup,
                         "CachedURL(base) + URL(rel + str(i)); i+=1",
                         "urlparse(urljoin(base, rel + str(i))); i+=1")

    def test_heavy(self):
        print('\n=== Manipulations speed ===')
        print('  noop   yurl')
        for url in ['https://habrahabr.ru:80/a/b/c?d=f#h']:
            setup = "url = URL({0})".format(repr(url))
            self.one_try(url, setup, "pass",
                         "(url.validate()"
                         " .setdefault(userinfo='homm')"
                         " .replace(authority='ya.ru')"
                         "  + URL('../../f'))"
                         ".validate().as_string()")


if __name__ == '__main__':
    if '-bench' in sys.argv:
        sys.argv.remove('-bench')
    unittest.main()

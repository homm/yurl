# coding: utf-8

from __future__ import print_function, unicode_literals
import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from yurl import (URL, InvalidScheme as Scheme, InvalidUserinfo as Userinfo,
                  InvalidHost as Host, InvalidPath as Path,
                  InvalidQuery as Query)


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
        splitted = (scheme, host, path, query, fragment, userinfo, port)
        self.assertEqual(url, splitted)
        self.assertEqual(URL(None, *splitted), splitted)
        self.assertEqual(URL(None, *url), splitted)

        if invalid:
            self.assertRaises(invalid, url.validate)
        else:
            url.validate()

        if urlsplit and '-v' in sys.argv:
            splitted = (scheme, url.authority, path, query, fragment)
            if self.split(orih_url) != splitted:
                print('\n  urllib issue:', orih_url, self.split(orih_url))

    def test_scheme(self):
        self.one_try('scheme:path', 'scheme', '', 'path')
        self.one_try('scheme:path:other', 'scheme', '', 'path:other')
        self.one_try('allow+chars-33.:path', 'allow+chars-33.', '', 'path')
        self.one_try('simple:', 'simple', '', '')
        self.one_try('google.com:80', 'google.com', '', '80')
        self.one_try('google.com:80/root', 'google.com', '', '80/root')
        self.one_try('not_cheme:path', 'not_cheme', '', 'path', invalid=Scheme)
        self.one_try('37signals:book', '37signals', '', 'book', invalid=Scheme)
        self.one_try(':realy-path', '', '', ':realy-path')
        self.one_try('://even-this', '', '', '://even-this')

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
        self.one_try('//@:?#', urlsplit=False)
        self.one_try('///path', '', '', '/path')
        self.one_try('//@host', '', 'host', urlsplit=False)
        self.one_try('//host:', '', 'host', urlsplit=False)
        self.one_try('//host:/', '', 'host', '/', urlsplit=False)
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
                         URL(None, 'a', 'd', '/f', 'g', 'h', 'b:c', '5'))
        # kwargs
        self.assertEqual(URL('a://b:c@d:5/f?g#h'),
                         URL(scheme='a', userinfo='b:c', host='d', port='5',
                             path='/f', query='g', fragment='h'))
        # ignore
        self.assertEqual(URL('//host'), URL('//host', scheme='sh', port='80'))
        # port convert
        self.assertEqual(URL(port=80), URL(port='80'))
        self.assertEqual(URL(None, 'SCHEME', 'HOST'),
                         URL(None, 'scheme', 'host'))

    def test_unicode(self):
        url = (URL('http://пользователь@домен.ком/путь?запрос#фрагмент')
               .replace(path='другой', fragment='третий'))
        # Convert to string.
        '{0}{1}{2}'.format(url.authority, url.full_path, url)

    @unittest.skip('not implemented')
    def test_add(self):
        self.assertEqual(URL('http://google.com/docs') + '/search?q=WAT',
                         URL('http://google.com/search?q=WAT'))
        self.assertEqual(URL('http://google.com/docs') + URL('/search?q=WAT'),
                         URL('http://google.com/search?q=WAT'))

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

    def test_authority(self):
        for url in ['', 'ya.ru', 'ya.ru:80', ':80', 'info@ya.ru',
                    'info@', 'info@:80']:
            self.assertEqual(URL('//' + url).authority, url)

    def test_full_path(self):
        for url in ['', 'path', 'path?query', 'path#fragment',
                    'path?query#fragment', '?query', '#fragment',
                    '?query#fragment']:
            self.assertEqual(URL(url).full_path, url)

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
                    URL(), URL('path'), URL('//host').replace(port=80)]:
            self.assertFalse(url is url.replace(host='strange'))
            self.assertEqual(url, url.replace())
            for idx, (field, value) in enumerate(zip(url._fields, url)):
                # replase to same
                self.assertEqual(url.replace(**{field: value}), url)
                # replace to some
                self.assertEqual(url.replace(**{field: 'some'})[idx], 'some')
                # clear
                self.assertEqual(url.replace(**{field: ''})[idx], '')

        self.assertEqual(
            URL().replace('SCHEME', 'HOST', '/PATH', '', '', 'AUTH', 30),
            ('scheme', 'host', '/PATH', '', '', 'AUTH', '30')
        )

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

    def test_replace_from(self):
        full_url = URL('scheme://user@host:80/path?query#frgment')
        for url in ['an://oth@er:33/full?url#!!', '/simple/path', 'scm:']:
            self.assertEqual(URL(url).replace_from(full_url), full_url)

        self.assertEqual(full_url.replace_from(URL('scm:')).scheme, 'scm')
        self.assertEqual(full_url.replace_from(URL('//hst')).host, 'hst')
        self.assertEqual(full_url.replace_from(URL('/pth')).path, '/pth')

    def test_setdefault(self):
        empty = URL()
        full1 = URL('scheme://user@host:80/path?query#frgment')
        full2 = URL('an://oth@er:33/full?url#!!')

        self.assertEqual(empty.setdefault(*full1), full1)
        self.assertEqual(full1.setdefault(*full2), full1)

        for idx, (field, value) in enumerate(zip(full1._fields, full1)):
            self.assertEqual(empty.setdefault(**{field: value}),
                             empty.replace(**{field: value}))
            self.assertEqual(empty.setdefault(**{field: value})[idx], value)
            self.assertEqual(full2.setdefault(**{field: value})[idx],
                             full2[idx])

    def test_test(self):
        def test(url, relative, relative_path):
            self.assertEqual(URL(url).is_relative(), relative)
            self.assertEqual(URL(url).is_relative_path(), relative_path)
        test('sc:', False, False)
        test('sc:path/', False, False)
        test('//host', True, False)
        test('/path', True, False)
        test('path/', True, True)
        test('./path/', True, True)


@unittest.skipUnless('-bench' in sys.argv, "run with -bench arg")
class BenchmarkTests(unittest.TestCase):
    test_urls = ['https://user:info@yandex.ru:8080/path/to+the=ar?gum=ent#s',
                 'scheme:8080/path/to;the=ar?gum=ent#s',
                 'lucky-number:3456',
                 '//host:80']

    def setUp(self):
        from timeit import repeat
        setup0 = 'from yurl import URL, CachedURL\n'
        try:
            import urllib.parse
        except ImportError:
            setup0 += 'from urlparse import urlparse, urlsplit\n'
        else:
            setup0 += 'from urllib.parse import urlparse, urlsplit\n'
        self.test = lambda stmt, setup='': min(repeat(stmt, setup0 + setup,
                                                      number=10**3))

    def one_try(self, url, setup, *tests):
        results = [self.test(test, setup) * 1000 for test in tests]

        print(end=' ', *['{0:6.4}'.format(result) for result in results])
        if results[0] > min(results[1:]):
            print('!warning', end='')
        print(' ', url)

    def test_parse(self):
        print('\n=== Test parse ===')
        for url in self.test_urls:
            setup = "i = 0; url = {0}".format(repr(url))
            self.one_try(url, setup,
                         "URL(url + str(i)); i+=1",
                         "urlsplit(url + str(i)); i+=1")
        print('  = with cache =')
        for url in self.test_urls:
            setup = "i = 0; url = {0}".format(repr(url))
            self.one_try(url, setup,
                         "CachedURL(url + str(i % 20)); i+=1",
                         "urlsplit(url + str(i % 20)); i+=1")

    def test_pickle(self):
        print('\n=== Test pickle ===')
        for url in self.test_urls:
            setup = ("try:\n  import cPickle as pickle\n"
                     "except ImportError:\n  import pickle\n"
                     "yurl = URL({0})\n"
                     "parsed = urlsplit({0})\n").format(repr(url))
            self.one_try(url, setup,
                         "pickle.dumps(yurl)",
                         "pickle.dumps(parsed)")

    def test_unpickle(self):
        print('\n=== Test unpickle ===')
        for url in self.test_urls:
            setup = (("try:\n  import cPickle as pickle\n"
                      "except ImportError:\n  import pickle\n"
                      "yurl = pickle.dumps(URL({0}))\n"
                      "parsed = pickle.dumps(urlsplit({0}))\n")
                     .format(repr(url)))
            self.one_try(url, setup,
                         "pickle.loads(yurl)",
                         "pickle.loads(parsed)")


if __name__ == '__main__':
    if '-bench' in sys.argv:
        sys.argv.remove('-bench')
    unittest.main()

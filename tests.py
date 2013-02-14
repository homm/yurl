import sys
import unittest

from yurl import URL


class ParseTests(unittest.TestCase):
    def setUp(self):
        from urllib.parse import urlsplit
        self.split = urlsplit

    def one_try(self, url, scheme='', host='', path='', query='', fragment='',
                userinfo='', port='', urlsplit=True):
        splitted = (scheme, host, path, query, fragment, userinfo, port)
        self.assertEqual(URL(url), splitted)
        self.assertEqual(URL(None, *splitted), splitted)
        self.assertEqual(URL(None, *URL(url)), splitted)

        if urlsplit and '-v' in sys.argv:
            if userinfo:
                host = userinfo + '@' + host
            if port:
                host += ':' + port
            splitted = (scheme, host, path, query, fragment)
            if self.split(url) != splitted:
                print('\n  urllib issue:', url, self.split(url))

    def test_scheme_valid(self):
        self.one_try('scheme:path', 'scheme', '', 'path')
        self.one_try('allow+chars-33.:path', 'allow+chars-33.', '', 'path')
        self.one_try('simple:', 'simple', '', '')
        self.one_try('google.com:80', 'google.com', '', '80')
        self.one_try('google.com:80/root', 'google.com', '', '80/root')

    def test_scheme_invalid(self):
        self.one_try('not_a_cheme:path', '', '', 'not_a_cheme:path')
        self.one_try('37signals:books', '', '', '37signals:books')
        self.one_try(':realy-path', '', '', ':realy-path')
        self.one_try('://even-this', '', '', '://even-this')

    def test_host_valid(self):
        self.one_try('scheme://host/path', 'scheme', 'host', '/path')
        self.one_try('//host/path', '', 'host', '/path')
        self.one_try('//host+path', '', 'host+path', '')
        self.one_try('//host', '', 'host', '')
        self.one_try('//this+is$also&host!', '', 'this+is$also&host!', '')

    def test_host_invalid(self):
        self.one_try('scheme:/host/path', 'scheme', '', '/host/path')
        self.one_try('scheme:///host/path', 'scheme', '', '/host/path')

    def test_port_valid(self):
        self.one_try('//host:80/path', '', 'host', '/path', port='80')
        self.one_try('//host:22:80/path', '', 'host:22', '/path', port='80')
        self.one_try('//host:80', '', 'host', port='80')
        self.one_try('//:80', port='80')

    def test_port_invalid(self):
        self.one_try('//host:no/path', '', 'host:no', '/path')
        self.one_try('//host:22:no/path', '', 'host:22:no', '/path')
        self.one_try('//host:-80/path', '', 'host:-80', '/path')

    def test_userinfo_valid(self):
        pass

    def test_userinfo_invalid(self):
        pass

    def test_path_valid(self):
        pass

    def test_path_invalid(self):
        pass

    def test_query_valid(self):
        self.one_try('?query', '', '', '', 'query')
        self.one_try('//host?query', '', 'host', '', 'query')
        self.one_try('//host/path?query', '', 'host', '/path', 'query')
        self.one_try('//ho?st/path?query', '', 'ho', '', 'st/path?query')
        self.one_try('?a://b:c@d.e/f?g#h', '', '', '', 'a://b:c@d.e/f?g', 'h')

    def test_query_invalid(self):
        self.one_try('#?query', '', '', '', '', '?query')

    def test_fragment_valid(self):
        self.one_try('#frag', '', '', '', '', 'frag')
        self.one_try('//host#frag', '', 'host', '', '', 'frag')
        self.one_try('//host/path#frag', '', 'host', '/path', '', 'frag')
        self.one_try('//host?query#frag', '', 'host', '', 'query', 'frag')
        self.one_try('//ho#st/path?query', '', 'ho', '', '', 'st/path?query')
        self.one_try('#a://b:c@d.e/f?g#h', '', '', '', '', 'a://b:c@d.e/f?g#h')

    def test_fragment_invalid(self):
        pass

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

    def test_add(self):
        return
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
        for url in ['','ya.ru', 'ya.ru:80', ':80', 'info@ya.ru',
                    'info@', 'info@:80']:
            self.assertEqual(URL('//' + url).authority, url)

    def test_full_path(self):
        for url in ['', 'path', 'path?query', 'path#fragment',
                    'path?query#fragment', '?query', '#fragment',
                    '?query#fragment']:
            self.assertEqual(URL(url).full_path, url)


@unittest.skipUnless('-bench' in sys.argv, "run with -bench arg")
class BenchmarkTests(unittest.TestCase):
    test_urls = ['https://user:info@yandex.ru:8080/path/to+the=ar?gum=ent#s',
                 'scheme:8080/path/to;the=ar?gum=ent#s',
                 'lucky-number:3456',
                 '//host:80']

    def setUp(self):
        from timeit import repeat
        setup0 = ('from urllib.parse import urlparse, urlsplit\n'
                  'from yurl import URL\n')
        self.test = lambda stmt, setup='': min(repeat(stmt, setup0 + setup,
                                                      number=10**3))

    def one_try(self, url, setup, *tests):
        results = [self.test(test, setup) * 1000 for test in tests]

        print(end=' ', *['{:6.4}'.format(result) for result in results])
        if results[0] > min(results[1:]):
            print('!warning', end='')
        print(' ', url)

    def test_parse(self):
        print('\n=== Test parse ===')
        for url in self.test_urls:
            setup = "i = 0; url = {}".format(repr(url))
            self.one_try(url, setup,
                         "URL(url + str(i)); i+=1",
                         "urlsplit(url + str(i)); i+=1")

    def test_pickle(self):
        print('\n=== Test pickle ===')
        for url in self.test_urls:
            setup = ("import pickle\n"
                     "yurl = URL({0})\n"
                     "parsed = urlsplit({0})\n").format(repr(url))
            self.one_try(url, setup,
                         "pickle.dumps(yurl)",
                         "pickle.dumps(parsed)")

    def test_unpickle(self):
        print('\n=== Test unpickle ===')
        for url in self.test_urls:
            setup = ("import pickle\n"
                     "yurl = pickle.dumps(URL({0}))\n"
                     "parsed = pickle.dumps(urlsplit({0}))\n").format(repr(url))
            self.one_try(url, setup,
                         "pickle.loads(yurl)",
                         "pickle.loads(parsed)")


if __name__ == '__main__':
    if '-bench' in sys.argv:
        sys.argv.remove('-bench')
    unittest.main()

import unittest

from betterparse import URL


class SplitTests(unittest.TestCase):
    def one_try(self, url, scheme='', host='', path='', query='', fragment='',
                userinfo='', port=''):
        splitted = (scheme, host, path, query, fragment, userinfo, port)
        self.assertEqual(URL(url), splitted)
        self.assertEqual(URL(None, *splitted), splitted)
        self.assertEqual(URL(None, *URL(url)), splitted)

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
        self.one_try('//HOST', '', 'host', '')
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
        pass

    def test_query_invalid(self):
        pass

    def test_fragment_valid(self):
        pass

    def test_fragment_invalid(self):
        pass

    def test_case_sensitivity(self):
        self.one_try('A://B:C@D.E/F?G#H', 'a', 'd.e', '/F', 'G', 'H', 'B:C')

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
        self.one_try('/path#', '', '', '/path')
        self.one_try('#')

if __name__ == '__main__':
    unittest.main()

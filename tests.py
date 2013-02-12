import unittest

from betterparse import URL


class SplitTests(unittest.TestCase):
    def one_try(self, url, scheme='', host='', path='', query='', fragment='',
                userinfo='', port=''):
        splitted = (scheme, host, path, query, fragment, userinfo, port)
        self.assertEqual(URL(url), splitted)

    def test_scheme(self):
        self.one_try('scheme:path', 'scheme', '', 'path')
        self.one_try('scheme+with-allow.chars-33:path',
                     'scheme+with-allow.chars-33', '', 'path')

        self.one_try('not_a_cheme:path', '', '', 'not_a_cheme:path')
        self.one_try('37signals:books', '', '', '37signals:books')
        self.one_try('lucku-number:33', 'lucku-number', '', '33')

        self.one_try('HTTP:PATH', 'http', '', 'PATH')

    def test_authority(self):
        # Host starts with //
        self.one_try('scheme://host/path', 'scheme', 'host', '/path')
        self.one_try('scheme:/host/path', 'scheme', '', '/host/path')
        self.one_try('scheme:///host/path', 'scheme', '', '/host/path')

        # Host with empty parts
        self.one_try('//host/path', '', 'host', '/path')
        self.one_try('//@host:/path', '', 'host', '/path')

        # port
        self.one_try('//host:80/path', '', 'host', '/path', port='80')
        self.one_try('//host:22:80/path', '', 'host:22', '/path', port='80')
        self.one_try('//host:not/path', '', 'host:not', '/path')
        self.one_try('//host:not:/path', '', 'host:not', '/path')
        self.one_try('//host:22:not/path', '', 'host:22:not', '/path')
        self.one_try('//host:22:not:/path', '', 'host:22:not', '/path')


if __name__ == '__main__':
    unittest.main()

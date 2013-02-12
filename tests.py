import unittest

from betterparse import _split_re


class SplitTests(unittest.TestCase):
    def one_try(self, url, scheme='', host='', path='', query='', fragment='',
            userinfo='', port=''):
        splitted = (scheme, userinfo, host, port, path, query, fragment)
        self.assertEqual(_split_re(url).groups(''), splitted)

    def test_scheme(self):
        self.one_try('scheme:path', 'scheme', '', 'path')
        self.one_try('scheme+with-allow.chars-33:path',
                     'scheme+with-allow.chars-33', '', 'path')
        self.one_try('not_a_cheme:path', '', '', 'not_a_cheme:path')
        self.one_try('37signals:books', '', '', '37signals:books')


if __name__ == '__main__':
    unittest.main()

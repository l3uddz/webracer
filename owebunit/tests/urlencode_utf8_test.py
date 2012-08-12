import unittest
import owebunit

class UrlencodeTestCase(unittest.TestCase):
    def test_urlencode_simple(self):
        input = dict(a='a', b='b')
        output = owebunit.urlencode_utf8(input)
        self.assertEqual('a=a&b=b', output)

if __name__ == '__main__':
    import unittest
    unittest.main()

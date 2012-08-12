import unittest
import owebunit

class UrlencodeTestCase(unittest.TestCase):
    def test_urlencode_simple(self):
        input = dict(a='a', b='b')
        output = owebunit.urlencode_utf8(input)
        self.assertEqual('a=a&b=b', output)
    
    def test_urlencode_list(self):
        input = dict(a=[1])
        output = owebunit.urlencode_utf8(input)
        self.assertEqual('a[]=1', output)
    
    def test_urlencode_list_multi(self):
        input = dict(a=[1, 2])
        output = owebunit.urlencode_utf8(input)
        self.assertEqual('a[]=1&a[]=2', output)
    
    def test_urlencode_tuple(self):
        input = dict(a=(1,))
        output = owebunit.urlencode_utf8(input)
        self.assertEqual('a[]=1', output)
    
    def test_urlencode_tuple_multi(self):
        input = dict(a=(1, 2))
        output = owebunit.urlencode_utf8(input)
        self.assertEqual('a[]=1&a[]=2', output)

if __name__ == '__main__':
    import unittest
    unittest.main()

# -*- coding: utf-8 -*-

import unittest
import webracer

class UrlencodeUtf8Test(unittest.TestCase):
    def test_urlencode_simple(self):
        input = dict(a='a', b='b')
        output = webracer.urlencode_utf8(input)
        # dictionary keys are not ordered
        self.assertTrue(output == 'a=a&b=b' or output == 'b=b&a=a')
    
    def test_urlencode_list(self):
        input = dict(a=[1])
        output = webracer.urlencode_utf8(input)
        self.assertEqual('a[]=1', output)
    
    def test_urlencode_list_multi(self):
        input = dict(a=[1, 2])
        output = webracer.urlencode_utf8(input)
        self.assertEqual('a[]=1&a[]=2', output)
    
    def test_urlencode_tuple(self):
        input = dict(a=(1,))
        output = webracer.urlencode_utf8(input)
        self.assertEqual('a[]=1', output)
    
    def test_urlencode_tuple_multi(self):
        input = dict(a=(1, 2))
        output = webracer.urlencode_utf8(input)
        self.assertEqual('a[]=1&a[]=2', output)
    
    def test_one_elment_tuple(self):
        # Use correct syntax
        input = (('a', 'b'),)
        expected = 'a=b'
        self.check(input, expected)
    
    def test_tuple_wrong_msg(self):
        # Pass a pair instead of a sequence of pairs
        input = ('a', 'b')
        try:
            webracer.urlencode_utf8(input)
        except ValueError as e:
            assert 'Parameter must be a sequence of pairs' in str(e)
        else:
            self.fail('Expected ValueError to be raised')
    
    def test_tuple_of_tuples(self):
        input = (('a', 'b'), ('c', 'd'))
        expected = 'a=b&c=d'
        self.check(input, expected)
    
    def test_list_of_lists(self):
        input = [['a', 'b'], ['c', 'd']]
        expected = 'a=b&c=d'
        self.check(input, expected)
    
    def test_list_of_tuples(self):
        input = [('a', 'b'), ('c', 'd')]
        expected = 'a=b&c=d'
        self.check(input, expected)
    
    def test_tuple_of_lists(self):
        input = (['a', 'b'], ['c', 'd'])
        expected = 'a=b&c=d'
        self.check(input, expected)
    
    def test_unicode(self):
        # utf-8 as input
        str = 'Колбаса'
        input = [['a', str]]
        expected = 'a=%D0%9A%D0%BE%D0%BB%D0%B1%D0%B0%D1%81%D0%B0'
        self.check(input, expected)
    
    def check(self, input, expected):
        output = webracer.urlencode_utf8(input)
        self.assertEqual(expected, output)

if __name__ == '__main__':
    import unittest
    unittest.main()

import unittest
import owebunit
import utils

class ExtendParamsTestCase(unittest.TestCase):
    def test_tuple_into_tuple(self):
        target = (('a', '1'), ('b', '2'))
        extra = (('c', '3'),)
        expected = (('a', '1'), ('b', '2'), ('c', '3'))
        self._check(target, extra, expected)
    
    def test_dict_into_tuple(self):
        target = (('a', '1'), ('b', '2'))
        extra = dict(c='3')
        expected = (('a', '1'), ('b', '2'), ('c', '3'))
        self._check(target, extra, expected)
    
    def test_dict_into_dict(self):
        target = dict(a='1', b='2')
        extra = dict(c='3')
        expected = dict(a='1', b='2', c='3')
        self._check(target, extra, expected)
    
    def test_tuple_into_dict(self):
        target = dict(a='1', b='2')
        extra = (('c', '3'),)
        self.assertRaises(ValueError, self._check, target, extra, None)
    
    def test_tuple_duplicates(self):
        target = (('a', '1'), ('b', '2'))
        extra = (('a', '3'),)
        expected = (('a', '1'), ('b', '2'), ('a', '3'))
        self._check(target, extra, expected)
    
    def test_dict_duplicates(self):
        target = dict(a='1', b='2')
        extra = dict(a='3')
        expected = dict(a='3', b='2')
        self._check(target, extra, expected)
    
    def test_list_into_list(self):
        target = [['a', '1'], ['b', '2']]
        extra = [['c', '3']]
        expected = (('a', '1'), ('b', '2'), ('c', '3'))
        self._check(target, extra, expected)
    
    def _check(self, target, extra, expected):
        actual = owebunit.extend_params(target, extra)
        self.assertEqual(utils.listit(expected), utils.listit(actual))

if __name__ == '__main__':
    import unittest
    unittest.main()

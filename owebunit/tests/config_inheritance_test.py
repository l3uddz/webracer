import unittest
import owebunit

class ConfigInheritanceTestCase(unittest.TestCase):
    def test_not_propagates_inappropriately(self):
        @owebunit.config(host='foo')
        class TestOne(owebunit.WebTestCase):
            def test_method(self):
                pass
        
        class TestTwo(owebunit.WebTestCase):
            def test_method(self):
                pass
        
        self.assertEquals('foo', TestOne('test_method').config.host)
        self.assertIs(None, TestTwo('test_method').config.host)

if __name__ == '__main__':
    import unittest
    unittest.main()

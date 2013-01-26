import unittest
import webracer

class ConfigInheritanceTest(unittest.TestCase):
    def test_not_propagates_inappropriately(self):
        @webracer.config(host='foo')
        class TestOne(webracer.WebTestCase):
            def test_method(self):
                pass
        
        class TestTwo(webracer.WebTestCase):
            def test_method(self):
                pass
        
        self.assertEquals('foo', TestOne('test_method').config.host)
        self.assertTrue(TestTwo('test_method').config.host is None)

if __name__ == '__main__':
    import unittest
    unittest.main()

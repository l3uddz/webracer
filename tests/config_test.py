import unittest
import webracer
import nose.tools

class ConfigTest(unittest.TestCase):
    def test_default_config(self):
        config = webracer.Config()
        assert config.host is None
    
    def test_modifying_config(self):
        config = webracer.Config()
        assert config.host is None
        
        config.host = 'testhost'
        self.assertEqual('testhost', config.host)
    
    def test_constructor_keywords(self):
        config = webracer.Config(host='testhost', port=1234)
        self.assertEqual('testhost', config.host)
        self.assertEqual(1234, config.port)
    
    @nose.tools.raises(ValueError)
    def test_bogus_constructor_keyword(self):
        config = webracer.Config(bogus='foo')

if __name__ == '__main__':
    import unittest
    unittest.main()

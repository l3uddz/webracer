import unittest
import owebunit

class ConfigTest(unittest.TestCase):
    def test_default_config(self):
        config = owebunit.Config()
        assert config.host is None
    
    def test_modifying_config(self):
        config = owebunit.Config()
        assert config.host is None
        
        config.host = 'testhost'
        self.assertEqual('testhost', config.host)

if __name__ == '__main__':
    import unittest
    unittest.main()

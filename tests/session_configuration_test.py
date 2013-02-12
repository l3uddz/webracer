import webracer
import unittest

class SessionConfigurationTest(unittest.TestCase):
    def test_no_configuration(self):
        session = webracer.session.Session()
        assert session.config.host is None
    
    def test_config_configuration(self):
        config = webracer.session.Config(host='testhost')
        session = webracer.session.Session(config)
        self.assertEqual('testhost', session.config.host)
    
    def test_kwargs_configuration(self):
        session = webracer.session.Session(host='testhost')
        self.assertEqual('testhost', session.config.host)

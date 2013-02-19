import webracer.agent
import unittest

class SessionConfigurationTest(unittest.TestCase):
    def test_no_configuration(self):
        session = webracer.agent.Session()
        assert session.config.host is None
    
    def test_config_configuration(self):
        config = webracer.agent.Config(host='testhost')
        session = webracer.agent.Session(config)
        self.assertEqual('testhost', session.config.host)
    
    def test_kwargs_configuration(self):
        session = webracer.agent.Session(host='testhost')
        self.assertEqual('testhost', session.config.host)

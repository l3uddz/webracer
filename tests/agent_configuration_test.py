import webracer.agent
import unittest

class AgentConfigurationTest(unittest.TestCase):
    def test_no_configuration(self):
        agent = webracer.agent.Agent()
        assert agent.config.host is None
    
    def test_config_configuration(self):
        config = webracer.agent.Config(host='testhost')
        agent = webracer.agent.Agent(config)
        self.assertEqual('testhost', agent.config.host)
    
    def test_kwargs_configuration(self):
        agent = webracer.agent.Agent(host='testhost')
        self.assertEqual('testhost', agent.config.host)

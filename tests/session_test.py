import webracer
from tests import utils
from tests import kitchen_sink_app

def setup_module():
    utils.start_bottle_server(kitchen_sink_app.app, 8052)

@webracer.config(host='localhost', port=8052)
class SessionTest(webracer.WebTestCase):
    def test_get(self):
        s = webracer.Session()
        s.get('/ok')
        self.assertEqual(200, s.response.code)
        self.assertEqual('ok', s.response.body)
    
    def test_custom_user_agent(self):
        # XXX improve this api
        config = webracer.Config(user_agent='Quux-o-matic/1.0')
        s = webracer.Session(config)
        s.get('/get_user_agent')
        self.assertEqual(200, s.response.code)
        self.assertEqual('Quux-o-matic/1.0', s.response.body)
    
    def test_double_user_agent_override(self):
        # XXX improve this api
        config = webracer.Config(user_agent='Quux-o-matic/1.0')
        s = webracer.Session(config)
        headers = {'user-agent': 'Barlicious/2.0'}
        s.get('/get_user_agent', headers=headers)
        self.assertEqual(200, s.response.code)
        self.assertEqual('Barlicious/2.0', s.response.body)

if __name__ == '__main__':
    import unittest
    unittest.main()

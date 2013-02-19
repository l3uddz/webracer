import webracer
import nose.plugins.attrib
from . import utils
from .apps import kitchen_sink_app

utils.app_runner_setup(__name__, kitchen_sink_app.app, 8056)

base_config = dict(host='localhost', port=8056)

@nose.plugins.attrib.attr('client')
class AgentWithoutCookieJarTest(webracer.WebTestCase):
    def test_request(self):
        '''Tests that the client works when use_cookie_jar is False.
        '''
        
        config = utils.add_dicts(base_config, dict(
            use_cookie_jar=False))
        s = webracer.Agent(**config)
        s.get('/ok')
        self.assertEqual(200, s.response.code)
        self.assertEqual('ok', s.response.body)
    
    def test_no_cookie_jar(self):
        config = utils.add_dicts(base_config, dict(
            use_cookie_jar=False))
        s = webracer.Agent(**config)
        s.get('/set_cookie')
        self.assertEqual(200, s.response.code)
        self.assertEqual('ok', s.response.body)
        
        s.assert_response_cookie('visited')
        s.assert_not_cookie_jar_cookie('visited')

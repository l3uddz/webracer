import webracer
import nose.plugins.attrib
from . import utils
from .apps import kitchen_sink_app

utils.app_runner_setup(__name__, kitchen_sink_app.app, 8056)

base_config = dict(host='localhost', port=8056)

@nose.plugins.attrib.attr('client')
class SessionWithoutCookieJarTest(webracer.WebTestCase):
    def test_request(self):
        '''Tests that the client works when use_cookie_jar is False.
        '''
        
        config = webracer.Config(**utils.add_dicts(base_config, dict(
            use_cookie_jar=False)))
        s = webracer.Session(config)
        s.get('/ok')
        self.assertEqual(200, s.response.code)
        self.assertEqual('ok', s.response.body)
    
    def test_no_cookie_jar(self):
        config = webracer.Config(**utils.add_dicts(base_config, dict(
            use_cookie_jar=False)))
        s = webracer.Session(config)
        s.get('/set_cookie')
        self.assertEqual(200, s.response.code)
        self.assertEqual('ok', s.response.body)
        
        s.assert_response_cookie('visited')
        s.assert_not_session_cookie('visited')

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
        
        # response cookie access
        self.assertEqual([], utils.listit(s.response.raw_cookies))
        self.assertEqual({}, s.response.cookies)
        
        # response assertions
        s.assert_not_response_cookie('visited')
        s.assert_not_cookie_jar_cookie('visited')
    
    def test_no_cookie_jar(self):
        '''Tests that the client works when use_cookie_jar is True,
        when cookies are set in response.
        '''
        
        config = utils.add_dicts(base_config, dict(
            use_cookie_jar=False))
        s = webracer.Agent(**config)
        s.get('/set_cookie')
        self.assertEqual(200, s.response.code)
        self.assertEqual('ok', s.response.body)
        
        # response cookie access
        self.assertEqual(1, len(s.response.raw_cookies))
        self.assertEqual(1, len(s.response.cookies))
        assert 'visited' in s.response.cookies
        
        cookie = s.response.cookies['visited']
        self.assertEqual('yes', cookie.value)
        
        # response assertions
        s.assert_response_cookie('visited')
        s.assert_not_cookie_jar_cookie('visited')
    
    def test_with_cookie_jar(self):
        s = webracer.agent.Agent(**base_config)
        s.get('/set_cookie')
        self.assertEqual(200, s.response.code)
        self.assertEqual('ok', s.response.body)
        
        # response cookie access
        self.assertEqual(1, len(s.response.raw_cookies))
        self.assertEqual(1, len(s.response.cookies))
        assert 'visited' in s.response.cookies
        
        cookie = s.response.cookies['visited']
        self.assertEqual('yes', cookie.value)
        
        # response assertions
        s.assert_response_cookie('visited')
        s.assert_cookie_jar_cookie('visited')
    
    @webracer.config(**base_config)
    def test_cookies_on_test_case_with_cookie_jar(self):
        self.get('/set_cookie')
        self.assert_status(200)
        self.assertEqual('ok', self.response.body)
        
        assert self.cookies is self.response.cookies
    
    @webracer.config(use_cookie_jar=False)
    @webracer.config(**base_config)
    def test_cookies_on_test_case_without_cookie_jar(self):
        self.get('/set_cookie')
        self.assert_status(200)
        self.assertEqual('ok', self.response.body)
        
        assert self.cookies is self.response.cookies

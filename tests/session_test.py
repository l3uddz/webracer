import webracer
import nose.plugins.attrib
from tests import utils
from .apps import kitchen_sink_app

utils.app_runner_setup(__name__, kitchen_sink_app.app, 8052)

@nose.plugins.attrib.attr('client')
@webracer.config(host='localhost', port=8052)
class BasicSessionTest(webracer.WebTestCase):
    def test_session(self):
        with self.session() as s:
            s.get('/ok')
            s.assert_status(200)
    
    def test_multiple_sessions(self):
        one = self.session()
        one.get('/ok')
        
        two = self.session()
        two.get('/internal_server_error')
        
        one.assert_status(200)
        two.assert_status(500)
    
    def test_implicit_session(self):
        self.get('/set_cookie')
        self.assert_status(200)
        self.assert_response_cookie('visited')
        self.assert_session_cookie('visited')
        
        self.get('/read_cookie')
        self.assert_status(200)
        self.assertEqual('yes', self.response.body)
        self.assert_not_response_cookie('visited')
        # session cookie is carried over
        self.assert_session_cookie('visited')

@nose.plugins.attrib.attr('client')
@webracer.no_session
@webracer.config(host='localhost', port=8052)
class NoSessionTest(webracer.WebTestCase):
    def test_implicit_session(self):
        self.get('/set_cookie')
        self.assert_status(200)
        self.assert_response_cookie('visited')
        self.assert_session_cookie('visited')
        
        self.get('/read_cookie')
        self.assert_status(200)
        self.assertEqual('', self.response.body)
        self.assert_not_response_cookie('visited')
        # session cookie is not carried over
        self.assert_not_session_cookie('visited')

base_config = dict(host='localhost', port=8052)

@nose.plugins.attrib.attr('client')
class SessionWithCustomConfigTest(webracer.WebTestCase):
    def test_get(self):
        config = webracer.Config(**base_config)
        s = webracer.Session(config)
        s.get('/ok')
        self.assertEqual(200, s.response.code)
        self.assertEqual('ok', s.response.body)
    
    def test_custom_user_agent(self):
        # XXX improve this api
        config = webracer.Config(**utils.add_dicts(base_config, dict(user_agent='Quux-o-matic/1.0')))
        s = webracer.Session(config)
        s.get('/get_user_agent')
        self.assertEqual(200, s.response.code)
        self.assertEqual('Quux-o-matic/1.0', s.response.body)
    
    def test_double_user_agent_override(self):
        # XXX improve this api
        config = webracer.Config(**utils.add_dicts(base_config, dict(user_agent='Quux-o-matic/1.0')))
        s = webracer.Session(config)
        headers = {'user-agent': 'Barlicious/2.0'}
        s.get('/get_user_agent', headers=headers)
        self.assertEqual(200, s.response.code)
        self.assertEqual('Barlicious/2.0', s.response.body)

import webracer
import ocookie
import nose.plugins.attrib
from . import utils
from .apps import kitchen_sink_app

utils.app_runner_setup(__name__, kitchen_sink_app.app, 8052)

@nose.plugins.attrib.attr('client')
@webracer.config(host='localhost', port=8052)
class BasicAgentTest(webracer.WebTestCase):
    def test_agent(self):
        with self.agent() as s:
            s.get('/ok')
            s.assert_status(200)
    
    def test_multiple_agents(self):
        one = self.agent()
        one.get('/ok')
        
        two = self.agent()
        two.get('/internal_server_error')
        
        one.assert_status(200)
        two.assert_status(500)
    
    def test_implicit_agent(self):
        self.get('/set_cookie')
        self.assert_status(200)
        self.assert_response_cookie('visited')
        self.assert_cookie_jar_cookie('visited')
        
        self.get('/read_cookie')
        self.assert_status(200)
        self.assertEqual('yes', self.response.body)
        self.assert_not_response_cookie('visited')
        # cookie jar cookie is carried over
        self.assert_cookie_jar_cookie('visited')

@nose.plugins.attrib.attr('client')
@webracer.no_session
@webracer.config(host='localhost', port=8052)
class NoSessionTest(webracer.WebTestCase):
    def test_implicit_agent(self):
        self.get('/set_cookie')
        self.assert_status(200)
        self.assert_response_cookie('visited')
        self.assert_cookie_jar_cookie('visited')
        
        self.get('/read_cookie')
        self.assert_status(200)
        self.assertEqual('', self.response.body)
        self.assert_not_response_cookie('visited')
        # cookie jar cookie is not carried over
        self.assert_not_cookie_jar_cookie('visited')

base_config = dict(host='localhost', port=8052)

@nose.plugins.attrib.attr('client')
class AgentConstructionTest(webracer.WebTestCase):
    def test_get(self):
        s = webracer.Agent(**base_config)
        s.get('/ok')
        self.assertEqual(200, s.response.code)
        self.assertEqual('ok', s.response.body)
    
    def test_custom_user_agent(self):
        # XXX improve this api
        config = utils.add_dicts(base_config, dict(user_agent='Quux-o-matic/1.0'))
        s = webracer.Agent(**config)
        s.get('/get_user_agent')
        self.assertEqual(200, s.response.code)
        self.assertEqual('Quux-o-matic/1.0', s.response.body)
    
    def test_double_user_agent_override(self):
        # XXX improve this api
        config = utils.add_dicts(base_config, dict(user_agent='Quux-o-matic/1.0'))
        s = webracer.Agent(**config)
        headers = {'user-agent': 'Barlicious/2.0'}
        s.get('/get_user_agent', headers=headers)
        self.assertEqual(200, s.response.code)
        self.assertEqual('Barlicious/2.0', s.response.body)
    
    def test_specifying_cookie_jar(self):
        cookie_jar = ocookie.CookieJar()
        s = webracer.Agent(cookie_jar=cookie_jar, **base_config)
        s.get('/set_cookie')
        s.assert_status(200)
        s.assert_response_cookie('visited', value='yes')
        assert 'visited' in cookie_jar
        self.assertEqual('yes', cookie_jar['visited'].value)
    
    def test_copy_highlevel(self):
        s = webracer.Agent(**base_config)
        s.get('/set_cookie_value', query=dict(v='start'))
        s.assert_status(200)
        s.assert_response_cookie('sink', value='start')
        
        a = s.copy()
        b = s.copy()
        
        a.get('/read_cookie_value/sink')
        a.assert_status(200)
        self.assertEqual('start', a.response.body)
        
        a.get('/set_cookie_value', query=dict(v='avalue'))
        a.assert_status(200)
        a.assert_response_cookie('sink', value='avalue')
        
        a.get('/read_cookie_value/sink')
        a.assert_status(200)
        self.assertEqual('avalue', a.response.body)
        
        # b has original start value
        
        b.get('/read_cookie_value/sink')
        b.assert_status(200)
        self.assertEqual('start', b.response.body)

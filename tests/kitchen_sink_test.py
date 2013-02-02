import webracer
from tests import utils
from tests import kitchen_sink_app

def setup_module():
    utils.start_bottle_server(kitchen_sink_app.app, 8041)

@webracer.config(host='localhost', port=8041)
class KitchenSinkTest(webracer.WebTestCase):
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
    
    def test_cookie(self):
        self.get('/set_cookie')
        self.assert_status(200)
        
        self.assert_response_cookie('visited')
        self.assert_response_cookie('visited', value='yes')
        
        # nonexistent cookie
        self.assert_not_response_cookie('nonexistent_cookie')
        
        with self.assert_raises(AssertionError):
            self.assert_response_cookie('visited', value='no')
    
    def test_multiple_cookies(self):
        self.get('/set_multiple_cookies')
        self.assert_status(200)
        
        self.assert_response_cookie('foo_a')
        self.assert_response_cookie('foo_a', value='a_value')
        self.assert_response_cookie('foo_b')
        self.assert_response_cookie('foo_b', value='b_value')
        self.assert_response_cookie('foo_c')
        self.assert_response_cookie('foo_c', value='c_value')
    
    def test_colon_in_cookie_value(self):
        #self.get('/set_cookie_value', query=('v', 'a:b'))
        self.get('/set_cookie_value', query=(('v', 'a:b'),))
        self.assert_status(200)
        
        self.assertEqual('a:b', self.response.body)
        self.assert_response_cookie('sink')
        # should get back the same value we passed,
        # but something appears to quote it...
        # on python 2.7, and not on python 3.3
        # XXX this test is now rather toothless
        #self.assert_response_cookie('sink', value='"a:b"')
    
    def test_colon_in_cookie_value_in_session(self):
        self.get('/set_cookie_value', query=(('v', 'a:b'),))
        self.assert_status(200)
        
        self.get('/read_cookie_value/sink')
        self.assert_status(200)
        # should get back the same value we passed initially.
        # the value in this test passes through cookie jar
        self.assertEqual('a:b', self.response.body)
    
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
    
    def test_json_parsing_empty(self):
        self.get('/json/empty')
        self.assert_status(200)
        self.assertEqual({}, self.response.json)
    
    def test_json_parsing_hash(self):
        self.get('/json/hash')
        self.assert_status(200)
        self.assertEqual({'a': 'b'}, self.response.json)
    
    def test_redirect_assertion(self):
        self.get('/redirect')
        self.assert_redirected_to_uri('/found')
    
    def test_follow_redirect(self):
        self.get('/redirect_to', query=dict(target='/ok'))
        self.assert_redirected_to_uri('/ok')
        self.follow_redirect()
        self.assert_status(200)
        self.assertEqual('ok', self.response.body)

@webracer.no_session
@webracer.config(host='localhost', port=8041)
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

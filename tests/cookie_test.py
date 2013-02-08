import webracer
from tests import utils
from tests import kitchen_sink_app

utils.app_runner_setup(__name__, kitchen_sink_app.app, 8057)

@webracer.config(host='localhost', port=8057)
class CookieTest(webracer.WebTestCase):
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

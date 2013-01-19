import urllib2
import cookielib
import unittest
from tests import utils
from tests import kitchen_sink_app

utils.start_bottle_server(kitchen_sink_app.app, 8099)

class UrllibTest(unittest.TestCase):
    def setUp(self):
        super(UrllibTest, self).setUp()
        
        self.cookie_jar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
    
    def test_baseline(self):
        resp = self.opener.open('http://localhost:8099/ok')
        body = resp.read()
        self.assertEqual('ok', body)
    
    def test_cookie(self):
        resp = self.opener.open('http://localhost:8099/set_cookie')
        cookies = list(self.cookie_jar)
        self.assertEqual(1, len(cookies))
        cookie = cookies[0]
        self.assertEqual('visited', cookie.name)
        self.assertEqual('yes', cookie.value)
    
    def test_cookie_with_colon(self):
        # a:b
        resp = self.opener.open('http://localhost:8099/set_cookie_value?v=a%3Ab')
        cookies = list(self.cookie_jar)
        self.assertEqual(1, len(cookies))
        cookie = cookies[0]
        self.assertEqual('sink', cookie.name)
        
        # bottle must be escaping cookie value.
        # we should not care what it is in the cookie header
        # as long as subsequent requests correctly interpret it
        self.assertEqual('"a:b"', cookie.value)
        
        resp = self.opener.open('http://localhost:8099/read_cookie_value/sink')
        body = resp.read()
        self.assertEqual('a:b', body)

if __name__ == '__main__':
    import unittest
    unittest.main()

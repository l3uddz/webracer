import sys
import unittest
from .. import utils
from ..apps import kitchen_sink_app

if utils.py3:
    import urllib.request as urllib_request
    import http.cookiejar as cookielib
    
    def decode_str(str):
        return str.decode('utf8')
else:
    import urllib2 as urllib_request
    import cookielib
    
    def decode_str(str):
        return str

utils.app_runner_setup(__name__, kitchen_sink_app.app, 8099)

class UrllibTest(unittest.TestCase):
    def setUp(self):
        super(UrllibTest, self).setUp()
        
        self.cookie_jar = cookielib.CookieJar()
        self.opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(self.cookie_jar))
    
    def test_baseline(self):
        resp = self.opener.open('http://localhost:8099/ok')
        body = decode_str(resp.read())
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
        # Apparently the value is quoted on python 2.7 and
        # not quoted on python 3.3
        #self.assertEqual('"a:b"', cookie.value)
        
        resp = self.opener.open('http://localhost:8099/read_cookie_value/sink')
        body = decode_str(resp.read())
        self.assertEqual('a:b', body)

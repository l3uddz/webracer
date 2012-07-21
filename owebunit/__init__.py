import unittest
import httplib
import urlparse
import ocookie.httplibadapter

class Response(object):
    def __init__(self, httplib_response):
        self.httplib_response = httplib_response
    
    @property
    def code(self):
        return self.httplib_response.status
    
    @property
    def cookie_list(self):
        try:
            return self._cookie_list
        except AttributeError:
            self._cookie_list = ocookie.httplibadapter.parse_cookies(
                self.httplib_response.getheaders()
            )
            return self._cookie_list
    
    @property
    def cookie_dict(self):
        try:
            return self._cookie_dict
        except AttributeError:
            self._cookie_dict = ocookie.cookie_list_to_dict(self.cookie_list)
            return self._cookie_dict

def uri(self):
    uri = self.path or '/'
    if self.params:
        uri += ';' + self.params
    if self.query:
        uri += '?' + self.query
    return uri

def parse_url(url):
    parsed_url = urlparse.urlparse(url)
    parsed_url.uri = uri(parsed_url)
    return parsed_url

class AssertRaisesContextManager(object):
    def __init__(self, expected):
        self.expected = expected
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        if type is None:
            assert False
        if type != self.expected:
            assert False
        # silence exception
        return True

class Session(object):
    def __init__(self):
        self._cookie_jar = ocookie.CookieJar()
    
    def get(self, url):
        parsed_url = parse_url(url)
        self.connection = httplib.HTTPConnection(*parsed_url.netloc.split(':'))
        self.connection.request('GET', parsed_url.uri)
        self.response = Response(self.connection.getresponse())
        for cookie in self.response.cookie_list:
            self._cookie_jar.add(cookie)
    
    def assert_code(self, code):
        self.assert_equal(code, self.response.code)
    
    def assert_equal(self, expected, actual):
        assert expected == actual
    
    def assert_response_cookie(self, name, **kwargs):
        '''Asserts that the response (as opposed to the session/cookie jar)
        contains the specified cookie.'''
        
        assert name in self.response.cookie_dict
        if kwargs:
            cookie = self.response.cookie_dict[name]
            if kwargs.has_key('value'):
                self.assert_equal(kwargs['value'], cookie.value)
    
    def assert_not_response_cookie(self, name):
        '''Asserts that a cookie with the specified name was not set
        in the response.'''
        
        assert name not in self.response.cookie_dict
    
    def assert_session_cookie(self, name, **kwargs):
        assert name in self._cookie_jar
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        pass

class WebTestCase(unittest.TestCase):
    def setUp(self):
        super(WebTestCase, self).setUp()
        self._session = Session()
    
    def session(self):
        session = Session()
        return session
    
    def get(self, url):
        self._session.get(url)
    
    def assert_raises(self, expected, *args):
        if args:
            return self.assertRaises(expected, *args)
        else:
            return AssertRaisesContextManager(expected)
    
    def assert_code(self, code):
        self._session.assert_code(code)
    
    def assert_response_cookie(self, name, **kwargs):
        self._session.assert_response_cookie(name, **kwargs)
    
    def assert_not_response_cookie(self, name):
        self._session.assert_not_response_cookie(name)
    
    def assert_session_cookie(self, name, **kwargs):
        self._session.assert_session_cookie(name, **kwargs)
    
    def assert_not_session_cookie(self, name):
        self._session.assert_not_session_cookie(name)

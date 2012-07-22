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
    def body(self):
        try:
            return self._body
        except AttributeError:
            self._body = self.httplib_response.read()
            return self._body
    
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
    
    def request(self, method, url, body=None, headers=None):
        parsed_url = parse_url(url)
        headers = self._merge_headers(headers)
        self.connection = httplib.HTTPConnection(*parsed_url.netloc.split(':'))
        kwargs = {}
        if body is not None:
            kwargs['body'] = body
        if headers is not None:
            kwargs['headers'] = headers
        self.connection.request(method.upper(), parsed_url.uri, **kwargs)
        self.response = Response(self.connection.getresponse())
        for cookie in self.response.cookie_list:
            self._cookie_jar.add(cookie)
    
    def get(self, url, body=None, headers=None):
        self.request('get', url, body, headers)
    
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
    
    def assert_not_session_cookie(self, name, **kwargs):
        assert name not in self._cookie_jar
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        pass
    
    def _merge_headers(self, user_headers):
        if isinstance(user_headers, list) or isinstance(user_headers, tuple):
            # convert to a dictionary for httplib
            map = {}
            for key, value in user_headers:
                if key in map:
                    raise ValueError, 'Duplicate headers are not supported by httplib'
                map[key] = value
            user_headers = map
        
        if self._cookie_jar:
            if user_headers is None:
                user_headers = {}
            if 'cookie' in user_headers:
                value = self._merge_cookie_header_values(user_headers['cookie'])
            else:
                value = self._cookie_jar.build_cookie_header()
        else:
            value = None
        
        if value:
            if user_headers:
                headers = dict(user_headers)
            else:
                headers = {}
            headers['cookie'] = value
        else:
            headers = user_headers
        return headers
    
    def _merge_cookie_header_values(self, user_header_value):
        user_cookie_dict = ocookie.CookieParser.parse_cookie_value(user_header_value)
        cookie_dict = ocookie.CookieDict()
        for cookie in self._cookie_jar:
            cookie_dict[cookie.name] = cookie
        for cookie in user_cookie_dict:
            cookie_dict[cookie.name] = cookie
        return cookie_dict.cookie_header_value()

class WebTestCase(unittest.TestCase):
    def setUp(self):
        super(WebTestCase, self).setUp()
        self._session = Session()
    
    def session(self):
        session = Session()
        return session
    
    @property
    def response(self):
        return self._session.response
    
    def get(self, url):
        if hasattr(self, '_no_session') and self._no_session:
            self._session = Session()
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

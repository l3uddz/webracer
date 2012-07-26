import unittest
import httplib
import urllib
import urlparse
import ocookie.httplibadapter

class HeadersDict(dict):
    '''Dictionary type for headers. Performs case folding of header names.
    '''
    
    def __init__(self, map=None):
        super(HeadersDict, self).__init__()
        
        if map:
            for key in map:
                self[key.lower()] = map[key]
    
    def __delitem__(self, key):
        super(HeadersDict, self).__delitem__(key.lower())
    
    def __getitem__(self, key):
        return super(HeadersDict, self).__getitem__(key.lower())
    
    def __setitem__(self, key, value):
        super(HeadersDict, self).__setitem__(key.lower(), value)
    
    def __contains__(self, key):
        return super(HeadersDict, self).__contains__(key.lower())
    
    def update(self, other):
        for key in other:
            self[key.lower()] = other[key]

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
    def etree(self):
        '''Returns an ElementTree built from response body.'''
        
        import xml.etree.ElementTree
        
        root = xml.etree.ElementTree.ElementTree(self.body)
        return root
    
    @property
    def lxml_etree(self):
        '''Returns an lxml.etree built from response body, treating
        the latter as XML.'''
        
        import lxml.etree
        
        doc = lxml.etree.XML(response.body)
    
    @property
    def lxml_etree_html(self):
        '''Returns an lxml.etree built from response body, treating
        the latter as HTML.'''
        
        import lxml.etree
        
        doc = lxml.etree.HTML(self.body)
        return doc
    
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

def urlencode_utf8(params):
    encoded = {}
    for key in params:
        value = params[key]
        if isinstance(value, unicode):
            encoded[key] = value.encode('utf-8')
        else:
            encoded[key] = value
    encoded = urllib.urlencode(encoded)
    return encoded

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
    def __init__(self, default_netloc=None):
        self._cookie_jar = ocookie.CookieJar()
        if default_netloc:
            self._default_host, self._default_port = default_netloc.split(':')
        else:
            self._default_host, self._default_port = None, None
    
    def request(self, method, url, body=None, headers=None):
        parsed_url = parse_url(url)
        headers = self._merge_headers(headers)
        host, port = self._netloc_to_host_port(parsed_url.netloc)
        self.connection = httplib.HTTPConnection(host, port)
        kwargs = {}
        if body is not None:
            if isinstance(body, dict):
                body = urlencode_utf8(body)
            #if headers is None:
                #headers = headers
            #else:
                #headers = HeadersDict(headers)
            #if 'content-type' not in headers:
                #headers['content-type'] = 'application/x-www-form-urlencoded'
            kwargs['body'] = body
        
        # XXX cherrypy waits for keep-alives to expire, work around that
        if headers is None:
            headers = {}
        else:
            headers = HeadersDict(headers)
        headers['connection'] = 'close'
        
        if headers is not None:
            kwargs['headers'] = headers
        self.connection.request(method.upper(), parsed_url.uri, kwargs.get('body'), kwargs.get('headers'))
        self.response = Response(self.connection.getresponse())
        for cookie in self.response.cookie_list:
            self._cookie_jar.add(cookie)
    
    def _netloc_to_host_port(self, netloc):
        if netloc:
            return netloc.split(':')
        else:
            # url contained path only
            return (self._default_host, self._default_port)
    
    # note: cherrypy webtest has a protocol argument
    def get(self, url, body=None, headers=None):
        return self.request('get', url, body=body, headers=headers)
    
    def post(self, url, body=None, headers=None):
        return self.request('post', url, body=body, headers=headers)
    
    def assert_status(self, code):
        self.assert_equal(code, self.response.code)
    
    def assert_equal(self, expected, actual):
        assert expected == actual, '%s expected but was %s' % (expected, actual)
    
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
                headers = HeadersDict(user_headers)
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
        self._session = self._create_session()
    
    def _create_session(self):
        kwargs = {}
        if hasattr(self.__class__, 'DEFAULT_NETLOC'):
            kwargs['default_netloc'] = self.__class__.DEFAULT_NETLOC
        return Session(**kwargs)
    
    def session(self):
        session = self._create_session()
        return session
    
    @property
    def response(self):
        return self._session.response
    
    def request(self, method, url, body=None, headers=None):
        if hasattr(self, '_no_session') and self._no_session:
            self._session = self._create_session()
        return self._session.request(method, url, body=body, headers=headers)
    
    def get(self, url, body=None, headers=None):
        return self.request('get', url, body=body, headers=headers)
    
    def post(self, url, body=None, headers=None):
        return self.request('post', url, body=body, headers=headers)
    
    def assert_raises(self, expected, *args):
        if args:
            return self.assertRaises(expected, *args)
        else:
            return AssertRaisesContextManager(expected)
    
    def assert_status(self, code):
        self._session.assert_status(code)
    
    def assert_response_cookie(self, name, **kwargs):
        self._session.assert_response_cookie(name, **kwargs)
    
    def assert_not_response_cookie(self, name):
        self._session.assert_not_response_cookie(name)
    
    def assert_session_cookie(self, name, **kwargs):
        self._session.assert_session_cookie(name, **kwargs)
    
    def assert_not_session_cookie(self, name):
        self._session.assert_not_session_cookie(name)

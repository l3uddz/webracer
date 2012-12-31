import httplib
import os.path
import re
import time as _time
import unittest
import urllib
import urlparse
import ocookie.httplibadapter

class Config(object):
    # Host, port and protocol to use when only path is requested.
    # Host may contain port and protocol via host:port or
    # protocol://host or protocol://host:port syntax.
    host = None
    port = None
    protocol = None
    
    # If True, failed responses will be saved in a directory specified by
    # save_dir.
    save_failed_responses = False
    save_dir = None

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
        
        root = xml.etree.ElementTree.fromstring(self.body)
        return root
    
    @property
    def lxml_etree(self):
        '''Returns an lxml.etree built from response body.
        
        Depending on content type of the response, either HTML parsing
        is used (text/html content type) or XML (everything else).
        '''
        
        if self.header_dict['content-type'].lower().find('text/html') >= 0:
            return self.lxml_etree_html
        else:
            return self.lxml_etree_xml
    
    @property
    def lxml_etree_xml(self):
        '''Returns an lxml.etree built from response body, treating
        the latter as XML.'''
        
        import lxml.etree
        
        doc = lxml.etree.XML(self.body)
        return doc
    
    @property
    def lxml_etree_html(self):
        '''Returns an lxml.etree built from response body, treating
        the latter as HTML.'''
        
        import lxml.etree
        
        doc = lxml.etree.HTML(self.body)
        return doc
    
    @property
    def json(self):
        '''Returns response body parsed as JSON.'''
        
        import json
        
        return json.loads(self.body)
    
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
    
    @property
    def header_list(self):
        return self.httplib_response.getheaders()
    
    @property
    def header_dict(self):
        header_list = self.header_list
        map = {}
        for key, value in header_list:
            map[key] = value
        return map
    
    @property
    def location(self):
        headers = self.header_dict
        if 'location' in headers:
            return headers['location']
        else:
            raise ValueError, 'There is no location header in this response'
    
    @property
    def location_uri(self):
        '''Location with the host/port stripped, for ease of asserting.'''
        
        location = self.location
        # XXX could do this via parseurl
        location = re.sub(r'^\w+://[^/]+', '', location)
        location = re.sub(r'^//[^/]+', '', location)
        return location
    
    @property
    def forms(self):
        # XXX optimize
        doc = self.lxml_etree
        forms = [Form(form_tag) for form_tag in doc.xpath('//form')]
        return forms

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

def _urlencode_value(value):
    if isinstance(value, unicode):
        encoded = value.encode('utf-8')
    else:
        encoded = str(value)
    return urllib.quote(encoded)

def urlencode_utf8(params):
    encoded = []
    for key in params:
        value = params[key]
        if isinstance(value, list) or isinstance(value, tuple):
            prefix = key + '[]='
            values = value
            for value in values:
                value = _urlencode_value(value)
                encoded.append(prefix + value)
        else:
            value = _urlencode_value(value)
            encoded.append(key + '=' + value)
    return '&'.join(encoded)

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
    def __init__(self, config, test_case, default_netloc=None):
        self.config = config
        self.test_case = test_case
        self._cookie_jar = ocookie.CookieJar()
        if default_netloc:
            self._default_host, self._default_port = default_netloc.split(':')
        else:
            self._default_host, self._default_port = None, None
    
    def request(self, method, url, body=None, query=None, headers=None):
        url = self._absolutize_url(url)
        parsed_url = parse_url(url)
        host, port = self._netloc_to_host_port(parsed_url.netloc)
        self.connection = httplib.HTTPConnection(host, port)
        kwargs = {}
        headers = self._merge_headers(headers)
        if headers is None:
            headers = headers
        else:
            headers = HeadersDict(headers)
        if body is not None:
            if isinstance(body, dict):
                body = urlencode_utf8(body)
            if 'content-type' not in headers:
                headers['content-type'] = 'application/x-www-form-urlencoded'
            # cherrypy refuses to process x-www-form-urlencoded without
            # a content length
            if len(body) == 0:
                headers['content-length'] = 0
        else:
            # apparently content type is set to x-www-form-urlencoded
            # even when there is no body specified, which proceeds
            # to break cherrypy per above
            headers['content-length'] = 0
        
        # XXX cherrypy waits for keep-alives to expire, work around that
        if headers is None:
            headers = {}
        else:
            headers = HeadersDict(headers)
        headers['connection'] = 'close'
        
        uri = parsed_url.uri
        if query is not None:
            if isinstance(query, dict):
                encoded_query = urlencode_utf8(query)
            elif isinstance(query, basestring):
                encoded_query = query
            else:
                raise ValueError, 'Query string is neither a string nor a dict'
            # XXX handle url also having a query
            uri += '?' + encoded_query
        
        self.connection.request(method.upper(), uri, body, headers)
        self.response = Response(self.connection.getresponse())
        for cookie in self.response.cookie_list:
            self._cookie_jar.add(cookie)
    
    def _netloc_to_host_port(self, netloc):
        if netloc:
            if ':' in netloc:
                host, port = netloc.split(':')
                return (host, int(port))
            else:
                return (netloc, self._default_port)
        else:
            # url contained path only
            return (self._default_host, self._default_port)
    
    # note: cherrypy webtest has a protocol argument
    def get(self, url, **kwargs):
        return self.request('get', url, **kwargs)
    
    def post(self, url, **kwargs):
        return self.request('post', url, **kwargs)
    
    def assert_status(self, code):
        if code == 'redirect':
            ok = self.response.code in (301, 302, 303)
        else:
            ok = self.response.code == code
        if not ok:
            msg = 'Response status %s expected but was %s' % (code, self.response.code)
            if self.response.code == 500:
                extra = self.test_case.get_500_extra_message()
                if extra:
                    msg += "\n" + extra
            if self.config.save_failed_responses:
                if len(self.response.body) > 0:
                    if self.config.save_dir is not None:
                        basename = 'response_%f' % _time.time()
                        with open(os.path.join(self.config.save_dir, basename), 'wb') as f:
                            f.write(self.response.body)
                    else:
                        msg += "\nCould not save response body - save_dir is None"
            assert False, msg
    
    def assert_redirected_to_uri(self, target):
        self.assert_status('redirect')
        self.assert_equal(target, self.response.location_uri)
    
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
    
    def clear_cookie_jar(self):
        self._cookie_jar = ocookie.CookieJar()
    
    def _absolutize_url(self, url):
        if url.startswith('/'):
            # convert to absolute url
            if self.config.host is None:
                raise ValueError, 'Url is only a path and host is not specified in configuration: %s' % url
            match = re.match(r'((\w+)://)?([^:]+)(:(\d+))?$', self.config.host)
            if not match:
                raise ValueError, 'Default host is malformed: %s' % self.config.host
            if self.config.protocol is not None:
                protocol = self.config.protocol
            elif match.group(1):
                protocol = match.group(2)
            else:
                protocol = None
            host = match.group(3)
            if self.config.port is not None:
                port = self.config.port
            elif match.group(4):
                port = match.group(5)
            else:
                port = None
            
            if protocol is None:
                if port == 443:
                    protocol = 'https'
                else:
                    protocol = 'http'
            prefix = '%s://%s' % (protocol, host)
            if port is not None:
                prefix += ':%s' % port
            # prefix has no trailing slash, url has a leading slash
            url = prefix + url
        elif not re.match(r'\w+://', url):
            raise ValueError, 'Url must either be an absolute url or an absolute path: %s' % url
        return url

class WebTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(WebTestCase, self).__init__(*args, **kwargs)
        # XXX does not inherit
        self.config = getattr(self.__class__, '_config', None) or Config()
    
    def setUp(self):
        super(WebTestCase, self).setUp()
        self._session = self._create_session()
    
    def _create_session(self):
        kwargs = {}
        if hasattr(self.__class__, 'DEFAULT_NETLOC'):
            kwargs['default_netloc'] = self.__class__.DEFAULT_NETLOC
        kwargs['config'] = self.config
        kwargs['test_case'] = self
        return Session(**kwargs)
    
    def session(self):
        session = self._create_session()
        return session
    
    @property
    def response(self):
        return self._session.response
    
    def request(self, method, url, **kwargs):
        if hasattr(self, '_no_session') and self._no_session:
            self._session = self._create_session()
        return self._session.request(method, url, **kwargs)
    
    def get(self, url, **kwargs):
        return self.request('get', url, **kwargs)
    
    def post(self, url, **kwargs):
        return self.request('post', url, **kwargs)
    
    def assert_raises(self, expected, *args):
        if args:
            return self.assertRaises(expected, *args)
        else:
            return AssertRaisesContextManager(expected)
    
    def assert_status(self, code):
        self._session.assert_status(code)
    
    def assert_redirected_to_uri(self, target):
        self._session.assert_redirected_to_uri(target)
    
    def assert_response_cookie(self, name, **kwargs):
        self._session.assert_response_cookie(name, **kwargs)
    
    def assert_not_response_cookie(self, name):
        self._session.assert_not_response_cookie(name)
    
    def assert_session_cookie(self, name, **kwargs):
        self._session.assert_session_cookie(name, **kwargs)
    
    def assert_not_session_cookie(self, name):
        self._session.assert_not_session_cookie(name)
    
    def get_500_extra_message(self):
        return None
    
    @property
    def cookie_dict(self):
        return self._session.cookie_dict
    
    @property
    def header_list(self):
        return self._session.header_list
    
    @property
    def header_dict(self):
        return self._session.header_dict

def no_session(cls):
    '''Class decorator requesting that session management should not be
    performed.
    '''
    
    cls._no_session = True
    return cls

def config(**kwargs):
    '''Class decorator for setting configuration on test cases.'''
    
    def decorator(cls):
        config = getattr(cls, '_config', None) or Config()
        for name in kwargs:
            setattr(config, name, kwargs[name])
        cls._config = config
        return cls
    return decorator

class Form(object):
    def __init__(self, form_tag):
        self._form_tag = form_tag
    
    @property
    def action(self):
        return self._form_tag.attrib.get('action')
    
    @property
    def method(self):
        return self._form_tag.attrib.get('method')

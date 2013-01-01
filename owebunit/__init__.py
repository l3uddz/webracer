# Note: responses are assumed to be immutable.

import functools
import httplib
import os.path
import re
import time as _time
import unittest
import urllib
import urlparse
import ocookie.httplibadapter

def is_mapping(value):
    '''Returns True if value is of a mapping type such as a dictionary,
    and False otherwise.
    '''
    
    # http://stackoverflow.com/questions/3854470/how-to-distinguish-between-a-sequence-and-a-mapping
    return hasattr(value, 'keys')

def is_container(value):
    '''Returns True if value is of a container type such as a list, tuple
    or a dictionary, but not a string, and False otherwise.
    '''
    
    # sequence or mapping, but not a string as strings are mappings
    return hasattr(value, '__getitem__') and not isinstance(value, basestring)

def is_string(value):
    '''Returns True if value is a string, and False otherwise.
    '''
    
    return isinstance(value, basestring)

def immutable(func):
    @functools.wraps(func)
    def decorated(self):
        if not getattr(self, '_cache', None):
            self._cache = {}
        name = func.__name__
        if name not in self._cache:
            value = func(self)
            self._cache[name] = value
        else:
            value = self._cache[name]
        return value
    return decorated

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
            self._cookie_list = ocookie.httplibadapter.parse_response_cookies(
                self.httplib_response
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
        if getattr(self, '_forms', None) is None:
            doc = self.lxml_etree
            self._forms = [Form(form_tag, self) for form_tag in doc.xpath('//form')]
        return self._forms

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
    if is_mapping(params):
        # assume a dictionary type
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
    else:
        # assume a list of pairs
        # http://docs.python.org/2/library/urllib.html#urllib.urlencode
        for pair in params:
            encoded.append(pair[0] + '=' + _urlencode_value(pair[1]))
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
            if is_container(body):
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
            if is_string(query):
                encoded_query = query
            elif hasattr(query, '__getitem__'):
                # sequence or mapping
                encoded_query = urlencode_utf8(query)
            else:
                raise ValueError, 'Query string is neither a string, a sequence nor a dict'
            # XXX handle url also having a query
            uri += '?' + encoded_query
        
        self.connection.request(method.upper(), uri, body, headers)
        self.response = Response(self.connection.getresponse())
        # XXX consider not writing attributes from here
        self.response.request_url = url
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
    
    def follow_redirect(self):
        assert 'location' in self.response.header_dict
        return self.get(self.response.location)
    
    def assert_status(self, code):
        if code == 'redirect':
            ok = self.response.code in (301, 302, 303)
        else:
            ok = self.response.code == code
        if not ok:
            msg = 'Response status %s expected but was %s' % (code, self.response.code)
            if 'location' in self.response.header_dict:
                msg += ' (to %s)' % self.response.header_dict['location']
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
    
    def follow_redirect(self):
        return self._session.follow_redirect()
    
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

class FormParams(object):
    def __init__(self, params, **kwargs):
        self.params = params
        self.options = kwargs
    
    @property
    def list(self):
        '''Returns a list of parameters that the form will submit.
        
        Return value is a list of (name, value) pairs. Multiple pairs
        may have the same name.
        
        Note: does not include parameters in form's action.
        
        Form elements that do not have name or value attributes are ignored.
        '''
        
        filtered_params = []
        if 'submit_name' in self.options:
            submit_name = self.options['submit_name']
        else:
            submit_name = None
            submit_found = False
        for tag, type, name, value in self.params:
            if tag == 'input' and type == 'submit':
                # allow only one submit element to provide a value.
                if submit_name:
                    if name != submit_name:
                        continue
                else:
                    if submit_found:
                        continue
                    submit_found = True
            filtered_params.append((name, value))
        return filtered_params
    
    @property
    def dict(self):
        '''Returns a dictionary of parameters that the form will submit.
        
        If there are multiple parameters with the same name, the last
        parameter in document is used.
        
        Note: does not include parameters in form's action.
        
        Form elements that do not have name or value attributes are ignored.
        '''
        
        # XXX optimize?
        return dict(self.list)
    
    def submit(self, name):
        found = False
        for tag, type, name_, value in self.params:
            if tag == 'input' and type == 'submit' and name == name_:
                found = True
                break
        if not found:
            raise ValueError, '"%s" is not a named submit element with a value on this form' % name
        options = dict(self.options)
        options['submit_name'] = name
        return FormParams(self.params, **options)

class Form(object):
    def __init__(self, form_tag, response):
        self._form_tag = form_tag
        self._response = response
    
    @property
    def action(self):
        return self._form_tag.attrib.get('action')
    
    @property
    @immutable
    def computed_action(self):
        '''The url that the form should submit to.
        '''
        
        return urlparse.urljoin(self._response.request_url, self.action)
    
    @property
    def method(self):
        return self._form_tag.attrib.get('method')
    
    @property
    @immutable
    def computed_method(self):
        '''The method that should be used to submit the form.
        
        If a method is given in the form, it is lowercased and returned.
        
        Otherwise, the default method of 'get' is returnd.
        '''
        
        method = self.method
        if method:
            method = method.lower()
        else:
            method = 'get'
        return method
    
    @property
    def params(self):
        params = []
        for element in self._form_tag.xpath('.//*[self::input or self::button or self::textarea or self::select]'):
            if 'name' not in element.attrib:
                continue
            if element.tag == 'select':
                options = element.xpath('.//option')
                # try to find a selected option;
                # use the last selected option if more than one is selected
                value = None
                for option in options:
                    # browsers differ on which values for selected attribute
                    # constitute the selection being active.
                    # consider presence of the attribute as the indicator
                    # that the option is selected.
                    # http://stackoverflow.com/questions/1033944/what-values-can-appear-in-the-selected-attribute-of-the-option-tag
                    if 'selected' in option.attrib:
                        # if the selected element has no value,
                        # clear the selected value.
                        # if there are multiple selected options,
                        # this may result in not having a value for the select
                        # despite some (earlier) selected options having values.
                        # XXX handle multiple selection selects
                        value = option.attrib.get('value')
                if value is None:
                    # get the first option as that will be selected
                    # by the browser
                    if len(options) > 0:
                        option = options[0]
                        # the first option may not have a value, in which case
                        # we won't return a value as well
                        value = option.attrib.get('value')
            else:
                value = element.attrib.get('value')
            if value is not None:
                params.append((element.tag, element.attrib.get('type'), element.attrib['name'], value))
        return FormParams(params)

def extend_params(target, extra):
    '''Extends a target parameter list, which can be a sequence or a mapping,
    with additional parameters which can also be a sequence or a mapping.
    
    The type of return value matches the type of target.
    
    No duplicate elimination is performed. Sequences can be added to sequences,
    dictionaries can be added to sequences but sequences cannot be added to
    dictionaries.
    
    Note: target is mutated unless it is a tuple, in which case a new list
    is returned.
    '''
    
    if is_mapping(target):
        if is_mapping(extra):
            target.update(extra)
        else:
            raise ValueError, "Mappings can only be extended with other mappings"
    elif is_container(target):
        # if target is a tuple we have to convert it to a list first
        # as tuples are immutable
        if type(target) == tuple:
            target = list(target)
        if is_mapping(extra):
            target.extend(extra.items())
        elif is_container(extra):
            target.extend(extra)
        else:
            raise ValueError, 'Unsupported type for extra: %s' % type(extra)
    else:
        raise ValueError, 'Unsupported type for target: %s' % type(target)
    return target

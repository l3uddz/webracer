# Note: responses are assumed to be immutable.

import sys
import functools
import os
import os.path
import re
import time as _time
import xml.sax.saxutils
import ocookie.httplib_adapter
import cidict

py3 = sys.version_info[0] == 3

# python 2/3 compatibility
if py3:
    import http.client as httplib
    import urllib.parse as urlparse
    base_exception_class = Exception
    string_type = str
else:
    import httplib
    import urllib
    import urlparse
    base_exception_class = StandardError
    string_type = basestring

class ConfigurationError(base_exception_class):
    pass

class NoForms(base_exception_class):
    pass

class MultipleForms(base_exception_class):
    pass

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
    return hasattr(value, '__getitem__') and not isinstance(value, string_type)

def is_string(value):
    '''Returns True if value is a string, and False otherwise.
    '''
    
    return isinstance(value, string_type)

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
    
    user_agent = None
    
    # If True, all responses will be saved in a directory specified by
    # save_dir.
    save_responses = False
    # If True, responses whose statuses are unexpected will be saved
    # in a directory specified by save_dir.
    # assert_status must be called for check response status.
    save_failed_responses = False
    save_dir = None
    
    # A function that will be invoked with a session argument to retrieve
    # any additional diagnostics for the response, if response status is 500.
    # Mostly this is useful when the application being tested exists in
    # the same process as the test suite, and the test suite has the ability
    # to e.g. obtain a stack trace that is not otherwise exposed by the
    # application.
    extra_500_message = None
    
    # Override session class to use. Allows defining additional helper methods
    # on session objects.
    session_class = None

class Response(object):
    def __init__(self, httplib_response):
        self.httplib_response = httplib_response
    
    @property
    def code(self):
        return self.httplib_response.status
    
    @property
    @immutable
    def raw_body(self):
        '''Returns the raw response body.
        
        In Python 3, this returns the bytes of the response.
        In Python 2, this is identical to body.
        '''
        
        # read() can only be called once, immutable decorator achieves this
        return self.httplib_response.read()
    
    @property
    @immutable
    def body(self):
        '''Returns the response body.
        
        In Python 3, this returns the response decoded into a string.
        In Python 2, this is identical to raw_body.
        '''
        
        if py3:
            return self.raw_body.decode('utf8')
        else:
            return self.raw_body
    
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
    @immutable
    def lxml_etree_xml(self):
        '''Returns an lxml.etree built from response body, treating
        the latter as XML.'''
        
        import lxml.etree
        
        doc = lxml.etree.XML(self.body)
        return doc
    
    @property
    @immutable
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
            self._cookie_list = ocookie.httplib_adapter.parse_response_cookies(
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
        map = cidict.cidict()
        for key, value in header_list:
            map[key] = value
        return map
    
    @property
    def location(self):
        headers = self.header_dict
        if 'location' in headers:
            return headers['location']
        else:
            raise ValueError('There is no location header in this response')
    
    @property
    def location_uri(self):
        '''Location with the host/port stripped, for ease of asserting.'''
        
        location = self.location
        # XXX could do this via parseurl
        location = re.sub(r'^\w+://[^/]+', '', location)
        location = re.sub(r'^//[^/]+', '', location)
        return location
    
    @property
    @immutable
    def forms(self):
        '''Returns forms in the response.
        
        By default, all forms are returned.
        
        It is possible to restrict forms to only ones matching specified
        XPath expression, CSS selector, name or id attributes via
        FormsCollection.__call__.
        '''
        
        return FormsCollection(self.lxml_etree, self)
    
    @property
    def form(self):
        return FormProxy(self.forms)

class FormElements(object):
    def __init__(self, elements):
        self.elements = elements
        self.submit_name = None
        self.chosen_values = {}
    
    @property
    def params(self):
        params = []
        selected_selects = {}
        for element_type, element_name, element_value, element_selected in self.elements:
            if element_name is None or element_type == 'reset':
                continue
            # first pass: figure out which values to send when
            # the last value should be chosen
            if element_type == 'option':
                if element_name in self.chosen_values:
                    # XXX rewrites destination if multiple options are present
                    # for the given select tag
                    selected_selects[element_name] = self.chosen_values[element_name]
                elif element_selected:
                    selected_selects[element_name] = element_value
                else:
                    # the first option should become selected
                    if element_name not in selected_selects:
                        selected_selects[element_name] = element_value
            elif element_type == 'radio':
                # XXX completely duplicated
                if element_name in self.chosen_values:
                    # XXX rewrites destination if multiple options are present
                    # for the given select tag
                    selected_selects[element_name] = self.chosen_values[element_name]
                elif element_selected:
                    selected_selects[element_name] = element_value
        
        processed_selects = {}
        submit_found = False
        for element_type, element_name, element_value, element_selected in self.elements:
            if element_name is None or element_type == 'reset':
                continue
            # second pass: actually build the parameter list
            if element_type == 'option':
                selected_value = selected_selects.get(element_name)
                # avoid creating multiple params when there are several
                # options with the same value.
                # if there are multiple options without a value and there
                # is no selected value and the valueless options come first,
                # send the first one. otherwise send the last one
                if element_value == selected_value and element_name not in processed_selects:
                    params.append((element_name, element_value))
                    processed_selects[element_name] = True
            else:
                if element_type == 'submit':
                    if not submit_found:
                        if self.submit_name is not None:
                            found = self.submit_name == element_name
                        else:
                            found = True
                        if found:
                            if element_value is not None:
                                params.append((element_name, element_value))
                            submit_found = True
                elif element_name in self.chosen_values:
                    if element_type == 'radio' or element_type == 'checkbox' or \
                        element_type == 'option':
                            if self.chosen_values[element_name] == element_value:
                                params.append((element_name, element_value))
                    else:
                        params.append((element_name, self.chosen_values[element_name]))
                        # XXX record that element_name was processed and
                        # do not process it again?
                elif element_type == 'radio' and element_name in selected_selects:
                    if selected_selects[element_name] == element_value:
                        params.append((element_name, element_value))
                elif element_type == 'checkbox':
                    if element_selected:
                        params.append((element_name, element_value))
                elif element_value is not None:
                    if element_type == 'radio':
                        ok = element_name not in processed_selects
                    else:
                        ok = True
                    if ok:
                        params.append((element_name, element_value))
                        processed_selects[element_name] = True
        return FormParams(params)
    
    @property
    def mutable(self):
        return MutableFormElements(self.elements)

class MutableFormElements(FormElements):
    def submit(self, name):
        found = False
        for element_type, element_name, element_value, element_selected in self.elements:
            if element_type == 'submit' and element_name == name:
                found = True
                break
        if not found:
            raise ValueError('"%s" is not a named submit element with a value on this form' % name)
        self.submit_name = name
    
    def set_value(self, name, value):
        '''Sets form element identified by the given name to the specified
        value.
        
        This method attempts to mimic closely what a human user could do with
        a typical web browser. Therefore:
        
        - The element identified by `name` must exist on the form.
        - The element must be of a type which allows user to change its value.
          For example, text, radio, checkbox, textarea, select, etc.
          Elements of unknown types are assumed to be user-changeable.
          submit, reset and image type elements are rejected by this method;
          to specify which submit element should be used, use `submit` method.
        '''
        
        found = False
        found_rejected = None
        for element_type, element_name, element_value, element_selected in self.elements:
            if element_name == name:
                if element_type == 'submit' or element_type == 'image' or \
                    element_type == 'reset' or element_type == 'button':
                        found_rejected = 'Wrong element type: %s' % element_type
                elif element_type == 'radio' or element_type == 'checkbox' or \
                    element_type == 'option':
                        if element_value == value:
                            found = True
                        else:
                            found_rejected = 'Element `%s` does not have `%s` as a possible value' % (name, value)
                else:
                    # assume it's a text field or similar, e.g. email in html5
                    found = True
            if found:
                self.chosen_values[name] = value
                break
        if not found and found_rejected:
            raise ValueError(found_rejected)

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
        
        return self.params
    
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

class Form(object):
    def __init__(self, form_tag, response):
        self._form_tag = form_tag
        self._response = response
    
    @property
    def name(self):
        return self._form_tag.attrib.get('name')
    
    @property
    def id(self):
        return self._form_tag.attrib.get('id')
    
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
            method = method.upper()
        else:
            method = 'GET'
        return method
    
    @property
    def elements(self):
        '''Returns all elements of the form.
        
        Elements without names or values are returned also, because selecting
        e.g. a submit button without a name will not send any other submit
        element names' with the form submission.
        
        For selects, the list of their options is returned, with select
        name added to each of the options. Other tags are returned as is.
        '''
        
        elements = []
        for element in self._form_tag.xpath('.//*[self::input or self::button or self::textarea or self::select]'):
            name = element.attrib.get('name')
            if element.tag == 'select':
                # XXX check if options must be direct descendants of selects
                for option in element.xpath('./option'):
                    # browsers differ on which values for selected attribute
                    # constitute the selection being active.
                    # consider presence of the attribute as the indicator
                    # that the option is selected.
                    # http://stackoverflow.com/questions/1033944/what-values-can-appear-in-the-selected-attribute-of-the-option-tag
                    selected = 'selected' in option.attrib
                    elements.append(('option', name, option.attrib.get('value'), selected))
            elif element.tag == 'textarea':
                # textareas always have a value
                value = element.text or ''
                elements.append(('textarea', name, value, None))
            else:
                if element.tag == 'input' and 'type' in element.attrib and \
                    element.attrib['type'] in ('radio', 'checkbox'):
                        selected = 'checked' in element.attrib
                else:
                    selected = None
                # use type attribute for element type, unless it is empty
                # in which case us tag name
                if 'type' in element.attrib:
                    element_type = element.attrib['type']
                else:
                    element_type = element.tag
                elements.append((element_type, name, element.attrib.get('value'), selected))
        return FormElements(elements)
    
    @property
    def params(self):
        return self.elements.params
    
    def __repr__(self):
        bits = ['owebunit.Form']
        for prop in ['id', 'name', 'action', 'method']:
            value = getattr(self, prop)
            if value is not None:
                bits.append('%s=%s' % (prop, xml.sax.saxutils.quoteattr(value)))
        return '<%s>' % ' '.join(bits)

def _implement_form_property(prop):
    @property
    def getter(self):
        self._materialize()
        return getattr(self.form, prop)
    return getter

def _format_form_query(**kwargs):
    items = []
    for key in kwargs:
        items.append('%s=%s' % (key, xml.sax.saxutils.quoteattr(kwargs[key])))
    return ' and '.join(items)

class FormProxy(object):
    def __init__(self, collection):
        self.collection = collection
    
    action = _implement_form_property('action')
    computed_action = _implement_form_property('computed_action')
    method = _implement_form_property('method')
    computed_method = _implement_form_property('computed_method')
    elements = _implement_form_property('elements')
    params = _implement_form_property('params')
    name = _implement_form_property('name')
    id = _implement_form_property('id')
    
    def __call__(self, **kwargs):
        forms = self.collection(**kwargs)
        self._check_length(forms, **kwargs)
        return forms[0]
    
    def _materialize(self):
        forms = self.collection()
        self._check_length(forms)
        self.form = forms[0]
    
    def _check_length(self, forms, **kwargs):
        if len(forms) == 0:
            if kwargs:
                msg = 'No forms matched %s' % _format_form_query(**kwargs)
            else:
                msg = 'No forms were found'
            raise NoForms(msg)
        elif len(forms) > 1:
            raise MultipleForms('Multiple (%d) forms were found' % len(forms))

class FormsCollection(object):
    def __init__(self, doc, response):
        self.doc = doc
        self.response = response
        self.all_forms = None
    
    def __call__(self, xpath=None, css=None, name=None, id=None):
        '''Returns forms matching a specified XPath expression, CSS selector,
        name or id attributes.
        
        Multiple restrictions can be specified, in which case only forms
        matching all conditions will be returned.
        '''
        
        if xpath is not None:
            forms = self.doc.xpath(xpath)
            if len(forms) == 0:
                return forms
        else:
            forms = None
        
        if css is not None:
            import lxml.cssselect
            selector = lxml.cssselect.CSSSelector(css)
            css_forms = selector(self.doc)
            if len(css_forms) == 0:
                return css_forms
            if forms is None:
                forms = css_forms
            else:
                forms = [form for form in forms if form in css_forms]
        
        # restrict to form tags
        if forms is not None:
            # note: xpath may have selected text nodes, thus
            # hasattr check
            forms = [form for form in forms if hasattr(form, 'tag') and form.tag == 'form']
        
        if name is not None or id is not None:
            if forms is None:
                conditions = []
                if name is not None:
                    conditions.append('@name=%s' % xml.sax.saxutils.quoteattr(name))
                if id is not None:
                    conditions.append('@id=%s' % xml.sax.saxutils.quoteattr(id))
                xpath = ' and '.join(conditions)
                xpath = '//form[%s]' % xpath
                forms = self.doc.xpath(xpath)
            else:
                if name is not None:
                    forms = [form for form in forms if form.attrib.get('name') == name]
                if id is not None:
                    forms = [form for form in forms if form.attrib.get('id') == id]
        
        if forms is None:
            # no conditions specified, return all forms
            self._initialize_all_forms()
            forms = self.all_forms
        
        return [Form(form, self.response) for form in forms]
    
    # treating FormCollection as a list of (all) forms
    def __len__(self):
        self._initialize_all_forms()
        return len(self.all_forms)
    
    def __getitem__(self, index):
        self._initialize_all_forms()
        return Form(self.all_forms[index], self.response)
    
    def __iter__(self):
        self._initialize_all_forms()
        forms = [Form(form, self.response) for form in self.all_forms]
        return iter(forms)
    
    def _initialize_all_forms(self):
        if self.all_forms is None:
            self.all_forms = self.doc.xpath('//form')

def uri(self):
    uri = self.path or '/'
    if self.params:
        uri += ';' + self.params
    if self.query:
        uri += '?' + self.query
    return uri

# XXX figure out if this is still needed and give it a better api
def parse_url(url):
    parsed_url = urlparse.urlparse(url)
    _uri = uri(parsed_url)
    return parsed_url, _uri

if py3:
    def _urlencode_value(value):
        '''Encodes value, first converting it to string if necessary.
        
        value should be either a string or something with a meaningful
        conversion to string, such as a number.
        
        If value is of bytes type, behavior is undefined.
        '''
        
        if type(value) != str:
            value = str(value)
        return urlparse.quote(value)
else:
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
        # Check for passing a list/tuple of two strings instead of a
        # one-element list/tuple - easy mistake to make
        if len(params) == 2 and type(params) in [list, tuple] and is_string(params[0]):
            raise ValueError('Parameter must be a sequence of pairs, not a pair itself')
        # assume a list of pairs
        # http://docs.python.org/2/library/urllib.html#urllib.urlencode
        for pair in params:
            encoded.append(pair[0] + '=' + _urlencode_value(pair[1]))
    return '&'.join(encoded)

class Session(object):
    def __init__(self, config=None, default_netloc=None):
        self.config = config or Config()
        self._cookie_jar = ocookie.CookieJar()
        if default_netloc:
            self._default_host, self._default_port = default_netloc.split(':')
        else:
            self._default_host, self._default_port = None, None
    
    def request(self, method, url, body=None, query=None, headers=None):
        url = self._absolutize_url(url)
        parsed_url, uri = parse_url(url)
        host, port = self._netloc_to_host_port(parsed_url.netloc)
        self.connection = httplib.HTTPConnection(host, port)
        kwargs = {}
        computed_headers = self._build_initial_headers()
        self._merge_headers(computed_headers, headers)
        if body is not None:
            if is_container(body):
                body = urlencode_utf8(body)
            if 'content-type' not in computed_headers:
                computed_headers['content-type'] = 'application/x-www-form-urlencoded'
            # cherrypy refuses to process x-www-form-urlencoded without
            # a content length
            if len(body) == 0:
                computed_headers['content-length'] = 0
        else:
            # apparently content type is set to x-www-form-urlencoded
            # even when there is no body specified, which proceeds
            # to break cherrypy per above
            computed_headers['content-length'] = 0
        
        # XXX cherrypy waits for keep-alives to expire, work around that
        computed_headers['connection'] = 'close'
        
        if query is not None:
            if is_string(query):
                encoded_query = query
            elif hasattr(query, '__getitem__'):
                # sequence or mapping
                encoded_query = urlencode_utf8(query)
            else:
                raise ValueError('Query string is neither a string, a sequence nor a dict')
            # XXX handle url also having a query
            uri += '?' + encoded_query
        
        self.connection.request(method.upper(), uri, body, computed_headers)
        self.response = Response(self.connection.getresponse())
        # XXX consider not writing attributes from here
        self.response.request_url = url
        for cookie in self.response.cookie_list:
            self._cookie_jar.add(cookie)
        if self.config.save_responses:
            self._save_response()
    
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
                if self.config.extra_500_message:
                    extra = self.config.extra_500_message()
                else:
                    extra = None
                if extra:
                    msg += "\n" + extra
            if self.config.save_failed_responses and not self.config.save_responses:
                try:
                    self._save_response()
                except e:
                    msg += "\n" + str(e)
            assert False, msg
    
    def _save_response(self):
        if len(self.response.body) > 0:
            if self.config.save_dir is not None:
                basename = 'response_%f' % _time.time()
                with open(os.path.join(self.config.save_dir, basename), 'wb') as f:
                    f.write(self.response.body)
                last_path = os.path.join(self.config.save_dir, 'last')
                if os.path.exists(last_path):
                    os.unlink(last_path)
                os.symlink(basename, last_path)
            else:
                raise ConfigurationError('Could not save response body - save_dir is None')
    
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
            if 'value' in kwargs:
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
    
    def _build_initial_headers(self):
        # We do not set multiple headers ourselves and therefore
        # can use a dictionary for headers
        headers = cidict.cidict()
        
        if self.config.user_agent is not None:
            headers['user-agent'] = self.config.user_agent
        
        return headers
    
    def _merge_headers(self, computed_headers, user_headers):
        if isinstance(user_headers, list) or isinstance(user_headers, tuple):
            # convert to a dictionary for httplib
            map = {}
            for key, value in user_headers:
                if key in map:
                    raise ValueError('Duplicate headers are not supported by httplib')
                map[key] = value
            user_headers = map
        
        if self._cookie_jar:
            if user_headers is not None and 'cookie' in user_headers:
                value = self._merge_cookie_header_values(user_headers['cookie'])
            else:
                value = self._cookie_jar.build_cookie_header_value()
        else:
            value = None
        if value:
            computed_headers['cookie'] = value
        
        if user_headers is not None:
            # need to exclude cookie headers since we already handled them
            for key in user_headers:
                if key.lower() != 'cookie':
                    computed_headers[key] = user_headers[key]
    
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
                raise ValueError('Url is only a path and host is not specified in configuration: %s' % url)
            match = re.match(r'((\w+)://)?([^:]+)(:(\d+))?$', self.config.host)
            if not match:
                raise ValueError('Default host is malformed: %s' % self.config.host)
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
            raise ValueError('Url must either be an absolute url or an absolute path: %s' % url)
        return url

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
            raise ValueError("Mappings can only be extended with other mappings")
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
            raise ValueError('Unsupported type for extra: %s' % type(extra))
    else:
        raise ValueError('Unsupported type for target: %s' % type(target))
    return target

from .case import *

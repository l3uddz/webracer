import unittest
from .session import Config, Session

# XXX bring into compliance with python 2.7 unittest api
class AssertRaisesContextManager(object):
    def __init__(self, expected):
        self.expected = expected
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        if type is None:
            raise AssertionError('%s expected but not raised' % str(self.expected))
        if type != self.expected:
            raise AssertionError('%s expected, not `%s`' % (self.expected.__class__, str(value)))
        self.exception = value
        # silence exception
        return True

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
        kwargs['config'] = self.config
        session_class = self.config.session_class or Session
        return session_class(**kwargs)
    
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
    
    # XXX move to utu
    # XXX accept kwargs
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

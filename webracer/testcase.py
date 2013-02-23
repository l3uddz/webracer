import types
import functools
import unittest
from .agent import Config, Agent

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
        self._agent = self._create_agent()
    
    def _create_agent(self):
        kwargs = {}
        kwargs['config'] = self.config
        agent_class = self.config.agent_class or Agent
        return agent_class(**kwargs)
    
    def agent(self):
        agent = self._create_agent()
        return agent
    
    @property
    def response(self):
        return self._agent.response
    
    def request(self, method, url, *args, **kwargs):
        if hasattr(self, '_no_session') and self._no_session:
            self._agent = self._create_agent()
        return self._agent.request(method, url, *args, **kwargs)
    
    def get(self, url, *args, **kwargs):
        return self.request('get', url, *args, **kwargs)
    
    def post(self, url, *args, **kwargs):
        return self.request('post', url, *args, **kwargs)
    
    def follow_redirect(self):
        return self._agent.follow_redirect()
    
    # XXX move to utu
    # XXX accept kwargs
    def assert_raises(self, expected, *args):
        if args:
            return self.assertRaises(expected, *args)
        else:
            return AssertRaisesContextManager(expected)
    
    def assert_status(self, code):
        self._agent.assert_status(code)
    
    def assert_redirected_to_uri(self, target):
        self._agent.assert_redirected_to_uri(target)
    
    def assert_response_cookie(self, name, **kwargs):
        self._agent.assert_response_cookie(name, **kwargs)
    
    def assert_not_response_cookie(self, name):
        self._agent.assert_not_response_cookie(name)
    
    def assert_cookie_jar_cookie(self, name, **kwargs):
        self._agent.assert_cookie_jar_cookie(name, **kwargs)
    
    def assert_not_cookie_jar_cookie(self, name):
        self._agent.assert_not_cookie_jar_cookie(name)
    
    @property
    def cookies(self):
        return self._agent.response.cookies
    
    @property
    def raw_headers(self):
        return self._agent.raw_headers
    
    @property
    def headers(self):
        return self._agent.headers

def no_session(cls):
    '''Class decorator requesting that session management should not be
    performed.
    '''
    
    cls._no_session = True
    return cls

def config(**kwargs):
    '''Function and class decorator for setting configuration on test cases.'''
    
    def decorator(cls_or_fn):
        if isinstance(cls_or_fn, types.FunctionType):
            fn = cls_or_fn
            @functools.wraps(fn)
            def decorated(self):
                saved = {}
                for key in kwargs:
                    saved[key] = getattr(self.config, key)
                    setattr(self.config, key, kwargs[key])
                try:
                    fn(self)
                finally:
                    for key in kwargs:
                        setattr(self.config, key, saved[key])
            return decorated
        else:
            cls = cls_or_fn
            config = getattr(cls, '_config', None) or Config()
            for name in kwargs:
                setattr(config, name, kwargs[name])
            cls._config = config
            return cls
    return decorator

import unittest
import httplib
import urlparse

class Response(object):
    def __init__(self, httplib_response):
        self.httplib_response = httplib_response
    
    @property
    def code(self):
        return self.httplib_response.status

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

class Session(object):
    def get(self, url):
        parsed_url = parse_url(url)
        self.connection = httplib.HTTPConnection(*parsed_url.netloc.split(':'))
        self.connection.request('GET', parsed_url.uri)
        self.response = Response(self.connection.getresponse())
    
    def assert_code(self, code):
        self.assert_equal(code, self.response.code)
    
    def assert_equal(self, expected, actual):
        assert expected == actual
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        pass

class WebTestCase(unittest.TestCase):
    def session(self):
        session = Session()
        return session
    
    def get(self, url):
        self.session = Session()
        self.session.get(url)
    
    def assert_code(self, code):
        self.session.assert_code(code)

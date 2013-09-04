import sys
from . import support
import ocookie.httplib_adapter

py3 = sys.version_info[0] == 3

if py3:
    import http.client as httplib
else:
    import httplib

class Response(object):
    def __init__(self, httplib_response):
        self.httplib_response = httplib_response
    
    @property
    def code(self):
        return self.httplib_response.status
    
    @property
    def raw_body(self):
        return self.httplib_response.read()
    
    @property
    def raw_cookies(self):
        return ocookie.httplib_adapter.parse_response_cookies(
            self.httplib_response
        )
    
    @property
    def raw_headers(self):
        return self.httplib_response.getheaders()

class Client(object):
    def request(self, req):
        parsed_url, uri = support.parse_url(req.url)
        host, port = support.netloc_to_host_port(parsed_url.netloc)
        if parsed_url.scheme == 'https':
            connection_cls = httplib.HTTPSConnection
        else:
            connection_cls = httplib.HTTPConnection
        connection = connection_cls(host, port)
        connection.request(req.method, uri, req.body, req.headers)
        response = Response(connection.getresponse())
        return response

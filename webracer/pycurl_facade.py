import pycurl
import ocookie
import re

try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

class Response(object):
    def __init__(self, curl, buf, headers):
        self.curl = curl
        self.buf = buf
        self.headers = headers
    
    @property
    def code(self):
        return self.curl.getinfo(self.curl.RESPONSE_CODE)
    
    @property
    def raw_body(self):
        return self.buf.getvalue()
    
    @property
    def raw_cookies(self):
        # Not delegating to ocookie because header storage is caller-dependent
        headers = [pair for pair in self.headers if pair[0].lower() in ['set-cookie', 'set-cookie2']]
        cookies = [ocookie.CookieParser.parse_set_cookie_value(value) for key, value in headers]
        return cookies
    
    @property
    def raw_headers(self):
        return self.headers

class Client(object):
    def request(self, req):
        curl = pycurl.Curl()
        # url might be a unicode string,
        # which would need to be encoded for earlier pycurls
        curl.setopt(curl.URL, req.url.encode('iso-8859-1'))
        
        if req.method != 'GET':
            if req.method == 'POST':
                # CUSTOMREQUEST does not work here
                curl.setopt(curl.POST, True)
            else:
                # method might be a unicode string,
                # which would need to be encoded for earlier pycurls
                curl.setopt(curl.CUSTOMREQUEST, req.method.encode('iso-8859-1'))
        
        buf = StringIO()
        curl.setopt(curl.WRITEFUNCTION, buf.write)
        
        if req.body is not None:
            curl.setopt(curl.POSTFIELDS, req.body)
        
        if req.headers is not None:
            header_list = []
            for key in req.headers:
                if ':' in key:
                    raise ValueError('Colon is not allowed in header name: %s' % key)
                # XXX assumes headers is a dict
                value = req.headers[key]
                # XXX very crude
                header = '%s: %s' % (key, value)
                header_list.append(header.encode('iso-8859-1'))
            curl.setopt(curl.HTTPHEADER, header_list)
        
        self.setup_header_parsing(curl)
        curl.perform()
        return Response(curl, buf, self.response_headers)
    
    def setup_header_parsing(self, curl):
        self.response_headers = []
        phase = [0]
        
        def header_function(header_line):
            # this encoding applies to both http status line and headers
            header_line = header_line.decode('iso-8859-1')
            if header_line == "\r\n":
                phase[0] = 2
            if phase[0] == 1:
                name, value = header_line.split(':', 1)
                value = re.sub(r'^ *(.*?)(?:\r\n)?$', r'\1', value)
                self.response_headers.append((name, value))
            if header_line.lower().startswith('http'):
                phase[0] += 1
            return len(header_line)
        curl.setopt(curl.HEADERFUNCTION, header_function)

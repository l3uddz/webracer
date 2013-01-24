import sys
import owebunit
from tests import utils
from tests import kitchen_sink_app

def setup_module():
    utils.start_bottle_server(kitchen_sink_app.app, 8045)
    utils.start_bottle_server(kitchen_sink_app.app, 8046, handler_class=TracebackHandler)

@owebunit.config(host='localhost', port=8045)
class Extra500Test(owebunit.WebTestCase):
    def test_without_extras(self):
        self.get('/unhandled_exception')
        self.assert_status(500)
        
        try:
            self.assert_status(200)
        except AssertionError as e:
            self.assertTrue('This is an unhandled exception' not in str(e))
        else:
            self.assertTrue(False)

_errors = None

def bottle_unhandled_exception_info():
    return _errors

import wsgiref.simple_server
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

class TracebackHandler(wsgiref.simple_server.WSGIRequestHandler):
    def __init__(self, *args, **kwargs):
        # must come before superclass init call
        self._error_file = StringIO()
        wsgiref.simple_server.WSGIRequestHandler.__init__(self, *args, **kwargs)
    
    def get_stderr(self):
        return self._error_file
    
    def handle(self):
        wsgiref.simple_server.WSGIRequestHandler.handle(self)
        
        global _errors
        _errors = self._error_file.getvalue()

@owebunit.config(host='localhost', port=8046,
    extra_500_message=bottle_unhandled_exception_info,
)
class Extra500WithExtraTest(owebunit.WebTestCase):
    def test_with_extra(self):
        self.get('/unhandled_exception')
        self.assert_status(500)
        
        try:
            self.assert_status(200)
        except AssertionError as e:
            self.assertTrue('This is an unhandled exception' in str(e))
        else:
            self.assertTrue(False)

if __name__ == '__main__':
    import unittest
    unittest.main()

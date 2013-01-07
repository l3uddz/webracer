import sys
import owebunit
import utils
import kitchen_sink_app

utils.start_bottle_server(kitchen_sink_app.app, 8045)

@owebunit.config(host='localhost', port=8045)
class Extra500TestCase(owebunit.WebTestCase):
    def test_without_extras(self):
        self.get('/unhandled_exception')
        self.assert_status(500)
        
        try:
            self.assert_status(200)
        except AssertionError, e:
            self.assertTrue('This is an unhandled exception' not in e.message)
        else:
            self.assertTrue(False)

_errors = None

def bottle_unhandled_exception_info():
    return _errors

import wsgiref.simple_server
import cStringIO as StringIO

class TracebackHandler(wsgiref.simple_server.WSGIRequestHandler):
    def __init__(self, *args, **kwargs):
        # must come before superclass init call
        self._error_file = StringIO.StringIO()
        wsgiref.simple_server.WSGIRequestHandler.__init__(self, *args, **kwargs)
    
    def get_stderr(self):
        return self._error_file
    
    def handle(self):
        wsgiref.simple_server.WSGIRequestHandler.handle(self)
        
        global _errors
        _errors = self._error_file.getvalue()

utils.start_bottle_server(kitchen_sink_app.app, 8046, handler_class=TracebackHandler)

@owebunit.config(host='localhost', port=8046,
    extra_500_message=bottle_unhandled_exception_info,
)
class Extra500TestCaseWithExtra(owebunit.WebTestCase):
    def test_with_extra(self):
        self.get('/unhandled_exception')
        self.assert_status(500)
        
        try:
            self.assert_status(200)
        except AssertionError, e:
            self.assertTrue('This is an unhandled exception' in e.message)
        else:
            self.assertTrue(False)

if __name__ == '__main__':
    import unittest
    unittest.main()

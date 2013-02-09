import sys
import webracer
import nose.plugins.attrib
from . import utils
from .apps import kitchen_sink_app

@nose.plugins.attrib.attr('client')
@webracer.config(host='localhost', port=8045)
class Extra500Test(webracer.WebTestCase):
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
    from StringIO import StringIO
except ImportError:
    from io import StringIO

class ErrorSilencingHandler(wsgiref.simple_server.WSGIRequestHandler):
    def __init__(self, *args, **kwargs):
        # must come before superclass init call
        self._error_file = StringIO()
        wsgiref.simple_server.WSGIRequestHandler.__init__(self, *args, **kwargs)
    
    def get_stderr(self):
        return self._error_file

class TracebackHandler(ErrorSilencingHandler):
    def handle(self):
        wsgiref.simple_server.WSGIRequestHandler.handle(self)
        
        global _errors
        _errors = self._error_file.getvalue()

utils.app_runner_setup_multiple(__name__, [
    [kitchen_sink_app.app, 8045, dict(handler_class=ErrorSilencingHandler)],
    [kitchen_sink_app.app, 8046, dict(handler_class=TracebackHandler)],
])

@nose.plugins.attrib.attr('client')
@webracer.config(host='localhost', port=8046,
    extra_500_message=bottle_unhandled_exception_info,
)
class Extra500WithExtraTest(webracer.WebTestCase):
    def test_with_extra(self):
        self.get('/unhandled_exception')
        self.assert_status(500)
        
        try:
            self.assert_status(200)
        except AssertionError as e:
            pass
        else:
            self.fail('Wrong response code: %d (expected 500)' % self.response.code)
        
        self.assertTrue('This is an unhandled exception' in str(e), 'Exception did not have expected additional information: %s' % str(e))

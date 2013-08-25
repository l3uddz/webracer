import webracer
import nose.plugins.attrib
from . import utils
from .apps import kitchen_sink_app

utils.app_runner_setup(__name__, kitchen_sink_app.app, 8062)

@nose.plugins.attrib.attr('client')
class AssertionsTest(webracer.WebTestCase):
    def test_assert_status_equal_single(self):
        self.get('http://127.0.0.1:8062/ok')
        
        # single code
        self.assert_status(200)
        
    def test_assert_status_in_list(self):
        self.get('http://127.0.0.1:8062/ok')
        
        # explicit list
        self.assert_status([200, 302])
        
    def test_assert_status_in_range(self):
        self.get('http://127.0.0.1:8062/ok')
        
        # range
        self.assert_status(range(200, 299))
    
    if not utils.py3:
        def test_assert_status_in_xrange(self):
            self.get('http://127.0.0.1:8062/ok')
            
            # xrange
            self.assert_status(xrange(200, 299))
        
    def test_assert_status_not_equal_single(self):
        self.get('http://127.0.0.1:8062/redirect')
        
        # wrong code
        with self.assert_raises(AssertionError):
            self.assert_status(200)
        
    def test_assert_status_not_in_list(self):
        self.get('http://127.0.0.1:8062/redirect')
        
        # not in list
        with self.assert_raises(AssertionError):
            self.assert_status([200, 400])
        
    def test_assert_status_not_in_range(self):
        self.get('http://127.0.0.1:8062/ok')
        
        # not in range
        with self.assert_raises(AssertionError):
            self.assert_status(range(300, 399))
    
    if not utils.py3:
        def test_assert_status_not_in_xrange(self):
            self.get('http://127.0.0.1:8062/ok')
            
            # not in xrange
            with self.assert_raises(AssertionError):
                self.assert_status(xrange(300, 399))
        
    def test_assert_status_redirect(self):
        self.get('http://127.0.0.1:8062/redirect')
        
        self.assert_status('redirect')
        
    def test_assert_status_not_redirect(self):
        self.get('http://127.0.0.1:8062/ok')
        
        with self.assert_raises(AssertionError):
            self.assert_status('redirect')

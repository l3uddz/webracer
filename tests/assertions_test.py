import webracer
import nose.plugins.attrib
from . import utils
from .apps import kitchen_sink_app

utils.app_runner_setup(__name__, kitchen_sink_app.app, 8062)

@nose.plugins.attrib.attr('client')
@webracer.config(host='localhost', port=8062)
class AssertionsTest(webracer.WebTestCase):
    def test_assert_status_equal_single(self):
        self.get('/ok')
        
        # single code
        self.assert_status(200)
        
    def test_assert_status_in_list(self):
        self.get('/ok')
        
        # explicit list
        self.assert_status([200, 302])
        
    def test_assert_status_in_range(self):
        self.get('/ok')
        
        # range
        self.assert_status(range(200, 299))
    
    if not utils.py3:
        def test_assert_status_in_xrange(self):
            self.get('/ok')
            
            # xrange
            self.assert_status(xrange(200, 299))
        
    def test_assert_status_not_equal_single(self):
        self.get('/redirect')
        
        # wrong code
        with self.assert_raises(AssertionError):
            self.assert_status(200)
        
    def test_assert_status_not_in_list(self):
        self.get('/redirect')
        
        # not in list
        with self.assert_raises(AssertionError):
            self.assert_status([200, 400])
        
    def test_assert_status_not_in_range(self):
        self.get('/ok')
        
        # not in range
        with self.assert_raises(AssertionError):
            self.assert_status(range(300, 399))
    
    if not utils.py3:
        def test_assert_status_not_in_xrange(self):
            self.get('/ok')
            
            # not in xrange
            with self.assert_raises(AssertionError):
                self.assert_status(xrange(300, 399))
        
    def test_assert_status_redirect(self):
        self.get('/redirect')
        
        self.assert_status('redirect')
        
    def test_assert_status_not_redirect(self):
        self.get('/ok')
        
        with self.assert_raises(AssertionError):
            self.assert_status('redirect')
    
    def test_assert_redirected_to_uri(self):
        self.get('/redirect')
        # path only
        self.assert_redirected_to_uri('/found')
    
    def test_assert_redirected_to_url(self):
        self.get('/redirect')
        # full url including protocol and host
        self.assert_redirected_to_url('http://localhost:8062/found')
    
    def test_current_url_when_expecting_200_receiving_404(self):
        self.get('/not-found')
        try:
            self.assert_status(200)
        except AssertionError as e:
            self.assertEqual('Response status 200 expected but was 404 (current url: http://localhost:8062/not-found)', str(e))

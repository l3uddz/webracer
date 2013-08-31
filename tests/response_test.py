import webracer
import nose.plugins.attrib
from . import utils
from .apps import kitchen_sink_app

utils.app_runner_setup(__name__, kitchen_sink_app.app, 8041)

@nose.plugins.attrib.attr('client')
@webracer.config(host='localhost', port=8041)
class ResponseTest(webracer.WebTestCase):
    def test_json_parsing_empty(self):
        self.get('/json/empty')
        self.assert_status(200)
        self.assertEqual({}, self.response.json)
    
    def test_json_parsing_hash(self):
        self.get('/json/hash')
        self.assert_status(200)
        self.assertEqual({'a': 'b'}, self.response.json)
    
    def test_raw_location(self):
        self.get('/relative-redirect')
        self.assertEqual('found', self.response.raw_location)
    
    def test_location_on_relative_redirect(self):
        # should return a full url
        self.get('/relative-redirect')
        self.assertEqual('http://localhost:8041/found', self.response.location)
    
    def test_follow_redirect(self):
        self.get('/redirect_to', query=dict(target='/ok'))
        self.assert_redirected_to_uri('/ok')
        self.follow_redirect()
        self.assert_status(200)
        self.assertEqual('ok', self.response.body)

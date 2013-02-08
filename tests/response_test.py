import webracer
from tests import utils
from tests import kitchen_sink_app

utils.app_runner_setup(__name__, kitchen_sink_app.app, 8041)

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
    
    def test_redirect_assertion(self):
        self.get('/redirect')
        self.assert_redirected_to_uri('/found')
    
    def test_follow_redirect(self):
        self.get('/redirect_to', query=dict(target='/ok'))
        self.assert_redirected_to_uri('/ok')
        self.follow_redirect()
        self.assert_status(200)
        self.assertEqual('ok', self.response.body)

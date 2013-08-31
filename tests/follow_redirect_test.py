import sys
import webracer
import mock
import nose.plugins.attrib
from . import utils
from .apps import kitchen_sink_app

utils.app_runner_setup(__name__, kitchen_sink_app.app, 8061)

@nose.plugins.attrib.attr('client')
@webracer.config(host='localhost', port=8061, follow_redirects=True)
class ConfigClassDecoratorTest(webracer.WebTestCase):
    def test_request(self):
        response = self.get('/redirect')
        self.assert_status(200)
        assert response.body == 'found'
    
    def test_request_with_relative_redirect(self):
        s = webracer.Agent(host='localhost', port=8061, follow_redirects=False)
        s.get('/relative-redirect')
        s.assert_status('redirect')
        # check that the location header has a relative redirect,
        # as bottle helpfully fixes it for us
        self.assertEqual('found', s.response.headers['location'])
        
        response = self.get('/relative-redirect')
        self.assert_status(200)
        assert response.body == 'found'

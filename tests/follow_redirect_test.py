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

import sys
import webracer
import mock
import nose.plugins.attrib
from tests import utils
from .apps import kitchen_sink_app

py3 = sys.version_info[0] == 3

utils.app_runner_setup(__name__, kitchen_sink_app.app, 8054)

@nose.plugins.attrib.attr('client')
class FullUrlTest(webracer.WebTestCase):
    def test_simple(self):
        self.get('http://127.0.0.1:8054/ok')
        self.assert_status(200)

@nose.plugins.attrib.attr('client')
class DefaultHostUrlTest(webracer.WebTestCase):
    def __init__(self, *args, **kwargs):
        super(DefaultHostUrlTest, self).__init__(*args, **kwargs)
        self.config.host = 'http://127.0.0.1:8054'
    
    def test_simple(self):
        self.get('/ok')
        self.assert_status(200)

@nose.plugins.attrib.attr('client')
@webracer.config(host='localhost', port=8054)
class ConfigDecoratorTest(webracer.WebTestCase):
    def test_simple(self):
        self.get('/ok')
        self.assert_status(200)

def mock_http_connection_returning_200():
    response = mock.MagicMock(status=200)
    mock_cls = mock.MagicMock()
    mock_cls.getresponse = mock.MagicMock(return_value=response)
    mock_http_connection = mock.MagicMock()
    mock_http_connection.return_value = mock_cls
    return mock_http_connection

if py3:
    http_connection_class = 'http.client.HTTPConnection'
else:
    http_connection_class = 'httplib.HTTPConnection'

class MockedServerTest(webracer.WebTestCase):
    @mock.patch(http_connection_class, mock_http_connection_returning_200())
    def test_portless_url(self):
        '''Check that our logic for issuing requests does not have any
        local problems'''
        
        self.get('http://server/path')
        self.assert_status(200)

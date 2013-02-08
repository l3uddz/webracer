import webracer
import nose.plugins.attrib
from tests import utils
from tests import kitchen_sink_app

utils.app_runner_setup(__name__, kitchen_sink_app.app, 8055)

@nose.plugins.attrib.attr('client')
@webracer.config(host='localhost', port=8055)
class ParamsTest(webracer.WebTestCase):
    def test_query_string(self):
        self.get('/get_param', query='p=value')
        self.assert_status(200)
        self.assertEqual('value', self.response.body)
    
    def test_query_tuple(self):
        self.get('/get_param', query=(('p', 'value'),))
        self.assert_status(200)
        self.assertEqual('value', self.response.body)
    
    def test_query_dict(self):
        self.get('/get_param', query=dict(p='value'))
        self.assert_status(200)
        self.assertEqual('value', self.response.body)
    
    def test_param_string(self):
        self.post('/param', body='p=value')
        self.assert_status(200)
        self.assertEqual('value', self.response.body)
    
    def test_param_dict(self):
        self.post('/param', body=dict(p='value'))
        self.assert_status(200)
        self.assertEqual('value', self.response.body)
    
    def test_param_tuple(self):
        self.post('/param', body=(('p', 'value'),))
        self.assert_status(200)
        self.assertEqual('value', self.response.body)
    
    def test_param_positional(self):
        self.post('/param', dict(p='value'))
        self.assert_status(200)
        self.assertEqual('value', self.response.body)
    
    def test_post_without_params(self):
        self.post('/param')
        self.assert_status(200)
        self.assertEqual('', self.response.body)
        
        # content-length should be set to zero for cherrypy
        self.post('/get_content_length')
        self.assert_status(200)
        self.assertEqual('0', self.response.body)
    
    def test_post_with_empty_params(self):
        self.post('/param', body={})
        self.assert_status(200)
        self.assertEqual('', self.response.body)
        
        # content-length should be set to zero for cherrypy
        self.post('/get_content_length', body={})
        self.assert_status(200)
        self.assertEqual('0', self.response.body)

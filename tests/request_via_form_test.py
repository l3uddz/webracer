import webracer
import nose.plugins.attrib
from . import utils
from .apps import form_app

utils.app_runner_setup(__name__, form_app.app, 8059)

@nose.plugins.attrib.attr('client')
@webracer.config(host='localhost', port=8059)
class RequestViaFormTest(webracer.WebTestCase):
    def test_get_form_as_url(self):
        self.get('/method_check_form')
        self.assert_status(200)
        
        form = self.response.form()
        
        self.get(form)
        self.assertEqual('GET', self.response.body)
    
    def test_post_form_as_url(self):
        self.get('/textarea')
        self.assert_status(200)
        
        form = self.response.form()
        
        self.post(form)
        self.assertEqual('{}', self.response.body)
    
    def test_post_form_with_elements(self):
        self.get('/textarea')
        self.assert_status(200)
        
        form = self.response.form()
        elements = form.elements
        
        self.post(form, elements)
        json = self.response.json
        self.assertEqual(dict(field='hello world'), json)
    
    def test_post_form_with_mutated_elements(self):
        self.get('/textarea')
        self.assert_status(200)
        
        form = self.response.form()
        elements = form.elements.mutable
        elements.set_value('field', 'changed')
        
        self.post(form, elements)
        json = self.response.json
        self.assertEqual(dict(field='changed'), json)

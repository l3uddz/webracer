import webracer
import nose.plugins.attrib
from tests import utils
from .apps import form_app

utils.app_runner_setup(__name__, form_app.app, 8044)

@nose.plugins.attrib.attr('client')
@webracer.config(host='localhost', port=8044)
class FormInternalsTest(webracer.WebTestCase):
    def test_elements_input(self):
        self.get('/one_form')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        elements = form.elements.elements
        self.assertEqual(3, len(elements))
        
        # type
        self.assertEqual('text', elements[0][0])
        # name
        self.assertEqual('textf', elements[0][1])
        # value
        self.assertEqual('textv', elements[0][2])
        
        self.assertEqual('submit', elements[1][0])
        self.assertEqual('button', elements[2][0])
    
    def test_params_input(self):
        self.get('/one_form')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        params = form.params
        self.assertEqual([['textf', 'textv']], utils.listit(params.params))
    
    def test_elements_select(self):
        self.get('/form_with_select_selected')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        elements = form.elements.elements
        self.assertEqual(3, len(elements))
        
        # type
        self.assertEqual('option', elements[0][0])
        # name
        self.assertEqual('selectf', elements[0][1])
        # value
        self.assertEqual('first', elements[0][2])
        # selected
        self.assertFalse(elements[0][3])
        
        # type
        self.assertEqual('option', elements[1][0])
        # name
        self.assertEqual('selectf', elements[1][1])
        # value
        self.assertEqual('second', elements[1][2])
        # selected
        self.assertTrue(elements[1][3])
    
    def test_params_select(self):
        self.get('/form_with_select_selected')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        params = form.params
        self.assertEqual([['selectf', 'second']], utils.listit(params.params))
    
    def test_first_radio_selected(self):
        self.get('/first_radio_selected')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        elements = form.elements.elements
        self.assertEqual(3, len(elements))
        self.assertEquals(['radio', 'field', 'first', True], utils.listit(elements[0]))
        self.assertEquals(['radio', 'field', 'second', False], utils.listit(elements[1]))
    
    def test_checkboxes(self):
        self.get('/checkboxes')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        elements = form.elements.elements
        self.assertEqual(3, len(elements))
        self.assertEquals(['checkbox', 'field', 'first', False], utils.listit(elements[0]))
        self.assertEquals(['checkbox', 'field', 'second', True], utils.listit(elements[1]))
    
    def test_empty_textarea(self):
        self.get('/empty_textarea')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        elements = form.elements.elements
        self.assertEqual(2, len(elements))
        self.assertEquals(['textarea', 'field', '', None], utils.listit(elements[0]))
    
    def test_textarea(self):
        self.get('/textarea')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        elements = form.elements.elements
        self.assertEqual(2, len(elements))
        self.assertEquals(['textarea', 'field', 'hello world', None], utils.listit(elements[0]))

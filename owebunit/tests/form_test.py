import owebunit
from owebunit.tests import utils
from owebunit.tests import form_app

utils.start_bottle_server(form_app.app, 8043)

@owebunit.config(host='localhost', port=8043)
class FormTestCase(owebunit.WebTestCase):
    def test_with_specified_attributes(self):
        self.get('/one-form')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        self.assertEqual('/there', form.action)
        # always a full url
        self.assertEqual('http://localhost:8043/there', form.computed_action)
        self.assertEqual('post', form.method)
        self.assertEqual('POST', form.computed_method)
    
    def test_without_specified_attributes(self):
        self.get('/no_attribute_form')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        self.assertTrue(form.action is None)
        self.assertEqual('http://localhost:8043/no_attribute_form', form.computed_action)
        self.assertTrue(form.method is None)
        self.assertEqual('GET', form.computed_method)
    
    def test_computed_action_relative(self):
        self.get('/subdir/relative_action_form')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        self.assertEqual('in_subdir', form.action)
        self.assertEqual('http://localhost:8043/subdir/in_subdir', form.computed_action)
    
    def test_params(self):
        self.get('/no_attribute_form')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        params = form.params.list
        if isinstance(params, list):
            params = tuple(params)
        expected = (('textf', 'textv'),)
        self.assertEqual(expected, params)
    
    def test_params_select_not_selected(self):
        self.get('/form_with_select_not_selected')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        params = form.params.list
        if isinstance(params, list):
            params = tuple(params)
        expected = (('selectf', 'first'),)
        self.assertEqual(expected, params)
    
    def test_params_select_selected(self):
        self.get('/form_with_select_selected')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        params = form.params.list
        if isinstance(params, list):
            params = tuple(params)
        expected = (('selectf', 'second'),)
        self.assertEqual(expected, params)
    
    def test_multiple_submits(self):
        self.get('/form_with_two_submits')
        self.assert_status(200)
        forms = self.response.forms
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        params = form.params.dict
        # first submit element should be returned by default
        self.assertTrue('submit-first' in params)
        self.assertTrue('submit-second' not in params)
        
        # choose another submit button
        params = form.params.submit('submit-second').dict
        self.assertTrue('submit-first' not in params)
        self.assertTrue('submit-second' in params)
        
        # submit and verify, this is really unnecessary but
        # I already wrote the target
        self.get(form.computed_action, body=params)
        self.assert_status(200)
        self.assertEquals({'submit-second': 'second'}, self.response.json)

if __name__ == '__main__':
    import unittest
    unittest.main()

import webracer
import re
import nose.tools
import nose.plugins.attrib
from . import utils
from .apps import form_app

utils.app_runner_setup(__name__, form_app.app, 8043)

@nose.plugins.attrib.attr('client')
@webracer.config(host='localhost', port=8043)
class FormTest(webracer.WebTestCase):
    def test_with_specified_attributes(self):
        self.get('/one_form')
        self.assert_status(200)
        
        form = self.response.form()
        self.assertEqual('/there', form.action)
        # always a full url
        self.assertEqual('http://localhost:8043/there', form.computed_action)
        self.assertEqual('post', form.method)
        self.assertEqual('POST', form.computed_method)
    
    def test_without_specified_attributes(self):
        self.get('/no_attribute_form')
        self.assert_status(200)
        
        form = self.response.form()
        self.assertTrue(form.action is None)
        self.assertEqual('http://localhost:8043/no_attribute_form', form.computed_action)
        self.assertTrue(form.method is None)
        self.assertEqual('GET', form.computed_method)
    
    def test_computed_action_relative(self):
        self.get('/subdir/relative_action_form')
        self.assert_status(200)
        
        form = self.response.form()
        self.assertEqual('in_subdir', form.action)
        self.assertEqual('http://localhost:8043/subdir/in_subdir', form.computed_action)
    
    def test_params(self):
        self.get('/no_attribute_form')
        self.assert_status(200)
        
        form = self.response.form()
        params = form.params.list
        if isinstance(params, list):
            params = tuple(params)
        expected = (('textf', 'textv'),)
        self.assertEqual(expected, params)
    
    def test_params_select_not_selected(self):
        self.get('/form_with_select_not_selected')
        self.assert_status(200)
        
        form = self.response.form()
        params = form.params.list
        if isinstance(params, list):
            params = tuple(params)
        expected = (('selectf', 'first'),)
        self.assertEqual(expected, params)
    
    def test_params_select_selected(self):
        self.get('/form_with_select_selected')
        self.assert_status(200)
        
        form = self.response.form()
        params = form.params.list
        if isinstance(params, list):
            params = tuple(params)
        expected = (('selectf', 'second'),)
        self.assertEqual(expected, params)
    
    def test_params_select_with_optgroup(self):
        self.get('/form_with_optgroup')
        self.assert_status(200)
        
        form = self.response.form()
        params = form.params.list
        if isinstance(params, list):
            params = tuple(params)
        expected = (('selectf', 'first'),)
        self.assertEqual(expected, params)
    
    def test_multiple_submits(self):
        self.get('/form_with_two_submits')
        self.assert_status(200)
        
        form = self.response.form()
        params = form.params.dict
        # first submit element should be returned by default
        self.assertTrue('submit-first' in params)
        self.assertTrue('submit-second' not in params)
        
        # choose another submit button
        elements = form.elements.mutable
        elements.submit('submit-second')
        params = elements.params.dict
        self.assertTrue('submit-first' not in params)
        self.assertTrue('submit-second' in params)
        
        # submit and verify, this is really unnecessary but
        # I already wrote the target
        self.post(form.computed_action, body=params)
        self.assert_status(200)
        self.assertEquals({'submit-second': 'second'}, self.response.json)
    
    def test_set_value(self):
        self.get('/one_form')
        self.assert_status(200)
        
        form = self.response.form()
        elements = form.elements.mutable
        elements.set_value('textf', 'newvalue')
        params = elements.params.list
        self.assertEqual([['textf', 'newvalue']], utils.listit(params))
    
    def test_clear_text(self):
        self.get('/one_form')
        self.assert_status(200)
        
        form = self.response.form()
        elements = form.elements.mutable
        elements.clear('textf')
        params = elements.params.list
        self.assertEqual([['textf', '']], utils.listit(params))
    
    def test_set_and_clear_text(self):
        self.get('/one_form')
        self.assert_status(200)
        
        form = self.response.form()
        elements = form.elements.mutable
        
        elements.set_value('textf', 'newvalue')
        params = elements.params.list
        self.assertEqual([['textf', 'newvalue']], utils.listit(params))
        
        elements.clear('textf')
        params = elements.params.list
        self.assertEqual([['textf', '']], utils.listit(params))
    
    def test_set_value_on_missing_element(self):
        self.get('/one_form')
        self.assert_status(200)
        
        form = self.response.form()
        elements = form.elements.mutable
        # https://github.com/nose-devs/nose/issues/30
        with self.assert_raises(ValueError) as cm:
            elements.set_value('missing', 'newvalue')
        
        assert 'Did not find element with name' in str(cm.exception)
    
    def test_clear_on_missing_element(self):
        self.get('/one_form')
        self.assert_status(200)
        
        form = self.response.form()
        elements = form.elements.mutable
        # https://github.com/nose-devs/nose/issues/30
        with self.assert_raises(ValueError) as cm:
            elements.clear('missing')
        
        assert 'Did not find element with name' in str(cm.exception)
    
    def test_first_radio_selected(self):
        self.get('/first_radio_selected')
        self.assert_status(200)
        
        form = self.response.form()
        elements = form.elements
        self.assertEquals([['field', 'first']], utils.listit(elements.params.list))
    
    def test_second_radio_selected(self):
        self.get('/second_radio_selected')
        self.assert_status(200)
        
        form = self.response.form()
        elements = form.elements
        self.assertEquals([['field', 'second']], utils.listit(elements.params.list))
    
    def test_radio_selection(self):
        self.get('/first_radio_selected')
        self.assert_status(200)
        
        form = self.response.form()
        elements = form.elements.mutable
        self.assertEquals([['field', 'first']], utils.listit(elements.params.list))
        
        # select the other radio button
        elements.set_value('field', 'second')
        self.assertEquals([['field', 'second']], utils.listit(elements.params.list))
        
        # select a nonexistent radio button
        try:
            elements.set_value('field', 'nonexistent')
        except ValueError as e:
            assert re.search(r'Element .* does not have .* as a possible value', str(e))
        else:
            self.fail('Expected ValueError to be raised')
    
    def test_checkboxes(self):
        self.get('/checkboxes')
        self.assert_status(200)
        
        form = self.response.form()
        elements = form.elements
        self.assertEquals([['field', 'second']], utils.listit(elements.params.list))
    
    def test_clear_checkbox(self):
        self.get('/checkboxes')
        self.assert_status(200)
        
        form = self.response.form()
        elements = form.elements.mutable
        self.assertEquals([['field', 'second']], utils.listit(elements.params.list))
        
        elements.clear('field', 'second')
        self.assertEquals([], utils.listit(elements.params.list))
    
    def test_checkbox_selection(self):
        self.get('/checkboxes')
        self.assert_status(200)
        
        form = self.response.form()
        elements = form.elements.mutable
        self.assertEquals([['field', 'second']], utils.listit(elements.params.list))
        
        # select the other checkbox
        elements.set_value('field', 'first')
        self.assertEquals([['field', 'first'], ['field', 'second']], utils.listit(elements.params.list))
    
    def test_set_and_clear_checkbox(self):
        self.get('/checkboxes')
        self.assert_status(200)
        
        form = self.response.form()
        elements = form.elements.mutable
        self.assertEquals([['field', 'second']], utils.listit(elements.params.list))
        
        # select the other checkbox
        elements.set_value('field', 'first')
        self.assertEquals([['field', 'first'], ['field', 'second']], utils.listit(elements.params.list))
        
        # clear the other checkbox
        elements.clear('field', 'first')
        self.assertEquals([['field', 'second']], utils.listit(elements.params.list))
    
    def test_empty_textarea(self):
        self.get('/empty_textarea')
        self.assert_status(200)
        
        form = self.response.form()
        elements = form.elements
        self.assertEquals([['field', '']], utils.listit(elements.params.list))
    
    def test_textarea(self):
        self.get('/textarea')
        self.assert_status(200)
        
        form = self.response.form()
        elements = form.elements
        self.assertEquals([['field', 'hello world']], utils.listit(elements.params.list))

import webracer
import nose.plugins.attrib
from tests import utils
from .apps import form_app

utils.app_runner_setup(__name__, form_app.app, 8049)

@nose.plugins.attrib.attr('client')
@webracer.config(host='localhost', port=8049)
class FormSingularTest(webracer.WebTestCase):
    def setUp(self):
        super(FormSingularTest, self).setUp()
        
        self.get('/form_retrieval')
        self.assert_status(200)
    
    def test_all(self):
        # does not materialize
        form = self.response.form
        
        # materializes
        with self.assert_raises(webracer.MultipleForms):
            form.action
    
    def test_all_call(self):
        # materializes when called
        with self.assert_raises(webracer.MultipleForms):
            form = self.response.form()
    
    def test_name(self):
        form = self.response.form(name='testname')
        self.assertEqual('by-name', form.action)
    
    def test_name_missing(self):
        with self.assert_raises(webracer.NoForms):
            self.response.form(name='missing')
    
    def test_id(self):
        form = self.response.form(id='formid')
        self.assertEqual('by-id', form.action)
    
    def test_id_missing(self):
        with self.assert_raises(webracer.NoForms):
            self.response.form(id='missing')
    
    def test_xpath_noop(self):
        # multiple forms
        with self.assert_raises(webracer.MultipleForms):
            form = self.response.form(xpath='//form')
    
    def test_xpath_all(self):
        with self.assert_raises(webracer.MultipleForms):
            form = self.response.form(xpath='//node()')
    
    def test_xpath_missing(self):
        with self.assert_raises(webracer.NoForms):
            self.response.form(xpath='//form[@id="missing"]')
    
    def test_xpath(self):
        form = self.response.form(xpath='//form[@id="testid3"]')
        self.assertEqual('by-name-and-id', form.action)
    
    def test_css_all(self):
        with self.assert_raises(webracer.MultipleForms):
            form = self.response.form(css='*')
    
    def test_css(self):
        form = self.response.form(css='#testid3')
        self.assertEqual('by-name-and-id', form.action)
    
    def test_css_missing(self):
        with self.assert_raises(webracer.NoForms):
            self.response.form(css='.missing')
    
    def test_css_and_name(self):
        form = self.response.form(css='*', name='testname')
        self.assertEqual('by-name', form.action)
    
    def test_missing_combinations(self):
        existing = [
            dict(xpath='//form'),
            dict(css='form'),
            dict(name='testname'),
            dict(id='formid'),
        ]
        missing = [
            dict(xpath='//strong'),
            dict(css='strong'),
            dict(name='missing'),
            dict(id='missing'),
        ]
        
        for e in existing:
            for m in missing:
                # On python 3:
                # TypeError: 'dict_keys' object does not support indexing
                if tuple(e.keys())[0] == tuple(m.keys())[0]:
                    continue
                
                merged = dict(e)
                merged.update(m)
                
                with self.assert_raises(webracer.NoForms):
                    form = self.response.form(**merged)
    
    def test_no_forms_message(self):
        try:
            self.response.form(xpath='//form[@id="missing-id"]')
        except webracer.NoForms as exc:
            # parameter should be included in the message
            self.assertTrue('missing-id' in str(exc), 'id not included in message')
        else:
            self.fail('NoForms not raised')

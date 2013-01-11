import owebunit
import utils
import form_app

utils.start_bottle_server(form_app.app, 8049)

@owebunit.config(host='localhost', port=8049)
class FormRetrievalTestCase(owebunit.WebTestCase):
    def setUp(self):
        super(FormRetrievalTestCase, self).setUp()
        
        self.get('/form_retrieval')
        self.assert_status(200)
    
    def test_all(self):
        # does not materialize
        form = self.response.form
        
        # materializes
        with self.assert_raises(owebunit.MultipleForms):
            form.action
    
    def test_all_call(self):
        # materializes when called
        with self.assert_raises(owebunit.MultipleForms):
            form = self.response.form()
    
    def test_name(self):
        form = self.response.form(name='testname')
        self.assertEqual('by-name', form.action)
    
    def test_name_missing(self):
        with self.assert_raises(owebunit.NoForms):
            self.response.form(name='missing')
    
    def test_id(self):
        form = self.response.form(id='formid')
        self.assertEqual('by-id', form.action)
    
    def test_id_missing(self):
        with self.assert_raises(owebunit.NoForms):
            self.response.form(id='missing')
    
    def test_xpath_noop(self):
        # multiple forms
        with self.assert_raises(owebunit.MultipleForms):
            form = self.response.form(xpath='//form')
    
    def test_xpath_all(self):
        with self.assert_raises(owebunit.MultipleForms):
            form = self.response.form(xpath='//node()')
    
    def test_xpath_missing(self):
        with self.assert_raises(owebunit.NoForms):
            self.response.form(xpath='//form[@id="missing"]')
    
    def test_xpath(self):
        form = self.response.form(xpath='//form[@id="testid3"]')
        self.assertEqual('by-name-and-id', form.action)
    
    def test_css_all(self):
        with self.assert_raises(owebunit.MultipleForms):
            form = self.response.form(css='*')
    
    def test_css(self):
        form = self.response.form(css='#testid3')
        self.assertEqual('by-name-and-id', form.action)
    
    def test_css_missing(self):
        with self.assert_raises(owebunit.NoForms):
            self.response.form(css='.missing')
    
    def test_css_and_name(self):
        form = self.response.form(css='*', name='testname')
        self.assertEqual('by-name', form.action)

if __name__ == '__main__':
    import unittest
    unittest.main()

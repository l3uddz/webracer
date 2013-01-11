import owebunit
import utils
import form_app

utils.start_bottle_server(form_app.app, 8048)

@owebunit.config(host='localhost', port=8048)
class FormRetrievalTestCase(owebunit.WebTestCase):
    def setUp(self):
        super(FormRetrievalTestCase, self).setUp()
        
        self.get('/form_retrieval')
        self.assert_status(200)
    
    def test_all(self):
        forms = self.response.forms
        self.assertEquals(5, len(forms))
        
        form = forms[4]
        self.assertEqual('by-name-and-id', form.action)
    
    def test_name(self):
        forms = self.response.forms(name='testname')
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        self.assertEqual('by-name', form.action)
    
    def test_name_missing(self):
        forms = self.response.forms(name='missing')
        self.assertEquals(0, len(forms))
    
    def test_id(self):
        forms = self.response.forms(id='formid')
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        self.assertEqual('by-id', form.action)
    
    def test_id_missing(self):
        forms = self.response.forms(id='missing')
        self.assertEquals(0, len(forms))
    
    def test_xpath_noop(self):
        forms = self.response.forms(xpath='//form')
        self.assertEquals(5, len(forms))
    
    def test_xpath_all(self):
        forms = self.response.forms(xpath='//node()')
        # should only return forms
        self.assertEquals(5, len(forms))
    
    def test_xpath(self):
        forms = self.response.forms(xpath='//form[@id="testid3"]')
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        self.assertEqual('by-name-and-id', form.action)
    
    def test_xpath_missing(self):
        forms = self.response.forms(xpath='//form[@id="missing"]')
        self.assertEquals(0, len(forms))
    
    def test_css_all(self):
        forms = self.response.forms(css='*')
        # should only return forms
        self.assertEquals(5, len(forms))
    
    def test_css_missing(self):
        forms = self.response.forms(css='#missing')
        self.assertEquals(0, len(forms))
    
    def test_css(self):
        forms = self.response.forms(css='#testid3')
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        self.assertEqual('by-name-and-id', form.action)
    
    def test_css_and_name(self):
        forms = self.response.forms(css='*', name='testname')
        self.assertEquals(1, len(forms))
        
        form = forms[0]
        self.assertEqual('by-name', form.action)

if __name__ == '__main__':
    import unittest
    unittest.main()

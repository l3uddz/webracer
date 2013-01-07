import lxml.etree
import owebunit
import bottle
import utils

app = bottle.Bottle()

@app.route('/xml')
def xml():
    bottle.response.content_type = 'application/xml'
    return '<rootelement><element><subelement>text</subelement></element></rootelement>'

@app.route('/html')
def html():
    bottle.response.content_type = 'text/html'
    return '<!doctype html><html><head><meta name=foo value=bar></head><body></body></html>'

utils.start_bottle_server(app, 8042)

@owebunit.config(host='localhost', port=8042)
class LxmlTestCase(owebunit.WebTestCase):
    def test_parse_xml(self):
        self.get('/xml')
        self.assert_status(200)
        doc = self.response.lxml_etree_xml
        self.assertTrue(isinstance(doc, lxml.etree._Element))
    
    def test_parse_html(self):
        self.get('/html')
        self.assert_status(200)
        doc = self.response.lxml_etree_html
        self.assertTrue(isinstance(doc, lxml.etree._Element))
    
    def test_parse_auto_xml(self):
        self.get('/xml')
        self.assert_status(200)
        doc = self.response.lxml_etree
        self.assertTrue(isinstance(doc, lxml.etree._Element))
    
    def test_parse_auto_html(self):
        self.get('/html')
        self.assert_status(200)
        doc = self.response.lxml_etree
        self.assertTrue(isinstance(doc, lxml.etree._Element))

if __name__ == '__main__':
    import unittest
    unittest.main()

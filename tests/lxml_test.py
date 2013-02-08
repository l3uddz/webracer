import lxml.etree
import webracer
import bottle
import nose.plugins.attrib
from tests import utils

app = bottle.Bottle()

@app.route('/xml')
def xml():
    bottle.response.content_type = 'application/xml'
    return '<rootelement><element><subelement>text</subelement></element></rootelement>'

@app.route('/html')
def html():
    bottle.response.content_type = 'text/html'
    return '<!doctype html><html><head><meta name=foo value=bar></head><body></body></html>'

utils.app_runner_setup(__name__, app, 8042)

@nose.plugins.attrib.attr('client')
@webracer.config(host='localhost', port=8042)
class LxmlTest(webracer.WebTestCase):
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

import lxml.etree
import webracer
import nose.plugins.attrib
from tests import utils
from tests import xml_app

utils.app_runner_setup(__name__, xml_app.app, 8042)

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

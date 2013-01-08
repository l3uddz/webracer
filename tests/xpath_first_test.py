import unittest
import lxml.etree
import owebunit.utils

class AbsolutizeUrlTestCase(owebunit.WebTestCase):
    def setUp(self):
        xml = '<root><el><child><grandchild>text</grandchild></child></el></root>'
        self.doc = lxml.etree.XML(xml)
    
    def test_xpath_first_found(self):
        child = owebunit.utils.xpath_first(self.doc, '//child')
        self.assertTrue(child is not None)
        self.assertEqual('child', child.tag)
    
    def test_xpath_first_missing(self):
        # should not raise
        child = owebunit.utils.xpath_first(self.doc, '//nonexistent')
        self.assertTrue(child is None)
    
    def test_xpath_first_check_found(self):
        # should not raise
        child = owebunit.utils.xpath_first_check(self.doc, '//child')
        self.assertTrue(child is not None)
        self.assertEqual('child', child.tag)
    
    def test_xpath_first_check_missing(self):
        try:
            owebunit.utils.xpath_first_check(self.doc, '//nonexistent')
        except AssertionError, e:
            # ok
            self.assertTrue('No elements matching xpath: //nonexistent' in e.message)
        else:
            self.fail('Assertion was not raised')

if __name__ == '__main__':
    import unittest
    unittest.main()

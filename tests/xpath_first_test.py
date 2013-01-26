import unittest
import lxml.etree
import webracer.utils

class AbsolutizeUrlTest(webracer.WebTestCase):
    def setUp(self):
        xml = '<root><el><child><grandchild>text</grandchild></child></el></root>'
        self.doc = lxml.etree.XML(xml)
    
    def test_xpath_first_found(self):
        child = webracer.utils.xpath_first(self.doc, '//child')
        self.assertTrue(child is not None)
        self.assertEqual('child', child.tag)
    
    def test_xpath_first_missing(self):
        # should not raise
        child = webracer.utils.xpath_first(self.doc, '//nonexistent')
        self.assertTrue(child is None)
    
    def test_xpath_first_check_found(self):
        # should not raise
        child = webracer.utils.xpath_first_check(self.doc, '//child')
        self.assertTrue(child is not None)
        self.assertEqual('child', child.tag)
    
    def test_xpath_first_check_missing(self):
        try:
            webracer.utils.xpath_first_check(self.doc, '//nonexistent')
        except AssertionError as e:
            # ok
            self.assertTrue('No elements matching xpath: //nonexistent' in str(e))
        else:
            self.fail('Assertion was not raised')

if __name__ == '__main__':
    import unittest
    unittest.main()

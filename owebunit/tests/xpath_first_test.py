import unittest
import lxml.etree
import owebunit

class AbsolutizeUrlTestCase(owebunit.WebTestCase):
    def test_xpath_first(self):
        xml = '<root><el><child><grandchild>text</grandchild></child></el></root>'
        doc = lxml.etree.XML(xml)
        
        # should not raise
        child = self.xpath_first(doc, '//child')
        self.assertTrue(child is not None)
        self.assertEqual('child', child.tag)
        
        try:
            self.xpath_first(doc, '//nonexistent')
            assert False
        except AssertionError:
            # ok
            pass

if __name__ == '__main__':
    import unittest
    unittest.main()

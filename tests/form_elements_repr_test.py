import unittest
import webracer

class FormElementsReprTest(unittest.TestCase):
    def test_repr_with_no_elements(self):
        elements = webracer.FormElements([])
        r = repr(elements)
        self.assertEqual('<webracer.FormElements: []>', r)
    
    def test_repr_with_one_element_not_selected(self):
        e = ['etype', 'ename', 'evalue', False]
        elements = webracer.FormElements([e])
        r = repr(elements)
        self.assertEqual('<webracer.FormElements: [etype name=ename, value=evalue]>', r)
    
    def test_repr_with_one_element_selected(self):
        e = ['etype', 'ename', 'evalue', True]
        elements = webracer.FormElements([e])
        r = repr(elements)
        self.assertEqual('<webracer.FormElements: [etype name=ename, value=evalue, selected]>', r)
    
    def test_repr_with_two_elements(self):
        e1 = ['etype', 'ename1', 'evalue', False]
        e2 = ['etype', 'ename2', 'evalue', True]
        elements = webracer.FormElements([e1, e2])
        r = repr(elements)
        self.assertEqual('<webracer.FormElements: [etype name=ename1, value=evalue], [etype name=ename2, value=evalue, selected]>', r)

if __name__ == '__main__':
    import unittest
    unittest.main()

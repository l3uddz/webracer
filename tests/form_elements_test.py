import unittest
import webracer

class FormElementsTest(unittest.TestCase):
    def test_params_for_empty_form(self):
        elements = webracer.FormElements([])
        params = elements.params.dict
        self.assertEqual({}, params)
    
    def test_params_for_nameless_submit_only(self):
        e = ['submit', None, 'doit', False]
        elements = webracer.FormElements([e])
        params = elements.params.dict
        self.assertEqual({}, params)
    
    def test_params_for_nameless_and_named_submits(self):
        e1 = ['submit', None, 'doit', False]
        e2 = ['submit', 'alt', 'alt', False]
        elements = webracer.FormElements([e1, e2])
        params = elements.params.dict
        self.assertEqual({}, params)

if __name__ == '__main__':
    import unittest
    unittest.main()

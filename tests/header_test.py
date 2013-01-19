import owebunit
from tests import utils
from tests import kitchen_sink_app

def setup_module():
    utils.start_bottle_server(kitchen_sink_app.app, 8051)

@owebunit.config(host='localhost', port=8051)
class KitchenSinkTestCase(owebunit.WebTestCase):
    def test_header_list(self):
        self.get('/ok')
        self.assert_status(200)
        
        actual = utils.listit(self.response.header_list)
        lowercased = [[key.lower(), value] for key, value in actual]
        self.assertTrue(['content-length', '2'] in lowercased)
        
        # in python 2.7 header names are lowercased.
        # in python 3.3 they are camelcased.
        # in any event, bogus casing should not be allowed.
        self.assertTrue(['content-LENGTH', '2'] not in actual)
    
    def test_header_dict(self):
        self.get('/ok')
        self.assert_status(200)
        
        actual = self.response.header_dict
        lowercased_keys = [key.lower() for key in actual.keys()]
        
        assert 'content-length' in lowercased_keys
        
        # all cases should be accepted by the dict itself
        assert 'content-length' in actual
        assert 'Content-Length' in actual
        assert 'content-LENGTH' in actual

if __name__ == '__main__':
    import unittest
    unittest.main()

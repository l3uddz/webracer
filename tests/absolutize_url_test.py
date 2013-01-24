import unittest
import owebunit

class AbsolutizeUrlTest(unittest.TestCase):
    def test_noop(self):
        config = owebunit.Config(host=None, port=None, protocol=None)
        url = 'http://absolute/url'
        self._perform(config, url, url)
    
    def test_with_host(self):
        config = owebunit.Config(host='host', port=None, protocol=None)
        url = '/path'
        expected = 'http://host/path'
        self._perform(config, url, expected)
    
    def test_with_host_and_port(self):
        config = owebunit.Config(host='host', port=8080, protocol=None)
        url = '/path'
        expected = 'http://host:8080/path'
        self._perform(config, url, expected)
    
    def test_with_host_as_url(self):
        config = owebunit.Config(host='http://host', port=None, protocol=None)
        url = '/path'
        expected = 'http://host/path'
        self._perform(config, url, expected)
    
    def test_with_host_and_port_as_url(self):
        config = owebunit.Config(host='http://host:8080', port=None, protocol=None)
        url = '/path'
        expected = 'http://host:8080/path'
        self._perform(config, url, expected)
    
    def test_with_port_only(self):
        config = owebunit.Config(host=None, port=8080, protocol=None)
        url = '/path'
        expected = 'http://host:8080/path'
        self.assertRaises(ValueError, self._perform, config, url, expected)
    
    def _perform(self, config, url, expected):
        session = owebunit.Session(config)
        absolutized = session._absolutize_url(url)
        self.assertEqual(expected, absolutized)

if __name__ == '__main__':
    import unittest
    unittest.main()

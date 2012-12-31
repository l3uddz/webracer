import unittest
import owebunit

class AbsolutizeUrlTestCase(unittest.TestCase):
    def test_noop(self):
        config = owebunit.Config()
        config.host = config.port = config.protocol = None
        url = 'http://absolute/url'
        self._perform(config, url, url)
    
    def test_with_host(self):
        config = owebunit.Config()
        config.host = 'host'
        config.port = config.protocol = None
        url = '/path'
        expected = 'http://host/path'
        self._perform(config, url, expected)
    
    def test_with_host_and_port(self):
        config = owebunit.Config()
        config.host = 'host'
        config.port = 8080
        config.protocol = None
        url = '/path'
        expected = 'http://host:8080/path'
        self._perform(config, url, expected)
    
    def test_with_host_and_port_as_url(self):
        config = owebunit.Config()
        config.host = 'http://host:8080'
        config.port = config.protocol = None
        url = '/path'
        expected = 'http://host:8080/path'
        self._perform(config, url, expected)
    
    def _perform(self, config, url, expected):
        session = owebunit.Session(config, None)
        absolutized = session._absolutize_url(url)
        self.assertEqual(expected, absolutized)

if __name__ == '__main__':
    import unittest
    unittest.main()

import owebunit
from tests import utils
from tests import kitchen_sink_app

utils.start_bottle_server(kitchen_sink_app.app, 8052)

class SessionTest(owebunit.WebTestCase):
    def test_get(self):
        s = owebunit.Session()
        s.get('http://127.0.0.1:8052/ok')
        self.assertEqual(200, s.response.code)
        self.assertEqual('ok', s.response.body)

if __name__ == '__main__':
    import unittest
    unittest.main()

import time
import owebunit
import mock
from . import utils
from . import kitchen_sink_app

utils.start_bottle_server(kitchen_sink_app.app, 8047)

class MySession(owebunit.Session):
    def extra_method(self):
        return 'extra'

@owebunit.config(session_class=MySession)
class SessionClassOverrideTestCase(owebunit.WebTestCase):
    def test_extra_method(self):
        with self.session() as s:
            s.get('http://127.0.0.1:8047/ok')
            s.assert_status(200)
            self.assertEqual('extra', s.extra_method())

if __name__ == '__main__':
    import unittest
    unittest.main()

import webracer
from tests import utils
from tests import kitchen_sink_app

def setup_module():
    utils.start_bottle_server(kitchen_sink_app.app, 8047)

class MySession(webracer.Session):
    def extra_method(self):
        return 'extra'

@webracer.config(session_class=MySession)
class SessionClassOverrideTest(webracer.WebTestCase):
    def test_extra_method(self):
        with self.session() as s:
            s.get('http://127.0.0.1:8047/ok')
            s.assert_status(200)
            self.assertEqual('extra', s.extra_method())

if __name__ == '__main__':
    import unittest
    unittest.main()

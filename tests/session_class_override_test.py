import webracer
import nose.plugins.attrib
from tests import utils
from tests import kitchen_sink_app

utils.app_runner_setup(__name__, kitchen_sink_app.app, 8047)

class MySession(webracer.Session):
    def extra_method(self):
        return 'extra'

@nose.plugins.attrib.attr('client')
@webracer.config(session_class=MySession)
@webracer.config(host='localhost', port=8047)
class SessionClassOverrideTest(webracer.WebTestCase):
    def test_extra_method(self):
        with self.session() as s:
            s.get('/ok')
            s.assert_status(200)
            self.assertEqual('extra', s.extra_method())

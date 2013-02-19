import webracer
import nose.plugins.attrib
from . import utils
from .apps import kitchen_sink_app

utils.app_runner_setup(__name__, kitchen_sink_app.app, 8047)

class MyAgent(webracer.Agent):
    def extra_method(self):
        return 'extra'

@nose.plugins.attrib.attr('client')
@webracer.config(agent_class=MyAgent)
@webracer.config(host='localhost', port=8047)
class AgentClassOverrideTest(webracer.WebTestCase):
    def test_extra_method(self):
        with self.agent() as s:
            s.get('/ok')
            s.assert_status(200)
            self.assertEqual('extra', s.extra_method())

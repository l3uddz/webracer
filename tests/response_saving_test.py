import os
import os.path
import webracer
import nose.plugins.attrib
from . import utils
from .apps import kitchen_sink_app

utils.app_runner_setup(__name__, kitchen_sink_app.app, 8060)

save_dir = os.path.join(os.path.dirname(__file__), 'tmp')

def list_save_dir():
    entries = os.listdir(save_dir)
    entries = [entry for entry in entries if entry[0] != '.']
    return entries

@nose.plugins.attrib.attr('client')
@webracer.config(host='localhost', port=8060)
@webracer.config(save_responses=True, save_dir=save_dir)
class ResponseTest(webracer.WebTestCase):
    def setUp(self, *args, **kwargs):
        super(ResponseTest, self).setUp(*args, **kwargs)
        
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        else:
            for entry in list_save_dir():
                os.unlink(os.path.join(save_dir, entry))
    
    def test_save_successful(self):
        self.assertEqual(0, len(list_save_dir()))
        
        self.get('/ok')
        self.assert_status(200)
        self.assertEqual('ok', self.response.body)
        
        entries = list_save_dir()
        # response + last symlink
        self.assertEqual(2, len(entries))
        assert 'last' in entries
        entries.remove('last')
        assert entries[0].startswith('response')
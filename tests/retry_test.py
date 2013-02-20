import webracer
import nose.plugins.attrib
from . import utils
from .apps import retry_app

if utils.py3:
    range_iter = range
else:
    range_iter = xrange

utils.app_runner_setup(__name__, retry_app.app, 8058)

base_config = dict(host='localhost', port=8058)

@webracer.config(**base_config)
@nose.plugins.attrib.attr('client')
class RetryTest(webracer.WebTestCase):
    def test_fixture_empty(self):
        self.get('/')
        self.assert_status(999)
    
    def test_fixture_not_empty(self):
        retry_app.status_codes = [200, 500, 404, 200]
        self.get('/')
        self.assert_status(200)
        self.get('/')
        self.assert_status(500)
        self.get('/')
        self.assert_status(404)
        self.get('/')
        self.assert_status(200)
    
    def test_with_retry_default(self):
        retry_app.status_codes = [200, 500, 404, 200]
        config = utils.add_dicts(base_config, dict(retry_failed=True, retry_count=5))
        with webracer.Agent(**config) as s:
            s.get('/')
            s.assert_status(200)
            s.get('/')
            s.assert_status(404)
            s.get('/')
            s.assert_status(200)
            s.get('/')
            s.assert_status(999)
    
    def test_with_retry_sequence(self):
        retry_app.status_codes = [200, 500, 404, 200]
        config = utils.add_dicts(base_config, dict(
            retry_failed=True, retry_count=5, retry_condition=range_iter(400, 599),
        ))
        with webracer.Agent(**config) as s:
            s.get('/')
            s.assert_status(200)
            # 404 is now retried
            s.get('/')
            s.assert_status(200)
            s.get('/')
            s.assert_status(999)
    
    def test_with_retry_custom(self):
        retry_app.status_codes = [200, 500, 404, 200]
        def retry_fn(response):
            return response.code == 200
        config = utils.add_dicts(base_config, dict(
            retry_failed=True, retry_count=5, retry_condition=retry_fn,
        ))
        with webracer.Agent(**config) as s:
            s.get('/')
            s.assert_status(500)
            s.get('/')
            s.assert_status(404)
            s.get('/')
            s.assert_status(999)

import webracer.utils.runwsgi
import sys
import nose.tools

py3 = sys.version_info[0] == 3

def app_runner_setup(module_name, app, port):
    app_runner_setup_multiple(module_name, [[app, port]])

def app_runner_setup_multiple(module_name, specs):
    # take module_name rather than module for convenience, to avoid
    # requiring all tests to import sys
    module = sys.modules[module_name]
    
    setup, teardown = webracer.utils.runwsgi.app_runner_setup(*specs)
    
    assert not hasattr(module, 'setup_module')
    assert not hasattr(module, 'teardown_module')
    
    module.setup_module = setup
    module.teardown_module = teardown

# http://code.activestate.com/recipes/106033-deep-list-to-convert-a-nested-tuple-of-tuples/
def listit(t):
    return list(map(listit, t)) if isinstance(t, (list, tuple)) else t

# XXX unused and untested currently
if sys.version_info[0] >= 2 or sys.version_info[0] == 2 and sys.version_info[1] >= 7:
    assert_raises = nose.tools.assert_raises
else:
    def assert_raises(exception, callable=None, *args, **kwargs):
        if callable is None:
            return webracer.case.AssertRaisesContextManager(exception)
        else:
            return nose.tools.assert_raises(exception, callable, *args, **kwargs)

def add_dicts(one, two):
    out = dict(one)
    for key in two:
        out[key] = two[key]
    return out

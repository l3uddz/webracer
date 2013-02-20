import bottle
import threading
import socket
import time as _time
import sys
import nose.tools

py3 = sys.version_info[0] == 3

class Server(bottle.WSGIRefServer):
    def run(self, handler): # pragma: no cover
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            base = self.options.get('handler_class', WSGIRequestHandler)
            class QuietHandler(base):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        self.srv = make_server(self.host, self.port, handler, **self.options)
        self.srv.serve_forever(poll_interval=0.1)

def start_bottle_server(app, port, **kwargs):
    server_thread = ServerThread(app, port, kwargs)
    server_thread.daemon = True
    server_thread.start()
    
    ok = False
    for i in range(10):
        try:
            conn = socket.create_connection(('127.0.0.1', port), 0.1)
        except socket.error as e:
            _time.sleep(0.1)
        else:
            conn.close()
            ok = True
            break
    if not ok:
        import warnings
        warnings.warn('Server did not start after 1 second')
    
    return server_thread.server

class ServerThread(threading.Thread):
    def __init__(self, app, port, server_kwargs):
        threading.Thread.__init__(self)
        self.app = app
        self.port = port
        self.server_kwargs = server_kwargs
        self.server = Server(host='localhost', port=self.port, **self.server_kwargs)
    
    def run(self):
        bottle.run(self.app, server=self.server, quiet=True)

def app_runner_setup(module_name, app, port):
    app_runner_setup_multiple(module_name, [[app, port]])

def app_runner_setup_multiple(module_name, specs):
    # take module_name rather than module for convenience, to avoid
    # requiring all tests to import sys
    module = sys.modules[module_name]
    
    def setup(self):
        self.servers = []
        for spec in specs:
            if len(spec) == 2:
                app, port = spec
                kwargs = {}
            else:
                app, port, kwargs = spec
            self.servers.append(start_bottle_server(app, port, **kwargs))
    
    def teardown(self):
        for server in self.servers:
            server.srv.shutdown()
    
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

import bottle
import threading
import socket
import time as _time
import sys
import nose.tools

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

class ServerThread(threading.Thread):
    def __init__(self, app, port, server_kwargs):
        threading.Thread.__init__(self)
        self.app = app
        self.port = port
        self.server_kwargs = server_kwargs
    
    def run(self):
        bottle.run(self.app, host='localhost', port=self.port, **self.server_kwargs)

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

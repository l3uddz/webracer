import bottle
import threading
import socket
import time as _time

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

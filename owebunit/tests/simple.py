import BaseHTTPServer
import threading
import time
import owebunit
import bottle

app = bottle.Bottle()

@app.route('/ok')
def ok():
    return 'ok'

@app.route('/internal_server_error')
def internal_error():
    bottle.abort(500, 'internal server error')

def run_server():
    app.run(host='localhost', port=8041)

class ServerThread(threading.Thread):
    def run(self):
        run_server()

def start_server():
    server_thread = ServerThread()
    server_thread.daemon = True
    server_thread.start()

start_server()

time.sleep(0.1)

class Case(owebunit.WebTestCase):
    def test_simple(self):
        self.get('http://127.0.0.1:8041/ok')
        self.assert_code(200)
    
    def test_session(self):
        with self.session() as s:
            s.get('http://127.0.0.1:8041/ok')
            s.assert_code(200)
    
    def test_multiple_sessions(self):
        one = self.session()
        one.get('http://127.0.0.1:8041/ok')
        
        two = self.session()
        two.get('http://127.0.0.1:8041/internal_server_error')
        
        one.assert_code(200)
        two.assert_code(500)

if __name__ == '__main__':
    import unittest
    unittest.main()

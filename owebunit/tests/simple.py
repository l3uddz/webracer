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

@app.route('/set_cookie')
def set_cookie():
    bottle.response.set_cookie('visited', 'yes')

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

class SimpleTestCase(owebunit.WebTestCase):
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
    
    def test_cookie(self):
        self.get('http://127.0.0.1:8041/set_cookie')
        self.assert_code(200)
        
        self.assert_response_cookie('visited')
        self.assert_response_cookie('visited', value='yes')
        
        # nonexistent cookie
        self.assert_not_response_cookie('nonexistent_cookie')
        
        with self.assert_raises(AssertionError):
            self.assert_response_cookie('visited', value='no')
    
    def test_implicit_session(self):
        self.get('http://127.0.0.1:8041/set_cookie')
        self.assert_code(200)
        self.assert_response_cookie('visited')
        self.assert_session_cookie('visited')
        
        self.get('http://127.0.0.1:8041/ok')
        self.assert_code(200)
        self.assert_not_response_cookie('visited')
        self.assert_session_cookie('visited')

if __name__ == '__main__':
    import unittest
    unittest.main()

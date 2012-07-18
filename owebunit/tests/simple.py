import BaseHTTPServer
import threading
import time
import owebunit

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        self.wfile.write("HTTP/1.0 200 OK\n")
        self.wfile.write("Content-Type: text/plain\n")
        self.wfile.write("\n")
        self.wfile.write("Response text")

def run_server():
    server_address = ('', 8041)
    httpd = BaseHTTPServer.HTTPServer(server_address, Handler)
    while True:
        httpd.handle_request()

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
        self.get('http://127.0.0.1:8041')
        self.assert_code(200)

if __name__ == '__main__':
    import unittest
    unittest.main()

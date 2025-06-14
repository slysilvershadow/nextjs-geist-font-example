import http.server
import socketserver
import webbrowser
import os
import socket
import time

PORT = 8000

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def wait_for_port_release(port, timeout=30):
    start_time = time.time()
    while is_port_in_use(port):
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Port {port} did not become available within {timeout} seconds")
        time.sleep(1)

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

try:
    # Wait for the port to become available
    wait_for_port_release(PORT)
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        print(f"Open http://localhost:{PORT} in your browser")
        httpd.serve_forever()
except Exception as e:
    print(f"Error: {e}")
    if isinstance(e, TimeoutError):
        print("Try manually killing the process using the port or choose a different port")

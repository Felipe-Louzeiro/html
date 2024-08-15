from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import json
from db import User, init_db
from users import generate_token, requires_auth

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/register':
            self.register()
        elif self.path == '/login':
            self.login()
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/profile':
            self.profile()
        elif self.path == '/hello':
            self.hello_world()
        else:
            self.send_response(404)
            self.end_headers()

    def register(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Username and password required')
            return

        if User.find_by_username(username):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'User already exists')
            return

        User.create(username, password)
        self.send_response(201)
        self.end_headers()
        self.wfile.write(b'User created successfully')

    def login(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Username and password required')
            return

        user = User.find_by_username(username)
        if user and user.check_password(password):
            token = generate_token(user.username)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'token': token}).encode())
        else:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'Invalid username or password')

    @requires_auth
    def profile(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'username': self.user_id}).encode())
        
    def hello_world(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Hello, World!')

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    init_db()
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Startado na porta {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()

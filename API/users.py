from multiprocessing import process
import jwt
import datetime
from functools import wraps
from http.server import BaseHTTPRequestHandler
from db import User

def generate_token(user_id):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(payload, process.env.SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        payload = jwt.decode(token, process.env.SECRET_KEY, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def requires_auth(handler):
    @wraps(handler)
    def decorated(self, *args, **kwargs):
        auth_header = self.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(" ")[1]
            user_id = decode_token(token)
            if user_id:
                self.user_id = user_id
                return handler(self, *args, **kwargs)
        self.send_response(401)
        self.end_headers()
        self.wfile.write(b'Unauthorized')
    return decorated
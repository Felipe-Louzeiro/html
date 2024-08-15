import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def connect_db():
    return sqlite3.connect('database.sqlite')

def init_db():
    with connect_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        conn.commit()
        
class User:
    def __init__(self, username, password=None):
        self.username = username
        self.password_hash = generate_password_hash(password) if password else None

    @staticmethod
    def create(username, password):
        user = User(username, password)
        with connect_db() as conn:
            conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                         (user.username, user.password_hash))
            conn.commit()

    @staticmethod
    def find_by_username(username):
        with connect_db() as conn:
            cur = conn.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cur.fetchone()
            if row:
                user = User(username=row[1])
                user.password_hash = row[2]
                return user
            return None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
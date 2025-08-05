import sqlite3
from flask import g

DATABASE = 'shortener.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY,
            shortcode TEXT UNIQUE,
            url TEXT,
            expiry TEXT,
            created_at TEXT
        )
        ''')
        db.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY,
            shortcode TEXT,
            timestamp TEXT
        )
        ''')
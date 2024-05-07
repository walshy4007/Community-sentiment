import sqlite3
from datetime import datetime

DATABASE_PATH = 'sentiments.db'

def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_data (
                guild_id TEXT,
                channel_name TEXT,
                sentiment TEXT,
                timestamp DATETIME
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS allowed_roles (
                guild_id TEXT,
                role_id TEXT,
                PRIMARY KEY (guild_id, role_id)
            )
        ''')
        conn.commit()

def insert_sentiment(guild_id, channel_name, sentiment):
    timestamp = datetime.utcnow()
    with sqlite3.connect(DATABASE_PATH) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO sentiment_data (guild_id, channel_name, sentiment, timestamp) VALUES (?, ?, ?, ?)',
                  (guild_id, channel_name, sentiment, timestamp))
        conn.commit()

def fetch_sentiment_data(query, params):
    with sqlite3.connect(DATABASE_PATH) as conn:
        c = conn.cursor()
        c.execute(query, params)
        return c.fetchall()

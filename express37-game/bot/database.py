import sqlite3
import secrets
import os

DATABASE = 'express37.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            balance REAL DEFAULT 10000.0,
            auth_token TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            dice1_throw1 INTEGER,
            dice2_throw1 INTEGER,
            dice1_throw2 INTEGER,
            dice2_throw2 INTEGER,
            result_number INTEGER,
            bet_amount REAL,
            win_amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized!")

def register_user(telegram_id, username=None, first_name=None):
    conn = get_db()
    cursor = conn.cursor()
    
    auth_token = secrets.token_hex(32)
    
    try:
        cursor.execute('''
            INSERT INTO users (telegram_id, username, first_name, auth_token)
            VALUES (?, ?, ?, ?)
        ''', (telegram_id, username, first_name, auth_token))
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        cursor.execute('SELECT id, auth_token FROM users WHERE telegram_id = ?', (telegram_id,))
        row = cursor.fetchone()
        user_id = row['id']
        auth_token = row['auth_token']
    
    conn.close()
    return user_id, auth_token

def get_user_by_token(token):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE auth_token = ?', (token,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_telegram_id(telegram_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def update_balance(user_id, amount):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, user_id))
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result['balance'] if result else 0

def save_game_round(user_id, d1t1, d2t1, d1t2, d2t2, result, bet_amount, win_amount):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO game_rounds 
        (user_id, dice1_throw1, dice2_throw1, dice1_throw2, dice2_throw2, result_number, bet_amount, win_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, d1t1, d2t1, d1t2, d2t2, result, bet_amount, win_amount))
    conn.commit()
    conn.close()

# Инициализация при импорте
init_db()
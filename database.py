import sqlite3
import os

DB_NAME = "documents.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Documents table
    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            task_type TEXT,
            original_notes TEXT,
            generated_document TEXT
        )
    ''')
    # Settings table
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_document(task_type, original_notes, generated_document):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO documents (task_type, original_notes, generated_document)
        VALUES (?, ?, ?)
    ''', (task_type, original_notes, generated_document))
    conn.commit()
    conn.close()

def save_setting(key, value):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO settings (key, value)
        VALUES (?, ?)
    ''', (key, value))
    conn.commit()
    conn.close()

def get_setting(key, default_value=""):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT value FROM settings WHERE key = ?', (key,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else default_value

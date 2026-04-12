import sqlite3
import os

DB_PATH = 'investment_site/instance/users.db'

def check_columns():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(user)")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    return columns

def add_missing_columns():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    missing = []
    
    new_columns = {
        'is_admin': 'BOOLEAN NOT NULL DEFAULT 0',
        'is_blocked': 'BOOLEAN NOT NULL DEFAULT 0',
        'custom_rate': 'REAL NOT NULL DEFAULT 0.0214',
        'budget_limit': 'REAL'
    }
    
    for col, definition in new_columns.items():
        try:
            cursor.execute(f"ALTER TABLE user ADD COLUMN {col} {definition}")
            print(f"Added {col}")
        except sqlite3.OperationalError:
            print(f"{col} already exists")
    
    conn.commit()
    conn.close()
    print("Schema updated successfully")

if __name__ == '__main__':
    columns = check_columns()
    print("Current columns:", columns)
    add_missing_columns()


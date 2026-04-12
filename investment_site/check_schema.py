import sqlite3
import sys

db_path = 'instance/users.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(user)")
columns = cursor.fetchall()

print("User table columns:")
for col in columns:
    print(f"  - {col[1]} ({col[2]}) {'PRIMARY KEY' if col[5] else ''}")

conn.close()


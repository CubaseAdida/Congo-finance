import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'users.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Before unblock:")
cursor.execute("SELECT id, email, is_admin, is_blocked FROM user WHERE email='admin@congofinance.com';")
result = cursor.fetchone()
print(result)

cursor.execute("UPDATE user SET is_blocked = 0 WHERE email='admin@congofinance.com';")
conn.commit()

print("\nAfter unblock (rows updated):", cursor.rowcount)
print("Verify:")
cursor.execute("SELECT id, email, is_admin, is_blocked FROM user WHERE email='admin@congofinance.com';")
result = cursor.fetchone()
print(result)

conn.close()
print("\nAdmin account unblocked successfully! Login: admin@congofinance.com / admin2024")


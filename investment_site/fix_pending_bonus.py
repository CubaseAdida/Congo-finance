import sqlite3

db_path = 'instance/users.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add pending_promo_bonus column
cursor.execute("ALTER TABLE user ADD COLUMN pending_promo_bonus FLOAT DEFAULT 0.0")

conn.commit()
conn.close()
print("pending_promo_bonus column added successfully.")

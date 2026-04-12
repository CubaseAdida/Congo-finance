import sqlite3
import os

# Path to the database
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'users.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if column exists
cursor.execute("PRAGMA table_info(user)")
columns = [column[1] for column in cursor.fetchall()]
print("Colonnes existantes:", columns)

if 'referrer_promo_code' not in columns:
    cursor.execute("ALTER TABLE user ADD COLUMN referrer_promo_code VARCHAR(8)")
    print("Colonne 'referrer_promo_code' ajoutée avec succès.")
else:
    print("Colonne 'referrer_promo_code' existe déjà.")

conn.commit()
conn.close()
print("Migration terminée.")

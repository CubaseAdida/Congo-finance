import sqlite3

db_path = 'instance/users.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add missing columns matching model
cursor.execute("ALTER TABLE user ADD COLUMN promo_code VARCHAR(8)")
cursor.execute("ALTER TABLE user ADD COLUMN promo_bonus_balance FLOAT DEFAULT 0.0")
cursor.execute("ALTER TABLE user ADD COLUMN promo_uses INTEGER DEFAULT 0")

# Generate promo_code for existing users (since nullable=False in model, but added nullable)
cursor.execute("UPDATE user SET promo_code = 'TEMP' || id WHERE promo_code IS NULL")

conn.commit()
conn.close()
print("Schema fixed: columns added. Existing users got temporary promo codes.")


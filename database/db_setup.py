import sqlite3
import os

# 🔥 ensure database folder exists
if not os.path.exists("database"):
    os.makedirs("database")

# 🔥 connect database
conn = sqlite3.connect("database/database.db")
cursor = conn.cursor()

# ---------------- USERS TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# ---------------- PREDICTIONS TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    supplier TEXT,
    region INTEGER,
    transport INTEGER,
    delay REAL,
    weather INTEGER,
    demand INTEGER,
    inventory INTEGER,
    traffic INTEGER,
    port_delay INTEGER,
    order_value REAL,
    fuel_cost REAL,
    risk TEXT
)
""")

# ---------------- INSERT ADMIN ----------------
cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
admin = cursor.fetchone()

if not admin:
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        ("admin", "admin123")
    )
    print("Admin user created")
else:
    print("Admin already exists")

# ---------------- SAVE ----------------
conn.commit()
conn.close()

print("Database setup completed successfully")
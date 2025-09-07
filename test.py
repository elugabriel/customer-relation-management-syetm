# seed.py
import sqlite3
import hashlib

DB_NAME = "crm_app.db"

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def seed_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Insert Admin
    cursor.execute("""
    INSERT OR IGNORE INTO admins (username, password, fullname, email, phone)
    VALUES (?, ?, ?, ?, ?)
    """, ("admin1", hash_password("admin123"), "System Admin", "admin@example.com", "08012345678"))

    # Insert Staff
    cursor.execute("""
    INSERT OR IGNORE INTO staff (username, password, fullname, email, phone, department)
    VALUES (?, ?, ?, ?, ?, ?)
    """, ("staff1", hash_password("staff123"), "John Staff", "staff@example.com", "08087654321", "Sales"))

    conn.commit()
    conn.close()
    print("✅ Admin and Staff seeded successfully!")

if __name__ == "__main__":
    seed_data()

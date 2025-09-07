# db.py
import sqlite3
from datetime import datetime

DB_NAME = "crm_app.db"

# -------------------
# CONNECTION HELPERS
# -------------------
def get_connection():
    """Create a database connection."""
    return sqlite3.connect(DB_NAME)


# -------------------
# INITIALIZE DATABASE
# -------------------
def init_db():
    """Initialize all tables in the database."""
    conn = get_connection()
    cursor = conn.cursor()

    # Admins
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        fullname TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        role TEXT DEFAULT 'admin',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Staff
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        fullname TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        department TEXT,
        role TEXT DEFAULT 'staff',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Customers
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        address TEXT,
        gender TEXT,
        dob DATE,
        occupation TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Leads
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        status TEXT DEFAULT 'New',
        assigned_to INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(assigned_to) REFERENCES staff(id)
    )
    """)

    # Feedback
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        handled_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(customer_id) REFERENCES customers(id),
        FOREIGN KEY(handled_by) REFERENCES staff(id)
    )
    """)

    # Activity Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        actor_type TEXT NOT NULL,
        actor_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        reminder_date DATE NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """)


    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")


# -------------------
# CRUD HELPERS
# -------------------

# --- Generic Utility ---
def fetch_all(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_one(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    row = cursor.fetchone()
    conn.close()
    return row


# --- Admins ---
def add_admin(username, password, fullname, email, phone=None, role="admin"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO admins (username, password, fullname, email, phone, role, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (username, password, fullname, email, phone, role, datetime.now()))
    conn.commit()
    conn.close()

def get_admins():
    return fetch_all("SELECT * FROM admins")

def get_admin_by_id(admin_id):
    return fetch_one("SELECT * FROM admins WHERE id = ?", (admin_id,))

def update_admin(admin_id, fullname=None, email=None, phone=None, role=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE admins
        SET fullname = COALESCE(?, fullname),
            email = COALESCE(?, email),
            phone = COALESCE(?, phone),
            role = COALESCE(?, role)
        WHERE id = ?
    """, (fullname, email, phone, role, admin_id))
    conn.commit()
    conn.close()

def delete_admin(admin_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admins WHERE id = ?", (admin_id,))
    conn.commit()
    conn.close()


# --- Staff ---
def add_staff(username, password, fullname, email, phone=None, department=None, role="staff"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO staff (username, password, fullname, email, phone, department, role, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, password, fullname, email, phone, department, role, datetime.now()))
    conn.commit()
    conn.close()

def get_staff():
    return fetch_all("SELECT * FROM staff")

def update_staff(staff_id, fullname=None, email=None, phone=None, department=None, role=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE staff
        SET fullname = COALESCE(?, fullname),
            email = COALESCE(?, email),
            phone = COALESCE(?, phone),
            department = COALESCE(?, department),
            role = COALESCE(?, role)
        WHERE id = ?
    """, (fullname, email, phone, department, role, staff_id))
    conn.commit()
    conn.close()

def delete_staff(staff_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM staff WHERE id = ?", (staff_id,))
    conn.commit()
    conn.close()


# --- Customers ---
def add_customer(name, email=None, phone=None, address=None, gender=None, dob=None, occupation=None, notes=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customers (name, email, phone, address, gender, dob, occupation, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, email, phone, address, gender, dob, occupation, notes, datetime.now()))
    conn.commit()
    conn.close()

def get_customers():
    return fetch_all("SELECT * FROM customers")

def update_customer(customer_id, name=None, email=None, phone=None, address=None, gender=None, dob=None, occupation=None, notes=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers
        SET name = COALESCE(?, name),
            email = COALESCE(?, email),
            phone = COALESCE(?, phone),
            address = COALESCE(?, address),
            gender = COALESCE(?, gender),
            dob = COALESCE(?, dob),
            occupation = COALESCE(?, occupation),
            notes = COALESCE(?, notes)
        WHERE id = ?
    """, (name, email, phone, address, gender, dob, occupation, notes, customer_id))
    conn.commit()
    conn.close()

def delete_customer(customer_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    conn.commit()
    conn.close()


# --- Leads ---
def add_lead(name, email=None, phone=None, status="New", assigned_to=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leads (name, email, phone, status, assigned_to, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, email, phone, status, assigned_to, datetime.now()))
    conn.commit()
    conn.close()

def get_leads():
    return fetch_all("SELECT * FROM leads")

def update_lead(lead_id, name=None, email=None, phone=None, status=None, assigned_to=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE leads
        SET name = COALESCE(?, name),
            email = COALESCE(?, email),
            phone = COALESCE(?, phone),
            status = COALESCE(?, status),
            assigned_to = COALESCE(?, assigned_to)
        WHERE id = ?
    """, (name, email, phone, status, assigned_to, lead_id))
    conn.commit()
    conn.close()

def delete_lead(lead_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
    conn.commit()
    conn.close()


# --- Feedback ---
def add_feedback(customer_id, message, status="Pending", handled_by=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feedback (customer_id, message, status, handled_by, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (customer_id, message, status, handled_by, datetime.now()))
    conn.commit()
    conn.close()

def get_feedback():
    return fetch_all("SELECT * FROM feedback")

def update_feedback(feedback_id, message=None, status=None, handled_by=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE feedback
        SET message = COALESCE(?, message),
            status = COALESCE(?, status),
            handled_by = COALESCE(?, handled_by)
        WHERE id = ?
    """, (message, status, handled_by, feedback_id))
    conn.commit()
    conn.close()

def delete_feedback(feedback_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))
    conn.commit()
    conn.close()


# --- Activity Logs ---
def log_activity(actor_type, actor_id, action, details=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO activity_logs (actor_type, actor_id, action, details, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (actor_type, actor_id, action, details, datetime.now()))
    conn.commit()
    conn.close()

def get_activity_logs():
    return fetch_all("SELECT * FROM activity_logs ORDER BY timestamp DESC")

def delete_activity_log(log_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM activity_logs WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()

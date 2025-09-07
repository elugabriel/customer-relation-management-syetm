# routes/dashboard.py
import sqlite3
import hashlib
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from db import get_connection

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

DB_NAME = "crm_app.db"  # adjust if needed


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ========================
# Role-based dashboards
# ========================
@dashboard_bp.route("/")
def dashboard():
    role = session.get("role")
    if not role:
        flash("You must log in first.", "warning")
        return redirect(url_for("auth.login"))

    if role == "admin":
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM staff")
        total_staff = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM customers")
        total_customers = cursor.fetchone()[0]

        try:
            cursor.execute("SELECT COUNT(*) FROM leads")
            total_leads = cursor.fetchone()[0]
        except:
            total_leads = 0

        try:
            cursor.execute("SELECT COUNT(*) FROM feedback WHERE status='pending'")
            pending_feedback = cursor.fetchone()[0]
        except:
            pending_feedback = 0

        try:
            cursor.execute("""
                SELECT actor_type, actor_id, action, details, timestamp
                FROM system_logs
                ORDER BY timestamp DESC
                LIMIT 5
            """)
            logs = cursor.fetchall()
            recent_logs = [
                {"actor_type": row[0], "actor_id": row[1], "action": row[2], "details": row[3], "timestamp": row[4]}
                for row in logs
            ]
        except:
            recent_logs = []

        conn.close()

        return render_template(
            "dashboard/dashboard_home.html",
            role=role,
            total_staff=total_staff,
            total_customers=total_customers,
            total_leads=total_leads,
            pending_feedback=pending_feedback,
            recent_logs=recent_logs
        )

    elif role == "staff":
        return render_template("dashboard/staff_home.html", role=role)

    elif role == "customer":
        return render_template("dashboard/customer_home.html", role=role)

    else:
        flash("Invalid role.", "danger")
        return redirect(url_for("auth.login"))


# ========================
# Admin Pages
# ========================
@dashboard_bp.route("/update_system")
def update_system():
    return render_template("dashboard/update_system.html")




@dashboard_bp.route("/monitor_system")
def monitor_system():
    return render_template("dashboard/monitor_system.html")


# @dashboard_bp.route("/manage_customers")
# def manage_customers():
#     return render_template("dashboard/manage_customers.html")


@dashboard_bp.route("/register_customer")
def register_customer():
    return render_template("dashboard/register_customer.html")


@dashboard_bp.route("/update_customer_profile")
def update_customer_profile():
    return render_template("dashboard/update_customer_profile.html")


@dashboard_bp.route("/track_sales")
def track_sales():
    return render_template("dashboard/track_sales.html")




# @dashboard_bp.route("/generate_report")
# def generate_report():
#     return render_template("dashboard/generate_report.html")


# ========================
# Customer Pages
# ========================
@dashboard_bp.route("/feedbacks")
def feedbacks():
    return render_template("dashboard/feedbacks.html")


@dashboard_bp.route("/updates")
def updates():
    return render_template("dashboard/updates.html")


@dashboard_bp.route("/transactions")
def transactions():
    return render_template("dashboard/transactions.html")


# ---------------------------
# Manage Users (List & Add)
# ---------------------------
@dashboard_bp.route("/manage_users", methods=["GET", "POST"])
def manage_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        phone = request.form.get("phone")
        role = request.form.get("role")

        try:
            if role == "admin":
                cursor.execute("""
                    INSERT INTO admins (username, password, fullname, email, phone, role)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (username, password, fullname, email, phone, role)
                )
            elif role == "staff":
                cursor.execute("""
                    INSERT INTO staff (username, password, fullname, email, phone, role)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (username, password, fullname, email, phone, role)
                )
            elif role == "customer":
                cursor.execute("""
                    INSERT INTO customers (username, password, fullname, email, phone, role)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (username, password, fullname, email, phone, role)
                )

            conn.commit()
            flash("User added successfully!", "success")
        except sqlite3.IntegrityError:
            flash("Error: Username or email already exists.", "danger")

    # Fetch users from all tables
    users = []
    for role, table in [("admin", "admins"), ("staff", "staff"), ("customer", "customers")]:
        rows = cursor.execute(f"SELECT * FROM {table}").fetchall()
        for row in rows:
            users.append({
                "id": row["id"],
                "username": row["username"],
                "fullname": row["fullname"],  # ✅ fixed: always fullname now
                "email": row["email"],
                "phone": row["phone"],
                "role": role
            })

    conn.close()
    return render_template("dashboard/manage_users.html", users=users)


# ---------------------------
# Edit User
# ---------------------------
@dashboard_bp.route("/edit_user/<role>/<int:user_id>", methods=["GET", "POST"])
def edit_user(role, user_id):
    # only admin can edit users
    if session.get("role") != "admin":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    cursor = conn.cursor()

    # determine table
    if role == "admin":
        table = "admins"
    elif role == "staff":
        table = "staff"
    elif role == "customer":
        table = "customers"
    else:
        flash("Invalid role.", "danger")
        conn.close()
        return redirect(url_for("dashboard.manage_users"))

    # fetch user row
    row = cursor.execute(f"SELECT * FROM {table} WHERE id=?", (user_id,)).fetchone()
    if not row:
        conn.close()
        flash("User not found.", "danger")
        return redirect(url_for("dashboard.manage_users"))

    # convert row to dict for template safety
    user = {k: row[k] for k in row.keys()}

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        try:
            if password:
                hashed = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute(
                    f"UPDATE {table} SET username=?, password=?, fullname=?, email=?, phone=? WHERE id=?",
                    (username, hashed, fullname, email, phone, user_id)
                )
            else:
                cursor.execute(
                    f"UPDATE {table} SET username=?, fullname=?, email=?, phone=? WHERE id=?",
                    (username, fullname, email, phone, user_id)
                )
            conn.commit()
            flash("User updated successfully.", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error updating user: {e}", "danger")
        finally:
            conn.close()

        return redirect(url_for("dashboard.manage_users"))

    # GET -> show form
    conn.close()
    return render_template("dashboard/edit_user.html", user=user, role=role)



# ---------------------------
# Delete User
# ---------------------------
@dashboard_bp.route("/delete_user/<role>/<int:user_id>", methods=["POST"])
def delete_user(role, user_id):
    # only admin can delete
    if session.get("role") != "admin":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("dashboard"))

    conn = get_db_connection()
    cursor = conn.cursor()

    table = "admins" if role == "admin" else "staff" if role == "staff" else "customers"
    try:
        cursor.execute(f"DELETE FROM {table} WHERE id=?", (user_id,))
        conn.commit()
        flash(f"{role.capitalize()} deleted successfully.", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error deleting user: {e}", "danger")
    finally:
        conn.close()

    return redirect(url_for("dashboard.manage_users"))


# ========================
# Assign Role
# ========================
@dashboard_bp.route("/assign_role", methods=["GET", "POST"])
def assign_role():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        user_id = request.form.get("user_id")
        role = request.form.get("role")
        user_type = request.form.get("user_type")  # admin/staff/customer

        table = "admins" if user_type == "admin" else "staff" if user_type == "staff" else "customers"

        cursor.execute(f"UPDATE {table} SET role=? WHERE id=?", (role, user_id))
        conn.commit()
        flash("Role updated successfully!", "success")

    # Fetch users
    users = []
    for role_type, table in [("admin", "admins"), ("staff", "staff"), ("customer", "customers")]:
        rows = cursor.execute(f"SELECT id, username, role FROM {table}").fetchall()
        for row in rows:
            users.append({
                "id": row["id"],
                "username": row["username"],
                "role": row["role"],
                "user_type": role_type
            })

    conn.close()
    return render_template("dashboard/assign_role.html", users=users)


# ========================
# Manage Customers
# ========================
@dashboard_bp.route("/manage_customers", methods=["GET", "POST"])
def manage_customers():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")
        gender = request.form.get("gender")
        occupation = request.form.get("occupation")
        username = request.form.get("username")
        password = request.form.get("password")

        cursor.execute("""
            INSERT INTO customers (fullname, email, phone, address, gender, occupation, username, password, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (fullname, email, phone, address, gender, occupation, username, password, "customer"))

        conn.commit()
        flash("Customer added successfully!", "success")

    customers = cursor.execute("SELECT * FROM customers").fetchall()
    conn.close()
    return render_template("dashboard/manage_customers.html", customers=customers)


# Edit Customer
@dashboard_bp.route("/edit_customer/<int:customer_id>", methods=["GET", "POST"])
def edit_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    customer = cursor.execute("SELECT * FROM customers WHERE id=?", (customer_id,)).fetchone()
    if not customer:
        flash("Customer not found!", "danger")
        return redirect(url_for("dashboard.manage_customers"))

    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")
        gender = request.form.get("gender")
        occupation = request.form.get("occupation")

        cursor.execute("""
            UPDATE customers
            SET fullname=?, email=?, phone=?, address=?, gender=?, occupation=?
            WHERE id=?
        """, (fullname, email, phone, address, gender, occupation, customer_id))

        conn.commit()
        conn.close()
        flash("Customer updated successfully!", "success")
        return redirect(url_for("dashboard.manage_customers"))

    conn.close()
    return render_template("dashboard/edit_customer.html", customer=customer)


# Delete Customer
@dashboard_bp.route("/delete_customer/<int:customer_id>")
def delete_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    conn.commit()
    conn.close()

    flash("Customer deleted successfully!", "success")
    return redirect(url_for("dashboard.manage_customers"))


# ========================
# Schedule Reminder
# ========================
@dashboard_bp.route("/schedule_reminder", methods=["GET", "POST"])
def schedule_reminder():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        title = request.form.get("title")
        description = request.form.get("description")
        reminder_date = request.form.get("reminder_date")

        cursor.execute("""
            INSERT INTO reminders (customer_id, title, description, reminder_date)
            VALUES (?, ?, ?, ?)
        """, (customer_id if customer_id else None, title, description, reminder_date))
        conn.commit()
        flash("Reminder scheduled successfully!", "success")

    # Customers for dropdown
    customers = cursor.execute("SELECT id, fullname FROM customers").fetchall()

    # Fetch reminders with customer names
    reminders = cursor.execute("""
        SELECT r.id, c.fullname, r.title, r.description, r.reminder_date, r.status
        FROM reminders r
        LEFT JOIN customers c ON r.customer_id = c.id
        ORDER BY r.reminder_date ASC
    """).fetchall()

    conn.close()
    return render_template("dashboard/schedule_reminder.html", customers=customers, reminders=reminders)


# Mark Reminder as Done
@dashboard_bp.route("/complete_reminder/<int:reminder_id>")
def complete_reminder(reminder_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE reminders SET status='completed' WHERE id=?", (reminder_id,))
    conn.commit()
    conn.close()
    flash("Reminder marked as completed!", "success")
    return redirect(url_for("dashboard.schedule_reminder"))


# Delete Reminder
@dashboard_bp.route("/delete_reminder/<int:reminder_id>")
def delete_reminder(reminder_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
    conn.commit()
    conn.close()
    flash("Reminder deleted successfully!", "success")
    return redirect(url_for("dashboard.schedule_reminder"))

import csv
from flask import Response

# ========================
# Generate Report
# ========================
@dashboard_bp.route("/generate_report", methods=["GET", "POST"])
def generate_report():
    conn = get_db_connection()
    cursor = conn.cursor()
    report_data, report_type = None, None

    if request.method == "POST":
        report_type = request.form.get("report_type")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        query = ""
        params = []

        if report_type == "customers":
            query = "SELECT id, fullname, email, phone, gender, occupation, created_at FROM customers"
        elif report_type == "users":
            # Merge admins + staff + customers
            query = """
                SELECT username, fullname, email, phone, role, created_at FROM admins
                UNION ALL
                SELECT username, fullname, email, phone, role, created_at FROM staff
                UNION ALL
                SELECT username, fullname, email, phone, role, created_at FROM customers
            """
        elif report_type == "sales":
            query = "SELECT id, customer_id, product, amount, status, created_at FROM sales"
        elif report_type == "reminders":
            query = "SELECT id, title, message, reminder_date, status, created_at FROM reminders"
        elif report_type == "transactions":
            query = "SELECT id, customer_id, amount, type, status, created_at FROM transactions"

        # Apply date filter if provided
        if start_date and end_date and query:
            if "WHERE" in query:
                query += " AND created_at BETWEEN ? AND ?"
            else:
                query += " WHERE created_at BETWEEN ? AND ?"
            params.extend([start_date, end_date])

        if query:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            report_data = [dict(row) for row in rows]

    conn.close()
    return render_template(
        "dashboard/generate_report.html",
        report_data=report_data,
        report_type=report_type
    )


# ========================
# Download Report (CSV)
# ========================
@dashboard_bp.route("/download_report/<report_type>")
def download_report(report_type):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = ""
    if report_type == "customers":
        query = "SELECT id, fullname, email, phone, gender, occupation, created_at FROM customers"
    elif report_type == "users":
        query = """
            SELECT username, fullname, email, phone, role, created_at FROM admins
            UNION ALL
            SELECT username, fullname, email, phone, role, created_at FROM staff
            UNION ALL
            SELECT username, fullname, email, phone, role, created_at FROM customers
        """
    elif report_type == "sales":
        query = "SELECT id, customer_id, product, amount, status, created_at FROM sales"
    elif report_type == "reminders":
        query = "SELECT id, title, message, reminder_date, status, created_at FROM reminders"
    elif report_type == "transactions":
        query = "SELECT id, customer_id, amount, type, status, created_at FROM transactions"

    if not query:
        flash("Invalid report type!", "danger")
        return redirect(url_for("dashboard.generate_report"))

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    # Create CSV
    si = []
    writer = csv.writer(si.append)
    if rows:
        header = rows[0].keys()
        si.append(",".join(header))
        for row in rows:
            si.append(",".join([str(val) if val is not None else "" for val in row]))

    output = "\n".join(si)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={report_type}_report.csv"}
    )

# routes/auth.py
import sqlite3
import hashlib
from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from db import get_connection

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        hashed_password = hash_password(password)

        conn = get_connection()
        cursor = conn.cursor()

        # =======================
        # Check Admins
        # =======================
        cursor.execute(
            "SELECT * FROM admins WHERE username=? AND password=?",
            (username, hashed_password)
        )
        admin = cursor.fetchone()
        if admin:
            session["role"] = "admin"
            session["user_id"] = admin[0]
            session["username"] = admin[1]
            conn.close()
            flash("Welcome Admin!", "success")
            return redirect(url_for("dashboard.dashboard"))

        # =======================
        # Check Staff
        # =======================
        cursor.execute(
            "SELECT * FROM staff WHERE username=? AND password=?",
            (username, hashed_password)
        )
        staff = cursor.fetchone()
        if staff:
            session["role"] = "staff"
            session["user_id"] = staff[0]
            session["username"] = staff[1]
            conn.close()
            flash("Welcome Staff!", "success")
            return redirect(url_for("dashboard.dashboard"))

        # =======================
        # Check Customers (hashed + plaintext)
        # =======================
        cursor.execute(
            "SELECT * FROM customers WHERE username=? AND password=?",
            (username, hashed_password)
        )
        customer = cursor.fetchone()

        if not customer:
            # fallback to plaintext match for migration
            cursor.execute(
                "SELECT * FROM customers WHERE username=? AND password=?",
                (username, password)
            )
            customer = cursor.fetchone()

            if customer:
                # update password to hashed for next login
                customer_id = customer[0]
                cursor.execute(
                    "UPDATE customers SET password=? WHERE id=?",
                    (hashed_password, customer_id)
                )
                conn.commit()

        if customer:
            session["role"] = "customer"
            session["user_id"] = customer[0]
            session["username"] = customer[1]
            conn.close()
            flash("Welcome Customer!", "success")
            return redirect(url_for("dashboard.dashboard"))

        conn.close()
        flash("Invalid username or password", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

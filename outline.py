crm_flask/
├── app.py
├── db.py
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── customer.py
│   └── dashboard.py
├── templates/
│   ├── base.html
│   ├── auth/
│   ├── customer/
│   └── dashboard/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── database/
    └── crm.db


# test_db.py
from db import (
    init_db,
    add_admin, get_admins, update_admin, delete_admin,
    add_staff, get_staff, update_staff, delete_staff,
    add_customer, get_customers, update_customer, delete_customer,
    add_lead, get_leads, update_lead, delete_lead,
    add_feedback, get_feedback, update_feedback, delete_feedback,
    log_activity, get_activity_logs
)

def run_tests():
    print("\n=== Initializing DB ===")
    init_db()

    # ---- Admins ----
    print("\n=== Admins Tests ===")
    add_admin("admin1", "pass123", "John Doe", "admin1@example.com", "123456")
    print("All admins:", get_admins())
    update_admin(1, fullname="John Updated", phone="999999")
    print("Updated admin:", get_admins())
    delete_admin(1)
    print("Admins after delete:", get_admins())

    # ---- Staff ----
    print("\n=== Staff Tests ===")
    add_staff("staff1", "pass123", "Alice Staff", "staff1@example.com", "111111", "Sales")
    print("All staff:", get_staff())
    update_staff(1, department="Marketing")
    print("Updated staff:", get_staff())
    delete_staff(1)
    print("Staff after delete:", get_staff())

    # ---- Customers ----
    print("\n=== Customers Tests ===")
    add_customer("Bob Customer", "bob@example.com", "222222", "Lagos", "Male", "1990-01-01", "Engineer", "VIP")
    print("All customers:", get_customers())
    update_customer(1, address="Abuja", notes="Loyal client")
    print("Updated customer:", get_customers())
    delete_customer(1)
    print("Customers after delete:", get_customers())

    # ---- Leads ----
    print("\n=== Leads Tests ===")
    add_lead("Charlie Lead", "charlie@example.com", "333333", "New", None)
    print("All leads:", get_leads())
    update_lead(1, status="Contacted")
    print("Updated lead:", get_leads())
    delete_lead(1)
    print("Leads after delete:", get_leads())

    # ---- Feedback ----
    print("\n=== Feedback Tests ===")
    add_customer("Test Customer", "test@example.com", "444444")  # re-add a customer
    add_feedback(1, "Great service!", "Pending")
    print("All feedback:", get_feedback())
    update_feedback(1, status="Resolved")
    print("Updated feedback:", get_feedback())
    delete_feedback(1)
    print("Feedback after delete:", get_feedback())

    # ---- Activity Logs ----
    print("\n=== Activity Logs Tests ===")
    log_activity("admin", 1, "created", "Added a new staff")
    print("Activity logs:", get_activity_logs())

if __name__ == "__main__":
    run_tests()

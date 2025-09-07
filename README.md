# CRM System

A lightweight Customer Relationship Management (CRM) system built with **Flask** and **SQLite** to manage customers, staff, sales, reminders, and reports. This system provides role-based dashboards for **Admin**, **Staff**, and **Customer** users.

---

## Table of Contents

1. [Features](#features)
2. [Project Structure](#project-structure)
3. [Technologies Used](#technologies-used)
4. [Installation](#installation)
5. [Database Setup](#database-setup)
6. [Running the Application](#running-the-application)
7. [Usage](#usage)
   - [Admin Dashboard](#admin-dashboard)
   - [Staff Dashboard](#staff-dashboard)
   - [Customer Dashboard](#customer-dashboard)
8. [Password Handling](#password-handling)
9. [Reporting](#reporting)
10. [Screenshots](#screenshots)
11. [Future Enhancements](#future-enhancements)
12. [License](#license)
13. [Author](#author)

---

## Features

### Admin
- Manage users (admin, staff, customers)
- Update system settings
- Monitor system logs
- Generate global reports
- Assign roles

### Staff
- View and update customer information
- Track and record sales
- Schedule follow-ups and reminders
- Generate personal activity reports
- Profile & settings management

### Customer
- View own transactions
- Receive reminders and updates
- Update profile information

---

## Project Structure

```
crm_app/
│
├─ routes/
│   ├─ auth.py
│   ├─ dashboard.py
│
├─ templates/
│   ├─ base.html
│   ├─ auth/
│   │   └─ login.html
│   ├─ dashboard/
│       ├─ dashboard_home.html
│       ├─ staff_home.html
│       ├─ customer_home.html
│       └─ ...
│
├─ static/
│   ├─ css/
│   └─ js/
│
├─ crm_app.db
├─ db.py
├─ app.py
└─ README.md
```

---

## Technologies Used

- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS, Bootstrap 5
- **Authentication:** Flask sessions, SHA256 hashed passwords
- **Reporting:** CSV download of filtered reports

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/crm_app.git
cd crm_app
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Database Setup

1. Initialize SQLite database:

```bash
python db.py
```

2. Ensure tables are created for:
- `admins`
- `staff`
- `customers`
- `sales`
- `reminders`
- `transactions`
- `system_logs`

3. Optionally, add a default admin user:

```sql
INSERT INTO admins (username, password, fullname, email, phone, role)
VALUES ('admin', 'hashed_password_here', 'Admin User', 'admin@example.com', '1234567890', 'admin');
```

---

## Running the Application

Start the Flask server:

```bash
python app.py
```

Open your browser and navigate to:

```
http://127.0.0.1:5000/auth/login
```

---

## Usage

### Admin Dashboard
- Add/edit/delete staff and customers
- Assign roles
- View recent system activity logs
- Generate reports

### Staff Dashboard
- View/update assigned customers
- Track new and existing sales
- Schedule and manage reminders
- Generate personal activity reports

### Customer Dashboard
- View transactions
- Receive reminders
- Update personal profile

---

## Password Handling

- Admin and Staff passwords are stored **hashed** using SHA256.
- Customer passwords support both **hashed and plaintext** for migration.
- Plaintext customer passwords are automatically updated to hashed upon first login.

---

## Reporting

- Users can generate reports filtered by date range.
- CSV downloads are supported for all report types:
  - Customers
  - Users
  - Sales
  - Reminders
  - Transactions

---

## Screenshots

*(Optional: Add screenshots of Admin, Staff, Customer dashboards)*

---

## Future Enhancements

- Integrate **email notifications** for reminders.
- Add **role-based analytics dashboards**.
- Support **multi-user concurrent sessions**.
- Implement **REST API** for external integrations.
- Add **password reset functionality**.

---

## License

This project is licensed under the MIT License.

---




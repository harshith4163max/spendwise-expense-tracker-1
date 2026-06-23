# 💸 SpendWise — Django Expense Tracker

A beautiful, full-featured personal finance tracker built with Django.

---

## ✨ Features

| Feature | Details |
|---|---|
| 📊 **Dashboard** | At-a-glance stats, 7-day chart, category breakdown, savings goals |
| 💳 **Transactions** | Add, edit, delete, filter & search income/expense entries |
| 📂 **Categories** | Custom emoji categories with color coding |
| 🎯 **Budgets** | Monthly budget limits per category with progress bars |
| 💎 **Savings Goals** | Track savings goals with visual progress |
| 📈 **Analytics** | 6-month trend charts + category donut chart |
| 👤 **Profile** | Avatar, bio, currency, monthly budget settings |
| 🔐 **Auth** | Register, login, logout with session management |

---

## 🚀 Quick Start

### Option 1 — One command (Linux/macOS)
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2 — Manual setup
```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Start the server
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## 🔑 Default Demo Credentials (via setup.sh)

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `admin123` |

---

## 📁 Project Structure

```
expense_tracker/
├── expense_tracker/        # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tracker/                # Main app
│   ├── models.py           # UserProfile, Category, Transaction, Budget, SavingsGoal
│   ├── views.py            # All page views
│   ├── forms.py            # Django forms
│   ├── urls.py             # URL routing
│   ├── admin.py            # Admin panel config
│   ├── signals.py          # Auto-create user profile
│   └── templates/tracker/
│       ├── base.html       # Sidebar + topbar layout
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── transactions.html
│       ├── transaction_form.html
│       ├── categories.html
│       ├── budgets.html
│       ├── savings.html
│       ├── analytics.html
│       └── profile.html
├── manage.py
├── requirements.txt
└── setup.sh
```

---

## 🗃️ Data Models

- **UserProfile** — Extended user with avatar, phone, currency, monthly budget
- **Category** — Named categories with emoji icon and hex color (income/expense)
- **Transaction** — Core model with title, amount, type, category, date, note
- **Budget** — Monthly budget limits per category
- **SavingsGoal** — Goal with target amount, current amount, deadline

---

## 🎨 Tech Stack

- **Backend**: Django 4.2, SQLite
- **Frontend**: Pure HTML/CSS + vanilla JS (no framework)
- **Charts**: Chart.js 4.4
- **Fonts**: Syne, Instrument Sans, DM Mono (Google Fonts)
- **Theme**: Dark luxury fintech aesthetic with lime-green accent

---

## 🌐 Pages & URLs

| URL | Page |
|---|---|
| `/login/` | Login |
| `/register/` | Register |
| `/dashboard/` | Main dashboard |
| `/transactions/` | Transaction list with filters |
| `/transactions/add/` | Add transaction |
| `/categories/` | Manage categories |
| `/budgets/` | Set monthly budgets |
| `/savings/` | Savings goals |
| `/analytics/` | Charts & analytics |
| `/profile/` | User profile & settings |
| `/admin/` | Django admin panel |

---

## 📝 Notes

- Uses SQLite by default — swap for PostgreSQL in `settings.py` for production
- Media files (avatars) stored in `/media/` — configure for production with cloud storage
- Set `SECRET_KEY` and `DEBUG=False` for production deployment

#!/bin/bash
# ============================================================
#  SpendWise — Quick Setup Script
# ============================================================

set -e

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   💸 SpendWise — Expense Tracker     ║"
echo "║   Setup & Launch Script              ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

PYTHON=$(command -v python3)
echo "✅ Python: $($PYTHON --version)"

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON -m venv venv
fi

# Activate
source venv/bin/activate
echo "✅ Virtual environment activated"

# Install deps
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Migrate
echo "🗄️  Running migrations..."
python manage.py migrate --run-syncdb 2>/dev/null || python manage.py migrate

# Create superuser (optional, skip if exists)
echo ""
echo "👤 Creating demo admin user (skip if exists)..."
python manage.py shell -c "
from django.contrib.auth.models import User
from tracker.models import UserProfile, Category
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@spendwise.com', 'admin123')
    u.first_name = 'Admin'
    u.last_name = 'User'
    u.save()
    defaults = [
        ('Food & Dining','🍔','#FF6B6B','expense'),
        ('Transport','🚗','#45B7D1','expense'),
        ('Housing','🏠','#96CEB4','expense'),
        ('Health','💊','#4ECDC4','expense'),
        ('Entertainment','🎮','#DDA0DD','expense'),
        ('Shopping','👗','#F0A500','expense'),
        ('Education','📚','#74B9FF','expense'),
        ('Utilities','💡','#FFEAA7','expense'),
        ('Salary','💰','#55EFC4','income'),
        ('Freelance','💻','#A29BFE','income'),
    ]
    for name, icon, color, ctype in defaults:
        Category.objects.get_or_create(user=u, name=name, defaults={'icon':icon,'color':color,'type':ctype})
    print('✅ Demo user created: admin / admin123')
else:
    print('ℹ️  Admin user already exists')
" 2>/dev/null

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║  🚀 Launching SpendWise on port 8000...      ║"
echo "╠══════════════════════════════════════════════╣"
echo "║  🌐 App:      http://127.0.0.1:8000          ║"
echo "║  🔧 Admin:    http://127.0.0.1:8000/admin    ║"
echo "║  👤 Login:    admin / admin123               ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

python manage.py runserver 0.0.0.0:8000

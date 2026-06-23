from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import date, timedelta
import json

from .models import UserProfile, Category, Transaction, Budget, SavingsGoal
from .forms import (LoginForm, RegisterForm, ProfileForm, TransactionForm,
                    CategoryForm, BudgetForm, SavingsGoalForm)


def get_or_create_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'tracker/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        profile = get_or_create_profile(user)
        # Create default categories
        defaults = [
            ('Food & Dining', '🍔', '#FF6B6B', 'expense'),
            ('Transport', '🚗', '#45B7D1', 'expense'),
            ('Housing', '🏠', '#96CEB4', 'expense'),
            ('Health', '💊', '#4ECDC4', 'expense'),
            ('Entertainment', '🎮', '#DDA0DD', 'expense'),
            ('Shopping', '👗', '#F0A500', 'expense'),
            ('Education', '📚', '#74B9FF', 'expense'),
            ('Utilities', '💡', '#FFEAA7', 'expense'),
            ('Clothes', '👕', '#F0A500', 'expense'),
            ('Salary', '💰', '#55EFC4', 'income'),
            ('Freelance', '💻', '#A29BFE', 'income'),
        ]
        for name, icon, color, ctype in defaults:
            Category.objects.get_or_create(user=user, name=name, defaults={'icon': icon, 'color': color, 'type': ctype})
        login(request, user)
        messages.success(request, f'Welcome to SpendWise, {user.first_name}! 🎉')
        return redirect('dashboard')
    return render(request, 'tracker/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    profile = get_or_create_profile(request.user)
    today = date.today()
    month_start = today.replace(day=1)

    # Current month stats
    month_transactions = Transaction.objects.filter(
        user=request.user,
        date__year=today.year,
        date__month=today.month
    )
    total_income = month_transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = month_transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    net_balance = total_income - total_expense

    # All-time balance
    all_income = Transaction.objects.filter(user=request.user, type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    all_expense = Transaction.objects.filter(user=request.user, type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    total_balance = all_income - all_expense

    # Recent transactions
    recent = Transaction.objects.filter(user=request.user).select_related('category')[:8]

    # Category breakdown (expenses this month)
    cat_breakdown = month_transactions.filter(type='expense').values(
        'category__name', 'category__color', 'category__icon'
    ).annotate(total=Sum('amount')).order_by('-total')[:6]

    # Last 7 days daily data
    daily_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        exp = Transaction.objects.filter(user=request.user, date=d, type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        inc = Transaction.objects.filter(user=request.user, date=d, type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        daily_data.append({'date': d.strftime('%a'), 'expense': float(exp), 'income': float(inc)})

    # Budgets
    budgets = Budget.objects.filter(user=request.user, month=today.month, year=today.year).select_related('category')

    # Savings goals
    savings = SavingsGoal.objects.filter(user=request.user)[:3]

    budget_used_pct = 0
    if profile.monthly_budget > 0:
        budget_used_pct = min(int((total_expense / profile.monthly_budget) * 100), 100)

    context = {
        'profile': profile,
        'total_balance': total_balance,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'recent': recent,
        'cat_breakdown': list(cat_breakdown),
        'daily_data': json.dumps(daily_data),
        'budgets': budgets,
        'savings': savings,
        'budget_used_pct': budget_used_pct,
        'month_name': today.strftime('%B %Y'),
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def transactions(request):
    profile = get_or_create_profile(request.user)
    qs = Transaction.objects.filter(user=request.user).select_related('category')

    # Filters
    ttype = request.GET.get('type', '')
    category = request.GET.get('category', '')
    period = request.GET.get('period', 'all')
    search = request.GET.get('search', '')

    if ttype:
        qs = qs.filter(type=ttype)
    if category:
        qs = qs.filter(category__id=category)
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(note__icontains=search))

    today = date.today()
    if period == 'today':
        qs = qs.filter(date=today)
    elif period == 'week':
        qs = qs.filter(date__gte=today - timedelta(days=7))
    elif period == 'month':
        qs = qs.filter(date__year=today.year, date__month=today.month)
    elif period == 'year':
        qs = qs.filter(date__year=today.year)

    total_shown = qs.aggregate(
        income=Sum('amount', filter=Q(type='income')),
        expense=Sum('amount', filter=Q(type='expense'))
    )

    categories = Category.objects.filter(user=request.user)
    total_income = total_shown['income'] or 0
    total_expense = total_shown['expense'] or 0
    context = {
        'profile': profile,
        'transactions': qs,
        'categories': categories,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_total': total_income - total_expense,
        'filters': {'type': ttype, 'category': category, 'period': period, 'search': search},
    }
    return render(request, 'tracker/transactions.html', context)


@login_required
def add_transaction(request):
    profile = get_or_create_profile(request.user)
    form = TransactionForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        transaction = form.save(commit=False)
        transaction.user = request.user
        transaction.save()
        messages.success(request, 'Transaction added successfully! ✅')
        return redirect('transactions')
    return render(request, 'tracker/transaction_form.html', {'form': form, 'profile': profile, 'action': 'Add'})


@login_required
def edit_transaction(request, pk):
    profile = get_or_create_profile(request.user)
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    form = TransactionForm(request.user, request.POST or None, instance=transaction)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Transaction updated! ✅')
        return redirect('transactions')
    return render(request, 'tracker/transaction_form.html', {'form': form, 'profile': profile, 'action': 'Edit'})


@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted.')
    return redirect('transactions')


@login_required
def categories_view(request):
    profile = get_or_create_profile(request.user)
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cat = form.save(commit=False)
        cat.user = request.user
        cat.save()
        messages.success(request, 'Category created! 🎨')
        return redirect('categories')
    categories = Category.objects.filter(user=request.user).annotate(
        transaction_count=Count('transactions')
    )
    return render(request, 'tracker/categories.html', {
        'profile': profile, 'form': form, 'categories': categories
    })


@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
    return redirect('categories')


@login_required
def budgets_view(request):
    profile = get_or_create_profile(request.user)
    today = date.today()
    form = BudgetForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        budget = form.save(commit=False)
        budget.user = request.user
        budget.save()
        messages.success(request, 'Budget set! 💰')
        return redirect('budgets')
    budgets = Budget.objects.filter(user=request.user, month=today.month, year=today.year).select_related('category')
    return render(request, 'tracker/budgets.html', {
        'profile': profile, 'form': form, 'budgets': budgets,
        'month_name': today.strftime('%B %Y')
    })


@login_required
def savings_view(request):
    profile = get_or_create_profile(request.user)
    form = SavingsGoalForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        goal = form.save(commit=False)
        goal.user = request.user
        goal.save()
        messages.success(request, 'Savings goal created! 🎯')
        return redirect('savings')
    goals = SavingsGoal.objects.filter(user=request.user)
    return render(request, 'tracker/savings.html', {
        'profile': profile, 'form': form, 'goals': goals
    })


@login_required
def update_savings(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        amount = request.POST.get('amount', 0)
        try:
            goal.current_amount = float(amount)
            goal.save()
            messages.success(request, 'Savings updated! 🎉')
        except:
            pass
    return redirect('savings')


@login_required
def profile_view(request):
    profile = get_or_create_profile(request.user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        user = request.user
        user.first_name = form.cleaned_data.get('first_name', user.first_name)
        user.last_name = form.cleaned_data.get('last_name', user.last_name)
        user.email = form.cleaned_data.get('email', user.email)
        user.save()
        messages.success(request, 'Profile updated! ✨')
        return redirect('profile')

    today = date.today()
    stats = {
        'total_transactions': Transaction.objects.filter(user=request.user).count(),
        'this_month': Transaction.objects.filter(user=request.user, date__month=today.month, date__year=today.year).count(),
        'categories': Category.objects.filter(user=request.user).count(),
        'savings_goals': SavingsGoal.objects.filter(user=request.user).count(),
    }
    return render(request, 'tracker/profile.html', {
        'profile': profile, 'form': form, 'stats': stats
    })


@login_required
def analytics(request):
    profile = get_or_create_profile(request.user)
    today = date.today()

    # Monthly trend (last 6 months)
    monthly = []
    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        exp = Transaction.objects.filter(user=request.user, date__year=y, date__month=m, type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        inc = Transaction.objects.filter(user=request.user, date__year=y, date__month=m, type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        from calendar import month_abbr
        monthly.append({'month': month_abbr[m], 'expense': float(exp), 'income': float(inc)})

    # Category breakdown
    cat_data = Transaction.objects.filter(
        user=request.user, type='expense',
        date__year=today.year, date__month=today.month
    ).values('category__name', 'category__color', 'category__icon').annotate(
        total=Sum('amount')
    ).order_by('-total')

    total_cat = sum(c['total'] for c in cat_data) or 1

    context = {
        'profile': profile,
        'monthly_data': json.dumps(monthly),
        'cat_data': json.dumps([{
            'name': c['category__name'] or 'Uncategorized',
            'color': c['category__color'] or '#ccc',
            'icon': c['category__icon'] or '📦',
            'total': float(c['total']),
            'pct': round(float(c['total']) / float(total_cat) * 100, 1)
        } for c in cat_data]),
        'month_name': today.strftime('%B %Y'),
    }
    return render(request, 'tracker/analytics.html', context)

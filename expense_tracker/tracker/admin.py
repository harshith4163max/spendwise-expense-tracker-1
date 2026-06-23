from django.contrib import admin
from .models import UserProfile, Category, Transaction, Budget, SavingsGoal

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'currency', 'monthly_budget']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'type', 'user']
    list_filter = ['type']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'type', 'category', 'date', 'user']
    list_filter = ['type', 'date']
    search_fields = ['title']

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'month', 'year']

@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'target_amount', 'current_amount', 'user']

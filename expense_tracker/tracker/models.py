from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    currency = models.CharField(max_length=5, default='₹')
    monthly_budget = models.DecimalField(max_digits=12, decimal_places=2, default=50000)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Category(models.Model):
    ICONS = [
        ('🍔', 'Food'), ('🚗', 'Transport'), ('🏠', 'Housing'),
        ('💊', 'Health'), ('🎮', 'Entertainment'), ('�', 'Clothes'),
        ('📚', 'Education'), ('✈️', 'Travel'), ('💡', 'Utilities'),
        ('💰', 'Income'), ('🎁', 'Gifts'), ('📱', 'Technology'),
        ('🏋️', 'Fitness'), ('🐾', 'Pets'), ('📦', 'Other'),
    ]
    COLORS = [
        ('#FF6B6B', 'Red'), ('#4ECDC4', 'Teal'), ('#45B7D1', 'Blue'),
        ('#96CEB4', 'Green'), ('#FFEAA7', 'Yellow'), ('#DDA0DD', 'Purple'),
        ('#F0A500', 'Orange'), ('#E17055', 'Coral'), ('#74B9FF', 'Sky'),
        ('#A29BFE', 'Lavender'),
    ]
    TYPE_CHOICES = [('expense', 'Expense'), ('income', 'Income')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, default='📦')
    color = models.CharField(max_length=7, default='#A29BFE')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='expense')

    class Meta:
        verbose_name_plural = 'Categories'
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TYPE_CHOICES = [('expense', 'Expense'), ('income', 'Income')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='transactions')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='expense')
    date = models.DateField(default=timezone.now)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.amount}"


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.IntegerField()
    year = models.IntegerField()

    class Meta:
        unique_together = ('user', 'category', 'month', 'year')

    def spent(self):
        from django.db.models import Sum
        total = Transaction.objects.filter(
            user=self.user, category=self.category,
            date__month=self.month, date__year=self.year, type='expense'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        return total

    def percentage(self):
        if self.amount == 0:
            return 0
        return min(int((self.spent() / self.amount) * 100), 100)

    def __str__(self):
        return f"{self.category.name} budget - {self.month}/{self.year}"


class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_goals')
    title = models.CharField(max_length=200)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deadline = models.DateField(null=True, blank=True)
    icon = models.CharField(max_length=10, default='🎯')
    created_at = models.DateTimeField(auto_now_add=True)

    def percentage(self):
        if self.target_amount == 0:
            return 0
        return min(int((self.current_amount / self.target_amount) * 100), 100)

    def __str__(self):
        return self.title

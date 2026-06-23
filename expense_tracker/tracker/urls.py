from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='tracker/password_reset.html',
        email_template_name='tracker/password_reset_email.html',
        subject_template_name='tracker/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='tracker/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='tracker/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='tracker/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('transactions/', views.transactions, name='transactions'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('transactions/<int:pk>/edit/', views.edit_transaction, name='edit_transaction'),
    path('transactions/<int:pk>/delete/', views.delete_transaction, name='delete_transaction'),
    path('categories/', views.categories_view, name='categories'),
    path('categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
    path('budgets/', views.budgets_view, name='budgets'),
    path('savings/', views.savings_view, name='savings'),
    path('savings/<int:pk>/update/', views.update_savings, name='update_savings'),
    path('profile/', views.profile_view, name='profile'),
    path('analytics/', views.analytics, name='analytics'),
]

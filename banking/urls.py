from django.urls import path
from .views import UserForgotPasswordView, UserPasswordResetConfirmView
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.logining, name='login'),
    path('create_account/', views.create_account, name='create_account'),
    path('success_account/', views.success_account, name='success_account'),
    path('cabinet/', views.cabinet, name='cabinet'),
    path('transfer/', views.transfer, name='transfer'),
    path('success_transfer/', views.success_transfer, name='success_transfer'),
    path('logout/', views.logouting, name='logout'),
    path('password-reset/', UserForgotPasswordView.as_view(), name='password_reset'),
    path('set-new-password/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.logining, name='login'),
    path('create_account/', views.create_account, name='create_account'),
    path('success_account/', views.success_account, name='success_account'),
    path('cabinet/', views.cabinet, name='cabinet'),
    path('transfer/', views.transfer, name='transfer'),
    path('success_transfer/', views.success_transfer, name='success_transfer'),
]

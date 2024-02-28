from django import forms
from django.contrib.auth.models import User


class CreateAccountForm(forms.Form):
    first_name = forms.CharField(max_length=25)
    last_name = forms.CharField(max_length=25)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class PaymentForm(forms.Form):
    email = forms.EmailField()
    amount = forms.DecimalField(max_digits=10, decimal_places=2)

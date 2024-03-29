from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from .forms import CreateAccountForm, LoginForm, PaymentForm, UserForgotPasswordForm, UserSetNewPasswordForm
from django.db import transaction, connection
from django.db.models import Q
from .models import Account, User, Transaction
from .conversion_rates import currency_rates

from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy


class UserForgotPasswordView(SuccessMessageMixin, PasswordResetView):
    """
    Представление по сбросу пароля по почте
    """
    form_class = UserForgotPasswordForm
    template_name = 'banking/user_password_reset.html'
    success_url = reverse_lazy('home')
    success_message = 'Письмо с инструкцией по восстановлению пароля отправлена на ваш email'
    subject_template_name = 'banking/email/password_subject_reset_mail.txt'
    email_template_name = 'banking/email/password_reset_mail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Запрос на восстановление пароля'
        return context


class UserPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    """
    Представление установки нового пароля
    """
    form_class = UserSetNewPasswordForm
    template_name = 'banking/user_password_set_new.html'
    success_url = reverse_lazy('home')
    success_message = 'Пароль успешно изменен. Можете авторизоваться на сайте.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Установить новый пароль'
        return context


def home(request):
    isauth = request.user.is_authenticated
    return render(request, 'banking/home.html', {'isauth': isauth})


def logining(request):
    if request.user.is_authenticated:
        return redirect('cabinet')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username'].lower()
            password = form.cleaned_data['password']
            if User.objects.filter(username=username).exists():
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('cabinet')
                else:
                    messages.error(request, 'Invalid username or password.')
            else:
                messages.error(request, 'Invalid username or password.')
    return render(request, 'banking/login.html')


def create_account(request):
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username__iexact=form.cleaned_data['email']).exists():
                messages.error(request, 'User with this email already exists.')
                return render(request, 'banking/create_account.html', {'form': form})
            # Создаем пользователя
            else:
                user = User.objects.create_user(username=form.cleaned_data['email'].lower(),
                                                email=form.cleaned_data['email'],
                                                password=form.cleaned_data['password'],
                                                first_name=form.cleaned_data['first_name'],
                                                last_name=form.cleaned_data['last_name'])

                # Создаем запись в таблице Account
                account = Account.objects.create(user=user)

                # Перенаправляем на страницу успеха
                return redirect('success_account')
        else:
            messages.error(request, 'Invalid data.')
    return render(request, 'banking/create_account.html')


def success_account(request):
    return render(request, 'banking/success_account.html')


def cabinet(request):
    if not request.user.is_authenticated:
        return redirect('login')
    # Получаем объект пользователя из запроса
    auth_user = request.user

    # Получаем объект Account для текущего пользователя, если он существует
    try:
        account = Account.objects.get(user=auth_user)
    except Account.DoesNotExist:
        account = None
    transactions = Transaction.objects.filter(Q(from_account=account) | Q(to_account=account)).order_by('-id')
    # Передаем информацию об аккаунте в контекст шаблона
    return render(request, 'banking/cabinet.html',
                  {'auth_user': auth_user, 'account': account, 'transactions': transactions,
                   'currency_rates': currency_rates})


@transaction.atomic
def transfer(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            recipient = form.cleaned_data['email']
            amount = form.cleaned_data['amount']
            if User.objects.filter(username=recipient).exists():
                # проверяем есть ли деньги на счету у переводящего
                if amount > request.user.account.balance:
                    messages.error(request, 'Insufficient funds.')
                    return redirect('transfer')
                else:
                    request.user.account.balance -= amount
                    request.user.account.save()
                    account = Account.objects.get(user__username=recipient)
                    account.balance += amount
                    account.save()
                    Transaction.objects.create(from_account=request.user.account, to_account=account, amount=amount)
                    return redirect('success_transfer')
            else:
                messages.error(request, 'Account not found.')
    return render(request, 'banking/transfer.html')


def success_transfer(request):
    return render(request, 'banking/success_transfer.html')


def logouting(request):
    logout(request)
    return render(request, 'banking/home.html')

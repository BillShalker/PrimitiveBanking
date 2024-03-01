from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CreateAccountForm, LoginForm, PaymentForm
from django.db import transaction, connection
from .models import Account, User, Transaction


def home(request):
    return render(request, 'banking/home.html')


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
    transactions = Transaction.objects.filter(from_account=account).all()

    # Передаем информацию об аккаунте в контекст шаблона
    return render(request, 'banking/cabinet.html',
                  {'auth_user': auth_user, 'account': account, 'transactions': transactions})


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

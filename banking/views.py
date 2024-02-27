from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CreateAccountForm, LoginForm
from .models import Account, User


def home(request):
    return render(request, 'banking/home.html')


def logining(request):
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
            user = User.objects.create_user(username=form.cleaned_data['email'].lower(), email=form.cleaned_data['email'],
                                            password=form.cleaned_data['password'])

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
    # Получаем объект пользователя из запроса
    auth_user = request.user

    # Получаем объект Account для текущего пользователя, если он существует
    try:
        account = Account.objects.get(user=auth_user)
    except Account.DoesNotExist:
        account = None

    # Передаем информацию об аккаунте в контекст шаблона
    return render(request, 'banking/cabinet.html', {'auth_user': auth_user, 'account': account})

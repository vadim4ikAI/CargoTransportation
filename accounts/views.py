from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login

def logout_view(request):
    logout(request)
    return redirect('home')


def home_view(request):
    return render(request, "home.html")

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Проверка на существование пользователя
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Это имя пользователя уже занято.')
            return render(request, 'accounts/register.html')  # Вернуть на страницу регистрации

        # Создание нового пользователя
        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, 'Регистрация прошла успешно!')
        return redirect('login')  # Перенаправление на страницу входа

    return render(request, 'accounts/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему!')
            return redirect('home')  # Перенаправление на главную страницу
        else:
            messages.error(request, 'Неверный логин или пароль.')  # Сообщение об ошибке
    return render(request, 'accounts/login.html')

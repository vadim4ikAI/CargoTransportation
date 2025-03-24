from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Driver, UserProfile, UserRole, Trip, TripDriver, Profit, Client, City, Route
import random
import json
from datetime import date
from collections import defaultdict
from django.utils import timezone
import csv
from decimal import Decimal

@csrf_exempt
def calculate_route(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            departure_city_name = data.get('departure_city')  # Получаем название города отправления
            arrival_city_name = data.get('arrival_city')      # Получаем название города назначения

            # Получаем идентификаторы городов из базы данных по их названиям
            departure_city = City.objects.filter(name__iexact=departure_city_name).first()
            arrival_city = City.objects.filter(name__iexact=arrival_city_name).first()

            # Проверка на наличие городов
            if not departure_city or not arrival_city:
                return JsonResponse({'error': 'Один или оба города не найдены.'}, status=400)

            # Генерируем случайное расстояние и цену
            distance = random.randint(100, 1000)  # расстояние от 100 до 1000 км
            price = distance * 50  # цена 0.5 за км

            # Сохраняем маршрут в базе данных
            route = Route(
                departure_city=departure_city,  # Используем ID города отправления
                arrival_city=arrival_city,      # Используем ID города назначения
                distance=distance,
                price=price
            )
            route.save()

            return JsonResponse({'distance': distance, 'price': price})
        except Exception as e:
            print(f"Ошибка: {str(e)}")  # Логирование ошибки в консоль
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def get_cities(request):
    if 'term' in request.GET:
        term = request.GET['term']
        cities = City.objects.filter(name__icontains=term)  # Фильтрация по введенному тексту
        city_names = [city.name for city in cities]
        return JsonResponse(city_names, safe=False)
    return JsonResponse([], safe=False)

def logout_view(request):
    logout(request)  # Очистка сессии
    return redirect('home')  # Перенаправление на главную страницу


def home_view(request):
    return render(request, "home.html")

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone_number = request.POST['phone_number']
        
        # Проверка на существование пользователя
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Это имя пользователя уже занято.')
            return render(request, 'accounts/register.html')  # Вернуть на страницу регистрации

        # Создание нового пользователя
        user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
        user.save()

        # Добавляем нового клиента
        Client.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            user=user
        )

        messages.success(request, 'Регистрация прошла успешно!')
        return redirect('login')  # Перенаправление на страницу входа

    return render(request, 'accounts/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Вход под новым пользователем
            messages.success(request, 'Вы успешно вошли в систему!')
            return redirect('home')  # Перенаправление на главную страницу
        else:
            messages.error(request, 'Неверный логин или пароль.')
    return render(request, 'accounts/login.html')

@login_required
def cabinet(request):
    context = {}
    
    try:
        profile = request.user.profile
    except:
        profile = UserProfile.objects.create(
            user=request.user,
            role=UserRole.CLIENT
        )
    
    context['profile'] = profile

    if profile.role == UserRole.DRIVER:
        try:
            driver = Driver.objects.get(user=request.user)
        except Driver.DoesNotExist:
            driver = Driver.objects.create(
                user=request.user,
                name=request.user.username,
                license_issue_date=date.today(),
            )
        
        # Получаем параметры сортировки и поиска
        sort_by = request.GET.get('sort_by', 'start_date')
        search_query = request.GET.get('search', '')
        
        # Получаем поездки водителя
        trips = TripDriver.objects.filter(driver=driver)
        if search_query:
            trips = trips.filter(
                Q(trip__route__departure_city__name__icontains=search_query) |
                Q(trip__route__arrival_city__name__icontains=search_query) |
                Q(trip__client__first_name__icontains=search_query) |
                Q(trip__client__last_name__icontains=search_query)
            )
        
        # Получаем статистику выплат по месяцам
        profits = Profit.objects.filter(driver=driver)
        monthly_stats = defaultdict(Decimal)
        for profit in profits:
            month = profit.date.strftime('%Y-%m')  # Форматируем дату в "ГГГГ-ММ"
            monthly_stats[month] += profit.amount
        
        context['monthly_stats'] = monthly_stats
        context['trips'] = trips
        
        # Сортировка
        if sort_by == 'rating':
            trips = trips.order_by('-trip__rating')
        elif sort_by == 'start_date':
            trips = trips.order_by('-trip__start_date')
        elif sort_by == 'cargo_weight':
            trips = trips.order_by('-trip__cargo_weight')
        
        # Получаем прибыль
        profits = Profit.objects.filter(driver=driver).order_by('-code')
        total_profit = profits.aggregate(Sum('amount'))['amount__sum'] or 0
        
        context.update({
            'driver': driver,
            'profits': profits,
            'total_profit': total_profit,
            'search_query': search_query,
            'sort_by': sort_by
        })
        
        if request.method == 'POST' and request.FILES.get('photo'):
            try:
                driver.photo = request.FILES['photo']
                driver.save()
                messages.success(request, 'Фото успешно обновлено')
                return redirect('cabinet')
            except Exception as e:
                messages.error(request, 'Ошибка при загрузке фото')
    
    return render(request, 'cabinet.html', context)

@login_required
def export_trips(request):
    driver = Driver.objects.get(user=request.user)
    trips = TripDriver.objects.filter(driver=driver)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="trips.csv"'

    writer = csv.writer(response)
    writer.writerow(['Дата', 'Маршрут', 'Клиент', 'Вес груза', 'Рейтинг', 'Отзыв'])

    for trip_driver in trips:
        trip = trip_driver.trip
        writer.writerow([
            trip.start_date,
            f"{trip.route.departure_city} → {trip.route.arrival_city}",
            f"{trip.client.first_name} {trip.client.last_name}",
            trip.cargo_weight,
            trip.rating,
            trip.feedback
        ])

    return response

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class UserRole(models.TextChoices):
    CLIENT = 'CLIENT', 'Клиент'
    DRIVER = 'DRIVER', 'Водитель'
    ADMIN = 'ADMIN', 'Администратор'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CLIENT,
        verbose_name='Роль пользователя'
    )

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class City(models.Model):
    code = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Название города')

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def __str__(self):
        return self.name


class Route(models.Model):
    code = models.AutoField(primary_key=True)
    departure_city = models.ForeignKey(City, related_name='departure_routes', on_delete=models.CASCADE, verbose_name='Город отправления')
    arrival_city = models.ForeignKey(City, related_name='arrival_routes', on_delete=models.CASCADE, verbose_name='Город назначения')
    distance = models.FloatField(verbose_name='Расстояние')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')

    class Meta:
        verbose_name = 'Маршрут'
        verbose_name_plural = 'Маршруты'

    def __str__(self):
        return f"{self.departure_city} to {self.arrival_city}"


class Trip(models.Model):
    code = models.AutoField(primary_key=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, verbose_name='Маршрут')
    client = models.ForeignKey('Client', on_delete=models.CASCADE, verbose_name='Клиент')
    cargo_weight = models.FloatField(verbose_name='Вес груза')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    rating = models.IntegerField(verbose_name='Рейтинг')
    feedback = models.TextField(verbose_name='Отзыв')

    class Meta:
        verbose_name = 'Поездка'
        verbose_name_plural = 'Поездки'

    def __str__(self):
        return f"Поездка {self.code}"


class TripService(models.Model):
    code = models.AutoField(primary_key=True)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, verbose_name='Поездка')
    service = models.ForeignKey('AdditionalService', on_delete=models.CASCADE, verbose_name='Услуга')

    class Meta:
        verbose_name = 'Услуга поездки'
        verbose_name_plural = 'Услуги поездок'

    def __str__(self):
        return f"Услуга для поездки {self.trip.code}"


class AdditionalService(models.Model):
    code = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Название услуги')

    class Meta:
        verbose_name = 'Дополнительная услуга'
        verbose_name_plural = 'Дополнительные услуги'

    def __str__(self):
        return self.name


class Client(models.Model):
    code = models.AutoField(primary_key=True, serialize=False)
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    phone_number = models.CharField(max_length=15, verbose_name='Номер телефона')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client')

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver', null=True)
    code = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Имя водителя')
    license_issue_date = models.DateField(verbose_name='Дата выдачи прав')
    photo = models.ImageField(upload_to='drivers_photos/', null=True, blank=True, verbose_name='Фото')

    class Meta:
        verbose_name = 'Водитель'
        verbose_name_plural = 'Водители'

    def __str__(self):
        return self.name


class TripDriver(models.Model):
    code = models.AutoField(primary_key=True)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, verbose_name='Поездка')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name='Водитель')

    class Meta:
        verbose_name = 'Водитель поездки'
        verbose_name_plural = 'Водители поездок'

    def __str__(self):
        return f"Водитель {self.driver.name} для поездки {self.trip.code}"


class Profit(models.Model):
    code = models.AutoField(primary_key=True)
    date = models.DateField(verbose_name='Дата вывода')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, verbose_name='Водитель')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')

    class Meta:
        verbose_name = 'Вывод прибыли'
        verbose_name_plural = 'Выводы прибыли'

    def __str__(self):
        return f"Прибыль {self.amount} для водителя {self.driver.name}"
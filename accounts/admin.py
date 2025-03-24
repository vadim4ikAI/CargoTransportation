from django.contrib import admin
from .models import City, Route, Trip, TripService, AdditionalService, Client, Driver, TripDriver, Profit, UserProfile
from django.utils.html import format_html


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('departure_city', 'arrival_city', 'distance', 'price')
    list_filter = ('departure_city', 'arrival_city')
    search_fields = ('departure_city__name', 'arrival_city__name')
    ordering = ('departure_city', 'arrival_city')


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('code', 'route', 'client', 'cargo_weight', 'start_date', 'end_date', 'rating')
    list_filter = ('start_date', 'end_date', 'route')
    search_fields = ('client__first_name', 'client__last_name', 'route__departure_city__name', 'route__arrival_city__name')
    ordering = ('start_date',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number')
    search_fields = ('first_name', 'last_name', 'phone_number')
    ordering = ('last_name', 'first_name')


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'license_issue_date', 'photo_tag')
    list_filter = ('license_issue_date',)
    search_fields = ('name',)
    ordering = ('name',)

    def photo_tag(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.photo.url)
        return "Нет фото"

    photo_tag.short_description = 'Фото'


@admin.register(Profit)
class ProfitAdmin(admin.ModelAdmin):
    list_display = ('driver', 'amount')
    list_filter = ('driver',)
    search_fields = ('driver__name',)
    ordering = ('-amount',)


# Регистрация оставшихся моделей без дополнительных настроек
admin.site.register(TripService)
admin.site.register(AdditionalService)
admin.site.register(TripDriver)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username']

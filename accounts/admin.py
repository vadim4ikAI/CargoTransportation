from django.contrib import admin
from .models import City, Route, Trip, TripService, AdditionalService, Client, Driver, TripDriver, Profit
from django.utils.html import format_html

class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'license_issue_date', 'photo_tag')

    def photo_tag(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.photo.url)
        return "Нет фото"
    photo_tag.short_description = 'Фото'

# Регистрация моделей
admin.site.register(City)
admin.site.register(Route)
admin.site.register(Trip)
admin.site.register(TripService)
admin.site.register(AdditionalService)
admin.site.register(Client)
admin.site.register(Driver, DriverAdmin)  # Используйте кастомный админ-класс
admin.site.register(TripDriver)
admin.site.register(Profit)

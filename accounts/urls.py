from django.urls import path
from .views import login_view, register, home_view, logout_view, get_cities, calculate_route, export_trips, cabinet
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('', home_view, name='home'),
    path('cabinet/', cabinet, name='cabinet'),
    path('get-cities/', get_cities, name='get_cities'),
    path('calculate-route/', calculate_route, name='calculate_route'),
    path('export-trips/', export_trips, name='export_trips'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
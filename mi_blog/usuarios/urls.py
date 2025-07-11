from . import views
from django.urls import path
from .views import (
    login_view, register_view, CustomPasswordResetView,
    register, CustomLoginView, inicio  # Asegúrate de tener esta vista
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', views.register, name='register'), # URL para el registro de usuarios
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('', inicio, name='home'),  # Ruta principal
]

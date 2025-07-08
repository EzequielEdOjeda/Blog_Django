from django.urls import path
from . import views
from .views import CustomPasswordResetView

urlpatterns = [
    path('register/', views.register, name='register'), # URL para el registro de usuarios
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
]

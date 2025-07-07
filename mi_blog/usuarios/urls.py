from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'), # URL para el registro de usuarios
]
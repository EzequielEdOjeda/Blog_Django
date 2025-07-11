from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse_lazy
from .forms import RegisterForm

# Vista personalizada de Login (acceso por URL directa)
def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')  # Redirige al home si ya está autenticado
    return render(request, 'login.html')

# Vista personalizada de Registro (acceso por URL directa)
def register_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    return render(request, 'register.html')

# Vista de envío de formulario de restablecimiento de contraseña
class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset_form.html'
    success_url = reverse_lazy('home')  # Redirige a '/' al completar

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')  # Evita mostrar el form a usuarios autenticados
        return super().dispatch(request, *args, **kwargs)

def inicio(request):
    return redirect('/') 

# Registro de nuevos usuarios
def register(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            commenters_group, _ = Group.objects.get_or_create(name='Commenters')
            user.groups.add(commenters_group)
            messages.success(request, '¡Tu cuenta ha sido creada exitosamente! Ahora puedes iniciar sesión.')
            return redirect('login')  # Redirige al login
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


# Vista de Login personalizada para redirección de administradores
class CustomLoginView(LoginView):
    def get_redirect_url(self):
        url = super().get_redirect_url()
        if self.request.user.is_authenticated and self.request.user.is_staff: # is_staff incluye superuser y personal del admin
            return '/admin/' # Redirigir a /admin/ si es staff/admin
        return url # De lo contrario, redirigir a la URL por defecto
        
        template_name = 'login.html'  # Usa tu plantilla de login
    redirect_authenticated_user = True  # Redirige si ya está autenticado

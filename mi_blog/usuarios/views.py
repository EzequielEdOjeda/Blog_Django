from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import Group # Importar Group para asignar roles
from django.contrib.auth.views import LoginView # Importar la vista de login base de Django
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView

class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset_form.html'

# Vista para el registro de nuevos usuarios
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Asignar el usuario al grupo "Commenters" por defecto
            commenters_group, created = Group.objects.get_or_create(name='Commenters')
            user.groups.add(commenters_group)
            messages.success(request, '¡Tu cuenta ha sido creada exitosamente! Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Vista de Login personalizada para redirección de administradores
class CustomLoginView(LoginView):
    def get_redirect_url(self):
        url = super().get_redirect_url()
        if self.request.user.is_authenticated and self.request.user.is_staff: # is_staff incluye superuser y personal del admin
            return '/admin/' # Redirigir a /admin/ si es staff/admin
        return url # De lo contrario, redirigir a la URL por defecto

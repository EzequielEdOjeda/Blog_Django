# mi_blog_profesional/urls.py
from django.contrib import admin
from django.urls import path, include
# from django.views.generic import TemplateView # Elimina o comenta esta línea si usas la nueva HomeView
from django.conf import settings
from django.conf.urls.static import static
from usuarios.views import CustomLoginView
from home.views import HomeView # <--- ¡ASEGÚRATE DE QUE ESTA LÍNEA ESTÉ PRESENTE!
from django.contrib.auth import views as auth_views

# Personalización del título del sitio de administración
admin.site.site_header = "Administración del Blog"
admin.site.site_title = "Panel de Administración"
admin.site.index_title = "Panel de Administración"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('usuarios.urls')),
    path('blog/', include('blog.urls')),
    # path('', TemplateView.as_view(template_name='home.html'), name='home'), # ELIMINA O COMENTA ESTA LÍNEA
    path('', HomeView.as_view(), name='home'), # AÑADE ESTA LÍNEA
    # Password reset integrado de Django (puede ir en usuario también)
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset_form.html'
    ), name='password_reset'),

    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),

    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

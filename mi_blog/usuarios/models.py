from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group # Importar Group

# Modelo de Perfil para extender el modelo User de Django
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Puedes añadir campos adicionales aquí si los necesitas, por ejemplo:
    # bio = models.TextField(blank=True, null=True)
    # profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username

    @property
    def is_editor(self):
        """
        Devuelve True si el usuario asociado a este perfil pertenece al grupo 'Editors'.
        """
        # Asegúrate de que el grupo 'Editors' exista.
        # Si el grupo no existe, esta verificación devolverá False, lo cual es seguro.
        return self.user.groups.filter(name='Editors').exists()

# Señales para crear y guardar el perfil automáticamente cuando se crea un usuario
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        # Asignar el usuario al grupo "Commenters" por defecto al registrarse
        commenters_group, created = Group.objects.get_or_create(name='Commenters')
        instance.groups.add(commenters_group)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
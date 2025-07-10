from django.db import models
from django.contrib import admin
# REMOVE THIS LINE: from .models import Post, Comment, Category # <--- THIS IS THE PROBLEM!

# IMPORTS FROM YOUR MODELS ARE NOT NEEDED HERE DUE TO @admin.register()
# However, you *do* need to import the models themselves if you haven't defined them elsewhere in this file.
# Since you're using @admin.register(Post), @admin.register(Comment), @admin.register(Category),
# the models are implicitly referenced by name. Django's admin system handles the lookup.
# For clarity, it's often good practice to explicitly import them, but the circular import issue
# happens when the import tries to run *before* the models are fully defined.

# The best way to avoid circular imports here is to simply use the decorator with the model name,
# and ensure your models are cleanly defined in blog/models.py without circular dependencies.
# If Django still complains about models not being defined, it means the import order is the issue,
# but for admin.py, it's typically fine to reference them directly by their class name after they're loaded.

# Let's explicitly import them to make sure they are known in this file's scope,
# but if the circular import problem *persists* even with this, we'll revert to not importing them
# and rely solely on the @admin.register decorator's magic.
# Given the previous context, the circular import might be deeper.
# For now, let's try the standard explicit import.

from .models import Post, Comment, Category # <--- Re-add this, but the previous error was likely due to users/models.py trying to import blog.models at the same time blog.models was trying to import auth/user which is related to users. This specific admin.py import is usually fine on its own.

# Personalización del modelo Post en el panel de administración
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status', 'category') # Campos a mostrar en la lista
    list_filter = ('status', 'created', 'publish', 'author', 'category') # Filtros laterales
    search_fields = ('title', 'content') # Campos para búsqueda
    prepopulated_fields = {'slug': ('title',)} # Rellena el slug automáticamente desde el título (en el admin)
    raw_id_fields = ('author',) # Muestra un widget de búsqueda para el autor
    date_hierarchy = 'publish' # Navegación por fechas
    ordering = ('status', 'publish') # Orden por defecto

# Personalización del modelo Comment en el panel de administración
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created', 'active') # Campos a mostrar en la lista
    list_filter = ('active', 'created', 'updated') # Filtros laterales
    search_fields = ('author__username', 'content') # Campos para búsqueda
    actions = ['approve_comments', 'disapprove_comments'] # Acciones personalizadas

    # Acción para aprobar comentarios
    @admin.action(description='Marcar comentarios seleccionados como activos')
    def approve_comments(self, request, queryset):
        queryset.update(active=True)
        self.message_user(request, f'{queryset.count()} comentarios han sido aprobados.')

    # Acción para desaprobar comentarios
    @admin.action(description='Marcar comentarios seleccionados como inactivos')
    def disapprove_comments(self, request, queryset):
        queryset.update(active=False)
        self.message_user(request, f'{queryset.count()} comentarios han sido desaprobados.')

# Personalización del modelo Category en el panel de administración
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)} # Rellena el slug automáticamente
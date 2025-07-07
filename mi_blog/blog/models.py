from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify # Importa slugify

# Manager para posts publicados
class PublishedManager(models.Manager):
    def get_queryset(self):
        # Filtra solo los posts con estado 'PUBLISHED'
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def save(self, *args, **kwargs):
        # Si no hay slug, lo genera a partir del nombre de la categoría
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Borrador'
        PUBLISHED = 'PB', 'Publicado'

    title = models.CharField(max_length=250)
    # El slug ahora es `blank=True` para que nuestro método save() lo genere
    # y `unique=True` para asegurar que no haya dos posts con el mismo slug
    slug = models.SlugField(max_length=250, blank=True, unique=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts'
    )
    content = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.DRAFT
    )
    featured_image = models.ImageField(
        upload_to='blog_images/%Y/%m/%d/',
        blank=True,
        null=True
    )

    objects = models.Manager() # Manager por defecto
    published = PublishedManager() # Nuestro manager personalizado

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ['-publish'] # Ordena los posts por fecha de publicación descendente
        indexes = [
            models.Index(fields=['-publish']), # Crea un índice en el campo 'publish' para mejorar el rendimiento de las consultas
        ]

    def __str__(self):
        return self.title

    # Sobrescribimos el método save para generar el slug automáticamente
    def save(self, *args, **kwargs):
        if not self.slug: # Si el slug no ha sido proporcionado (ej. al crear un post nuevo)
            base_slug = slugify(self.title) # Genera un slug a partir del título
            unique_slug = base_slug
            num = 1
            # Bucle para asegurar que el slug sea único
            # Si ya existe un post con el mismo slug (excluyendo el post actual si es una actualización)
            while Post.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{num}" # Añade un sufijo numérico para hacerlo único
                num += 1
            self.slug = unique_slug # Asigna el slug único al post
        super().save(*args, **kwargs) # Llama al método save original del modelo para guardar el objeto

    def get_absolute_url(self):
        # Genera la URL canónica para un post
        # Usamos los atributos de fecha del post y el slug que ya está garantizado
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug])

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comments_made'
    )
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ['created'] # Ordena los comentarios por fecha de creación ascendente
        indexes = [
            models.Index(fields=['created']), # Crea un índice en el campo 'created'
        ]

    def __str__(self):
        # Representación de cadena para el comentario
        author_name = self.author.username if self.author else "Anónimo"
        return f'Comentario de {author_name} en {self.post.title}'
from . import models
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Comment, Category
from .forms import CommentForm, PostForm, PostFilterForm # Asegúrate de importar PostFilterForm
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count # Asegúrate de añadir 'Count' aquí
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Comment, Post # Asumiendo que tus modelos se llaman Comment y Post

@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    # Asegúrate de que solo el autor del comentario o un superusuario/editor pueda eliminar
    if request.user == comment.author or request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_editor and request.user == comment.post.author):
        post_slug = comment.post.slug
        publish_date = comment.post.publish
        comment.delete()
        # Redirigir de nuevo a la página de detalles del post
        return redirect('blog:post_detail', year=publish_date.year, month=publish_date.month, day=publish_date.day, slug=post_slug)
    else:
        # Manejar el intento de eliminación no autorizado (por ejemplo, redirigir con un mensaje de error)
        return redirect('blog:post_detail', year=comment.post.publish.year, month=comment.post.publish.month, day=comment.post.publish.day, slug=comment.post.slug)

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 6
    template_name = 'blog/post_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = PostFilterForm(self.request.GET) # Asegúrate de que self.form siempre se define aquí

        if self.form.is_valid():
            category_obj = self.form.cleaned_data.get('category') # Renombrado para claridad
            start_date = self.form.cleaned_data.get('start_date')
            end_date = self.form.cleaned_data.get('end_date')
            min_comments = self.form.cleaned_data.get('min_comments')
            query = self.form.cleaned_data.get('query')

            if category_obj: # Usa el objeto Category para filtrar
                queryset = queryset.filter(category=category_obj)
            if start_date:
                queryset = queryset.filter(publish__gte=start_date)
            if end_date:
                queryset = queryset.filter(publish__lte=end_date)
            if min_comments is not None:
                from django.db.models import Count
                queryset = queryset.annotate(comment_count=Count('comments', filter=Q(comments__active=True))).filter(comment_count__gte=min_comments)
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query) |
                    Q(author__username__icontains=query)
                )

        return queryset.order_by('-publish')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form # El formulario ya está inicializado en get_queryset

        # Pasa el objeto Category seleccionado, o None si no hay
        selected_category_obj = self.form.cleaned_data.get('category') if self.form.is_valid() else None
        context['selected_category'] = selected_category_obj.pk if selected_category_obj else '' # Pasa el PK o un string vacío

        # Estos están bien, ya que vienen como strings del GET
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        context['min_comments'] = self.request.GET.get('min_comments', '')
        context['query'] = self.request.GET.get('query', '')
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        # Asegurarse de que solo se puedan ver posts publicados, a menos que sea un editor/admin
        if self.request.user.is_authenticated and (self.request.user.is_superuser or self.request.user.profile.is_editor):
            return Post.objects.all()
        return Post.published.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['comments'] = post.comments.filter(active=True)
        context['comment_form'] = CommentForm()
        # Añadir el formulario de filtro/búsqueda para la barra lateral
        context['filter_form'] = PostFilterForm(self.request.GET or None)
        return context

# Mixin para verificar si el usuario es superusuario o editor
class EditorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or (hasattr(self.request.user, 'profile') and self.request.user.profile.is_editor)

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permiso para realizar esta acción.")
        return redirect('home') # O a una página de error de acceso denegado

class PostCreateView(EditorRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.publish = timezone.now() # Asegura que la fecha de publicación se establece
        response = super().form_valid(form)
        messages.success(self.request, "El post ha sido publicado con éxito.")
        return response

    def get_success_url(self):
        # Redirige al post recién creado
        return self.object.get_absolute_url()


class PostUpdateView(EditorRequiredMixin, UpdateView): # Nueva vista para editar
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html' # Reutilizamos el mismo formulario template

    def get_queryset(self):
        # Solo el superusuario o el autor del post (si es editor) puede editar
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(author=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "El post ha sido actualizado con éxito.")
        return response

    def get_success_url(self):
        return self.object.get_absolute_url() # Redirige al post editado


class PostDeleteView(EditorRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')

    def get_queryset(self):
        # Solo el superusuario o el autor del post (si es editor) puede eliminar
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(author=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "El post ha sido eliminado con éxito.")
        return response


def post_comment(request, year, month, day, slug):
    post = get_object_or_404(Post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day,
                             slug=slug)
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user if request.user.is_authenticated else None
            new_comment.save()
            messages.success(request, "Tu comentario ha sido añadido con éxito.")
            return redirect(post.get_absolute_url() + '#comments')
        else:
            messages.error(request, "Error al enviar el comentario. Por favor, revisa los campos.")
            # Si el formulario no es válido, renderiza la página con los errores
            comments = post.comments.filter(active=True)
            return render(request, 'blog/post_detail.html', {
                'post': post,
                'comments': comments,
                'comment_form': comment_form,
                'filter_form': PostFilterForm(request.GET or None) # Asegurarse de pasar el form de filtro
            })
    return redirect(post.get_absolute_url())

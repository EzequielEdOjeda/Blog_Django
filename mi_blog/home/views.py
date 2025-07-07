# home/views.py
from django.views.generic import ListView
from blog.models import Post

class HomeView(ListView):
    template_name = 'home.html'
    context_object_name = 'latest_posts'
    queryset = Post.published.order_by('-publish')[:6] # Obtener los 6 posts más recientes
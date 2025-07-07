from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('new/', views.PostCreateView.as_view(), name='post_create'),
    # Nueva URL para editar posts
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/comment/', views.post_comment, name='post_comment'),
]
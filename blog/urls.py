from django.urls import path
from .views import list_or_create_posts, post_detail

urlpatterns = [
    path('posts/', list_or_create_posts, name='list-or-create-posts'),
    path('posts/<int:id>/', post_detail, name='post-detail'),
]
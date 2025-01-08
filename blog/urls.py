from django.urls import path, include
from . import views

urlpatterns = [
    path("posts/", views.PostListCreateView.as_view(), name="post-list-create"),
    path("posts/<int:pk>/", views.PostDetailView.as_view(), name="post-detail"),
    path("posts/category/<str:category_name>/", views.PostsByCategory.as_view(), name="posts-by-category"),
    path("posts/author/<str:username>/", views.PostsByAuthorView.as_view(), name="posts-by-author"),
    path("posts/<int:post_id>/comments/", views.CommentListCreateView.as_view(), name="comment-list-create"),

    # Endpoints for most liked and highest rated posts
    path("posts/most-liked/", views.MostLikedPostsView.as_view(), name="most-liked-posts"),
    path("posts/highest-rated/", views.HighestRatedPostsView.as_view(), name="highest-rated-posts"),

    # Endpoints for sharing post
    path("posts/<int:post_id>/share/", views.PostShareView.as_view(), name="post-share"),
]
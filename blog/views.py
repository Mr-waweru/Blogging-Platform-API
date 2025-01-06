from rest_framework import generics, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .models import *
from .serializers import *
from .permissions import IsOwnerOrReadOnly

class PostListCreateView(generics.ListCreateAPIView):
    """View to list all posts or create a new post"""

    queryset = Post.objects.all().order_by("-published_date")
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "tags", "published_date"]   # Allow filtering by these fields
    search_fields = ["title", "content", "tags__name", "author__username"]  # Allow searching by these fields
    ordering_fields = ["published_date", "title"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostCreateUpdateSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        """Set the author of the post to the currently authenticated user"""
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        """Handle POST request"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View to retrieve, update, or delete a single post"""
    
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def update(self, request, *args, **kwargs):
        """Handle PUT request"""
        partial = kwargs.pop("partial", False)
        instance = self.get_objects()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """Handle DELETE request"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostsByCategory(generics.ListAPIView):
    """View to list all posts in a specific category"""
    
    serializer_class = PostSerializer

    def get_queryset(self):
        """Filter posts by the category specified in the URL"""
        category_name = self.kwargs.get("category_name")
        return Post.objects.filter(category__name__iexact=category_name)
    
    def list(self, request, *args, **kwargs):
        """Handle GET request"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostsByAuthorView(generics.ListAPIView):
    """View to list all posts by a specific author"""
    
    serializer_class = PostSerializer

    def get_queryset(self):
        """Filter posts by the author specified in the URL"""
        author_username = self.kwargs.get("username")
        return Post.objects.filter(author__username=author_username)
    
    def list(self, request, *args, **kwargs):
        """Handle GET request"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentListCreateView(generics.ListCreateAPIView):
    """View to list or create comments for a specific post"""
    
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Filter comments by the post specified in the URL"""
        post_id = self.kwargs.get("post_id")
        return Comment.objects.filter(post_id=post_id)
    
    def perform_create(self, serializer):
        """Set the author of the comment to the currently authenticated user"""
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        """Handle POST request"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

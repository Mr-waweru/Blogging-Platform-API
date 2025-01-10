from rest_framework import generics, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .models import *
from .serializers import *
from .permissions import IsOwnerOrReadOnly
from django.db.models import Count, Avg
from django.core.mail import send_mail

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
    """View to retrieve, update, or delete a single post with actions for liking and rating"""
    
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def update(self, request, *args, **kwargs):
        """Handle PUT request"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """Handle DELETE request"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get(self, request, *args, **kwargs):
        """Retrieve a single post along with total likes and average rating"""
        post = self.get_object()
        post_data = {
            "post": PostSerializer(post).data,
            "total_likes": post.likes.count(),
            "average_rating": post.ratings.aggregate(Avg("rating"))["rating__avg"] or 0  # Calculate average rating
        }
        return Response(post_data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        """Handle actions: like or rate a post"""
        post = self.get_object()
        action = request.data.get("action")

        if action == "like":
            # Check if the user has already liked the post
            existing_like = Like.objects.filter(post=post, user = request.user)
            if existing_like.exists():
                # If the user has already liked the post, unlike it
                existing_like.delete()
                return Response({"detail": "Post unliked successfully!"}, status=status.HTTP_200_OK)
            else:
                # Otherwise, add a like
                Like.objects.create(post=post, user = request.user)
                return Response({"detail": "Post liked successfully!"}, status=status.HTTP_200_OK)

        elif action == "rate":
            # Validate and update or create a rating for the post
            rating_value = request.data.get("rating")
            if not rating_value or not (1 <= int(rating_value) <= 5):
                return Response({"detail": "Invalid rating value. Must be between 1 and 5."}, status=status.HTTP_400_BAD_REQUEST)
            rating, created = Rating.objects.update_or_create(
                post=post, user=request.user,
                defaults={"rating": rating_value}   # Update or set the rating value
            )
            return Response({"detail": "Post rated successfully!"}, status=status.HTTP_200_OK)
        
        return Response({"detail": "Invalid action. Use 'like' or 'rate'."}, status=status.HTTP_400_BAD_REQUEST)


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
        """Associate the comment with the post and the current user"""
        post_id = self.kwargs.get("post_id")    # Get the post_id from the URL
        post = Post.objects.get(id=post_id) # Retrieve the corresponding Post object
        serializer.save(author=self.request.user, post=post)    # Save the comment with post and author

    def create(self, request, *args, **kwargs):
        """Handle POST request"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MostLikedPostsView(generics.ListAPIView):
    """View to list most liked posts"""

    serializer_class = PostSerializer

    def get_queryset(self):
        """Annotate posts with like counts and order by the highest like count"""
        most_liked = Post.objects.annotate(like_count=Count("likes")).order_by("-like_count")
        return most_liked
    

class HighestRatedPostsView(generics.ListAPIView):
    """View to list highest rated posts"""

    serializer_class = PostSerializer

    def get_queryset(self):
        """Annotate posts with average ratings and order by the highest average rating"""
        highest_rated_post = Post.objects.annotate(average_rating=Avg("ratings__rating")).order_by("-average_rating")
        return highest_rated_post
    

class PostShareView(generics.GenericAPIView):
    """View to share a post via email."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post_id = self.kwargs["post_id"]
        post = Post.objects.get(id=post_id)
        recipient_email = request.data.get("email") # Expecting email from the request body

        if not recipient_email:
            return Response({"detail": "Email is required to share the post."}, status=status.HTTP_400_BAD_REQUEST)

        subject = f"Check out this post: {post.title}"
        message = f"Hello,\n\nI wanted to share this interesting post with you:\n\nTitle: {post.title}\n\n{post.content}\n\nBest regards,"
        from_email = settings.DEFAULT_FROM_EMAIL

        send_mail(subject, message, from_email, [recipient_email])

        return Response({"detail": "Post shared successfully!"}, status=status.HTTP_200_OK)

from rest_framework import serializers
from .models import Post, Comment, Tag, Category, Like, Rating
from django.contrib.auth import get_user_model

User = get_user_model()

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()   # Represent the author as a string

    class Meta:
        model = Comment
        fields = ["id", "author", "content", "created_at", "updated_at"]


class PostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    author = serializers.StringRelatedField()
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id", "title", "content", "author", "category", "tags",
            "published_date", "updated", "comments"
        ]


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating posts"""

    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())  # Add tags by ID

    class Meta:
        model = Post
        fields = ["title", "content", "category", "tags"]


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Display user's username
    post_title = serializers.CharField(source="post.title", read_only=True)  # Include post title in the response

    class Meta:
        model = Like
        fields = "__all__"
        read_only_fields = ["user"]

    def create(self, validated_data):
        """Overriding the create method to associate the authenticated user with the like"""
        validated_data["user"] = self.context["request"].user  # Set the user as the logged-in user
        return super().create(validated_data)


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    post_title = serializers.CharField(source="post.title", read_only=True)

    class Meta:
        model = Rating
        fields = "__all__"

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
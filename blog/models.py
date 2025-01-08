from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.utils.text import slugify

class CustomUserManager(BaseUserManager):
    """How to create a regular user"""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email) # Ensures the email is in a standard format
        user = self.model(email=email, **extra_fields)  # Creates a user instance using the custom user model
        user.set_password(password) # Hashes the password for security
        user.save(using=self._db)   # Saves the user to the database
        return user
    
    """Defines how to create a superuser"""
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        for field in ["is_staff", "is_superuser", "is_active"]:
            if not extra_fields.get(field):
                raise ValueError(f"Superuser must have {field} set to True")
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=60, unique=True)
    username = models.CharField(max_length=15, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def __str__(self):
        return (self.username).lower()


class Category(models.Model):
    """Model representing a product category"""
    name = models.CharField(max_length=35, unique=True)

    def save(self, *args, **kwargs):
        self.name = self.name.lower()   # Normalize the name to lowercase before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    """
    This constraint prevents the database from accepting duplicates 
    based on case-insensitive comparisons.
    """
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"], name="unique_category_name", condition=models.Q(name__iexact=models.F("name"))
            )
        ]
        verbose_name_plural = "Categories"  # Correct pluralization


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:   # Generate a slug if it doesn't already exist
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name="posts")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="posts")
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
    published_date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.author}"
    
    class Meta:
        ordering = ["-published_date"]  # Default ordering by published date, descending
    

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")  # Links to a specific post
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Link to the user who wrote the comment
    content = models.TextField()  # The comment's text
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the creation time
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set the last update time

    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"
    

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ("post", "user")  # Ensures a user can like a post only once

    def __str__(self):
       return f"liked by {self.user.username}"
    

class Rating(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings")
    rating = models.PositiveIntegerField(choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")])

    class Meta:
        unique_together = ("post", "user")  # Ensures one rating per user per post

    def __str__(self):
        return f"Rating of {self.rating} by {self.user.username} for {self.post.title}"
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow owners to edit or delete their posts"""

    def has_object_permission(self, request, view, obj):
        # Allow read-only methods for any user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow write methods only if the user is the author of the post
        return obj.author == request.user

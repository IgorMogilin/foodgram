from rest_framework import permissions


class IsRecipeAuthor(permissions.BasePermission):
    """Разрешение на действия только для автора рецепта."""
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

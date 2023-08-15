from rest_framework import permissions


from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsAdminOrReadOnly(permissions.BasePermission):
    """Админу: полный доступ, остальным: только чтение."""
    def has_permission(self, request, view):

        return request.method in SAFE_METHODS or request.user.is_staff


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Автору объекта: полный доступ,
    анониму: безопасные методы,
    аутентифицированному: доступ, но без доступа к объекту.
    """
    def has_permission(self, request, view):

        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):

        return obj.author == request.user
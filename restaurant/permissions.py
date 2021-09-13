from rest_framework.permissions import BasePermission


class IsAdminOrNone(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'Admin'
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return request.user.role == 'Admin'
        return False

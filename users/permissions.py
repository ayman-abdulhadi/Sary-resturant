from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.role == 'Admin'
        else:
            return True

    def has_object_permission(self, request, view, obj):
        return request.user.role == 'Admin'

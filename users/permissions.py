from rest_framework.permissions import BasePermission


class OnlyUnathorized(BasePermission):
    """
    Allows access only to authorized users.
    """

    def has_permission(self, request, view):
        return request.user.is_anonymous


class OnlyAdminPermission(BasePermission):
    """
    Allow access only to admins
    """

    def has_permission(self, request, view):
        return request.user.is_superuser

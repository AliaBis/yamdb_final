from rest_framework import permissions

from api_yamdb.settings import ADMIN, MODERATOR


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return request.user.role == ADMIN or request.user.is_superuser


class MeOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        else:
            return True


class GetAllPostDeleteAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.user.is_anonymous:
            return False
        return request.user.role == ADMIN or request.user.is_superuser


class ReviewCommentsPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_anonymous:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.role == ADMIN:
            return True
        if request.user.role == MODERATOR:
            return True
        if request.user.is_superuser:
            return True
        return obj.author == request.user

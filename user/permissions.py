from rest_framework import permissions
from .models import *

class EditUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "PUT" and request.user.is_edit:
            return True
        return False

class DeleteUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "DELETE" and request.user.is_delete:
            return True
        return False

class CreateUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST" and request.user.is_post:
            return True
        return False


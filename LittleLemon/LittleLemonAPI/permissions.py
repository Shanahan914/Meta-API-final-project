from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.browser == request.user

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name="manager").exists():
            return True

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name="customer").exists():
            return True

class IsDriver(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name="driver").exists():
            return True
        

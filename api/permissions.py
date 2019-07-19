from rest_framework.permissions import BasePermission


class IsObjectOwner(BasePermission):
    my_safe_methods = ['GET', 'PUT', 'PATCH', 'DELETE']

    def has_permission(self, request, view):
        if request.method in self.my_safe_methods:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True
        else:
            return obj == request.user or request.user.is_superuser


class IsObjectOwnerWithCreate(BasePermission):
    my_safe_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

    def has_permission(self, request, view):
        if request.method in self.my_safe_methods:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True
        else:
            return obj.author == request.user or request.user.is_superuser
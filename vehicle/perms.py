from rest_framework.permissions import BasePermission



class IsVehicleOwnerOrIsAdminOrStaff(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True

        elif obj.lister == request.user:
            return True

        return False

class IsVehicleOwner(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if obj.lister == request.user:
            return True

        return False

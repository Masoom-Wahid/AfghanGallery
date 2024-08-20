from rest_framework.permissions import BasePermission



class PaymentOwnerOrAdminOrStaff(BasePermission):
    def has_permission(self, request, view):
        if not request.user:
            return False
        if not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        else:
            if obj.user == request.user:
                return True
            else:
                return False

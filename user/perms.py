from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user == None:
            return False
        return bool(request.user.is_superuser)

class IsStaff(BasePermission):
    def has_permission(self, request, view):
        if request.user == None: return False
        return bool(request.user.is_staff)

class IsAdminOrStaff(BasePermission):
    def has_permission(self, request, view):
        if request.user == None : return False
        return bool(request.user.is_staff or request.user.is_superuser)

class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_verified)


class IsOwnerOrAdminOrStaff(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        if request.user.is_staff or request.user.is_superuser:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """
        a admin can delete whenever and whomever he wants
        staff can only delete other users and themselves
        users can only delete themselves
        """
        if request.user.is_superuser: return True
        if request.user.is_staff:
            if obj.is_superuser:
                return False
            if obj.is_staff:
                return obj == request.user
            else:
                return True
        # he isnt staff nor superuser
        return obj == request.user


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        obj = view.get_object()
        return bool(request.user == obj.user)

# class IsOwnerOrAdmin(BasePermission):
#     def has_permission(self, request, view):
#         instance = view.get_object()
#         return bool(request.user.is_staff or instance == request.user)


# class IsSuperUser(BasePermission):
#     def has_permission(self, request, view):
#         instance = view.get_object()
#         if instance.is_superuser:
#             return False
#         return bool(request.user.is_staff)

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


class IsOwnerOrAdminOrStaff(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        if request.user.is_staff or request.user.is_superuser:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        print(f"req is {request.user}")
        print(f"obj is {obj}")
        if request.user.is_staff or request.user.is_superuser:
            return True
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

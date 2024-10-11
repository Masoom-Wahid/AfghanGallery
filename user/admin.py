from django.contrib import admin
from .models import CustomUser,Room,Message
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password','phone_no','tazkira')}),
        (_('Personal info'), {'fields': ('name','last_name')}),
        (_('Permissions'), {'fields': ('is_verified', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'name','last_name', 'is_staff')
    search_fields = ('email', 'name','last_name')
    ordering = ('email',)
    list_filter = ("email",'phone_no')

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Room)
admin.site.register(Message)

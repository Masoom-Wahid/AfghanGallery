from django.contrib import admin

from .models import UserFavs,UserHistory,UserNotifications

admin.site.register(UserFavs)
admin.site.register(UserHistory)
admin.site.register(UserNotifications)

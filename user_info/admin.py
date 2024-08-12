from django.contrib import admin

from .models import UserFavs,UserHistory

admin.site.register(UserFavs)
admin.site.register(UserHistory)
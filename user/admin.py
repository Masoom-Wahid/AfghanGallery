from django.contrib import admin
from .models import CustomUser,Room,Message

admin.site.register(CustomUser)
admin.site.register(Room)
admin.site.register(Message)
from .models import UserFavs, UserNotifications
from rest_framework import serializers

class UserNotifsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotifications
        fields = "__all__"


class UserFavsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFavs
        fields = "__all__"

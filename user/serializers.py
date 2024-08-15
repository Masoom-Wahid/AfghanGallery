from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.utils import IntegrityError as DjangoIntegrityError


class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    name = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    last_name = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    phone_no = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    is_verified = serializers.CharField(read_only=True)
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name', 'last_name', 'phone_no',"is_verified"]


class CustomUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["email", "password", "name", "last_name", "phone_no"]

class AuthSerializerClass(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password']

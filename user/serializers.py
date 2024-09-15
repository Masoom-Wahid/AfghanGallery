from rest_framework import serializers
from django.contrib.auth import get_user_model
from utils.serializers import generate_keyword_args
from user.models import Room

class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    name = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    last_name = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    phone_no = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    is_verified = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    class Meta:
        model = get_user_model()
        fields = [
            'email',
            'name',
            'last_name',
            'phone_no',
            "is_verified",
            "is_staff",
            "is_superuser"
        ]

        extra_kwargs = generate_keyword_args(
            fields=fields,
            unique_names=["email","phone_no"],
            model=model
        )

    def get_fields(self):
        """
        since i want 'is_verified' to be editiable only by staff and superuser here edit those
        and 'is_staff' and 'is_superuser' to be editable by superuser only
        """
        fields = super().get_fields()
        request = self.context.get('request')

        if request:
            
            if request.user.is_staff or request.user.is_superuser:
                fields['is_verified'].read_only = False
            
            if request.user.is_superuser:
                fields['is_staff'].read_only = False
                fields['is_superuser'].read_only = False

        return fields

class CustomUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        
        fields = ["email", "password", "name", "last_name", "phone_no"]
        
        
        extra_kwargs = generate_keyword_args(
            fields=fields,
            unique_names=["email","phone_no"],
            model=model
        ) 



class AuthSerializerClass(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password']




class RoomSerializer(serializers.ModelSerializer):
    user1_email = serializers.SerializerMethodField()
    user2_email = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = '__all__'

    def get_user1_email(self,obj):
        return obj.user1.email

    def get_user2_email(self,obj):
        return obj.user2.email

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import BaseUserManager,PermissionsMixin
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser,PermissionsMixin):

    email = models.EmailField(blank=False, null=False, unique=True)
    username = models.CharField(blank=True, null=True, unique=True, max_length=50)
    is_verified = models.BooleanField(default=False)
    phone_regex = r"^07[02346789]\d{7}|02[0]\d{7}"
    phone_validator = RegexValidator(
        regex=phone_regex, message="Enter a valid phone number."
    )
    phone_no = models.CharField(
        max_length=55, validators=[phone_validator], blank=True,null=True
    )
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False) 


    class Meta:
        swappable = "AUTH_USER_MODEL"
        verbose_name = "user"
        verbose_name_plural = "users"

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    def __str__(self) -> str:
        return self.email






class Room(models.Model):
    user1 = models.ForeignKey(get_user_model(),on_delete=models.SET_NULL,null=True,blank=False,related_name="first_user")
    user2 = models.ForeignKey(get_user_model(),on_delete=models.SET_NULL,null=True,blank=False,related_name="second_user")


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user1.email} => {self.user2.email}"


class Message(models.Model):
    sender = models.ForeignKey(get_user_model(),on_delete=models.SET_NULL,null=True,blank=False,related_name="sender")
    receiver = models.ForeignKey(get_user_model(),on_delete=models.SET_NULL,null=True,blank=False,related_name="receiver")
    room_id = models.ForeignKey(Room,on_delete=models.CASCADE)
    msg = models.TextField(null=False,blank=False,) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

        
    def __str__(self) -> str:
        return self.msg
    

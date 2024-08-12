from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager,PermissionsMixin
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password



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
    # TODO: add payment_plan a Ref to PaymentPlan Table


    class Meta:
        swappable = "AUTH_USER_MODEL"
        verbose_name = "user"
        verbose_name_plural = "users"

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    def __str__(self) -> str:
        return self.email

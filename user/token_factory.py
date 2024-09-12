from datetime import datetime,timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
import jwt
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Custom claims
        token["email"] = user.email
        token["is_admin"] = user.is_superuser
        token["user_id"] = user.pk
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

def create_token(user):
    data = {
        "user_id" : user.pk,
        "is_admin" : user.is_superuser,
        "email" : user.email,
        "exp" : datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRATION_TIME)
    }

    return jwt.encode(data,settings.SECRET_KEY,algorithm="HS256")


def decode_token(token):
    try:
        data = jwt.decode(token,settings.SECRET_KEY,algorithms="HS256")
        user_id = data.get("user_id",None)
        if not user_id:
            return None
        return get_user_model().objects.get(id=user_id)
    except(
        jwt.ExpiredSignatureError,
        jwt.DecodeError,
        jwt.InvalidTokenError,
        get_user_model().DoesNotExist,
    ):
        return None

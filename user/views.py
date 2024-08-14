from rest_framework.decorators import action, parser_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
from .token_factory import create_token
from .serializers import (
    CustomUserSerializer,
    CustomUserCreateSerializer,
    AuthSerializerClass
)
from django.shortcuts import get_object_or_404
from .perms import IsOwnerOrAdminOrStaff
from rest_framework.mixins import CreateModelMixin,UpdateModelMixin,DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.parsers import FormParser,MultiPartParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class UserViewSet(CreateModelMixin,UpdateModelMixin,DestroyModelMixin,GenericViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = CustomUserSerializer


    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        elif self.action in  ["update","destroy","upload_tazkira"]:
            return [IsAuthenticated(),IsOwnerOrAdminOrStaff()]
        return super().get_permissions()


    def create(self,request):
        serializer = CustomUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        instance.set_password(serializer.data["password"])
        instance.save()
        token = create_token(instance)
        return Response({"token": token}, status=status.HTTP_201_CREATED)


    @swagger_auto_schema(
        operation_description="Upload a Tazkira document for a user.",
        manual_parameters=[
            openapi.Parameter(
                'tazkira',
                openapi.IN_FORM,
                description="The Tazkira file to upload.",
                type=openapi.TYPE_FILE,
                required=True,
            ),
        ],
        responses={
            204: 'No Content - Tazkira uploaded successfully.',
            400: openapi.Response('Bad Request - Missing tazkira file.'),
        },
        tags=['User Tazkira Upload'],
    )
    @action(
        detail=False,
        methods=["POST"],
        parser_classes=[MultiPartParser,FormParser],
        url_path='(?P<pk>\d+)/upload',
        url_name="Upload Tazkira Url",
        filter_backends=[],
        serializer_class=None,
    )
    def upload_tazkira(self,request,pk=None):
        tazkira = request.FILES.get("tazkira")
        if not tazkira:
            return Response(
                {"detail" : "'id' and 'tazkira' required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = self.get_object()
        user.tazkira = tazkira
        user.save()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


    def update(self, request, pk=None):
        user = self.get_object()
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self,request,pk=None):
        user = self.get_object()
        user = get_object_or_404(get_user_model(),pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)







class JwtToken(APIView):
    def post(self,request):
        email = request.data.get("email",None)
        password = request.data.get("password",None)
        if not email or not password:
            return Response(
                {"detail" : "'email' and 'password' required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(email=email,password=password)
        if user:
            token = create_token(user)
            return Response(
                {
                    "token" : token,
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail" : "Invalid User"},
                status=status.HTTP_400_BAD_REQUEST
            )

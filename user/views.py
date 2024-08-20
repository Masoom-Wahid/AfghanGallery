from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView, status
from rest_framework.permissions import AllowAny

from user_info.models import UserFavs, UserNotifications
from user_info.serializers import UserFavsSerializer, UserNotifsSerializer
from .perms import IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
from payment.serializers import PaymentPlanSerializer 
from .token_factory import create_token
from .serializers import (
    CustomUserSerializer,
    CustomUserCreateSerializer,
    RoomSerializer
)
from django.shortcuts import get_object_or_404
from .perms import IsOwnerOrAdminOrStaff,IsAdmin
from rest_framework.mixins import CreateModelMixin,UpdateModelMixin,DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.parsers import FormParser,MultiPartParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from payment.models import PaymentPlan 
from .models import Room


class UserViewSet(CreateModelMixin,UpdateModelMixin,DestroyModelMixin,GenericViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = CustomUserSerializer


    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        elif self.action in ["chats","notifs","favs"]:
            return [IsAuthenticated()]
        elif self.action in  [
            "partial_update",
            "destroy",
            "upload_tazkira",
            "payment_history"
        ]:
            return [IsOwnerOrAdminOrStaff()]
        elif self.action == "staff":
            return [IsAdmin()]
        return super().get_permissions()


    def create(self,request):
        serializer = CustomUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        instance.set_password(serializer.data["password"])
        instance.save()
        token = create_token(instance)
        return Response({"token": token}, status=status.HTTP_201_CREATED)


    """
    @swagger_auto_schema(
            methods=["get"],
            operation_id="payment_history_list",
            summary="Retrieve a list user's payment history",
            description="Retrieve a list user's payment history.",
            responses={
                200: openapi.Response(
                    description='A list of staff users',
                    schema=PaymentPlanSerializer
                ),
                400: openapi.Response(
                    description='Bad request',
                    schema=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                        }
                    )
                ),
                404: openapi.Response(
                    description='Invalid User',
                    schema=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                        }
                    )
                ),
            },
            tags=['Payment History']
        )
    """
    @action(
        detail=False,
        methods=["GET"],
        url_path="payment_history",
        url_name="Get user's payment history",
        filter_backends=[],
        serializer_class=None,
    )
    def payment_history(self,request):
        instance= self.get_object()

        payments = PaymentPlan.objects.filter(
            user = instance
        )

        serializer = PaymentPlanSerializer(
            payments,
            many=True
        )

        return Response(
            serializer.data
        )





    @swagger_auto_schema(
            methods=["get"],
            operation_id="staff_list",
            summary="Retrieve a list of staff users",
            description="Retrieve a list of staff users who have is_staff=True but are not is_superuser.",
            responses={
                200: openapi.Response(
                    description='A list of staff users',
                    schema=CustomUserSerializer
                ),
                400: openapi.Response(
                    description='Bad request',
                    schema=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                        }
                    )
                )
            },
            tags=['Staff Management']
        )
    @swagger_auto_schema(
            methods=['post'],
            operation_id="staff_create",
            summary="Create a new staff user",
            description="Create a new user with staff status (is_staff=True).",
            request_body=CustomUserSerializer,
            responses={
                201: openapi.Response(
                    description='Successfully created staff user',
                    schema=CustomUserSerializer
                ),
                400: openapi.Response(
                    description='Bad request',
                    schema=CustomUserSerializer
                ),
            },
            tags=['Staff Management']
        )
    @action(
        detail=False,
        methods=["POST","GET"],
    )
    def staff(self,request):
        if request.method == "GET":
            instance = get_user_model().objects.filter(is_staff=True, is_superuser=False)
            paginator = self.paginator
            page = paginator.paginate_queryset(instance, request)
            if page is not None:
                serializer = CustomUserSerializer(
                    page,
                    many=True,
                    context={"request":request}
                )
                return paginator.get_paginated_response(serializer.data)

            serializer = CustomUserSerializer(
                instance,
                many=True,
                context={"request":request}
            )
            return Response(serializer.data)

        elif request.method == "POST":
            serializer = CustomUserCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            instance.is_staff= True
            instance.is_verified=True
            instance.set_password(serializer.data["password"])
            instance.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )






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


    def partial_update(self, request, pk=None):
        user = self.get_object()
        serializer = CustomUserSerializer(
            user,
            data=request.data,
            partial=True,
            context={"request":request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self,request,pk=None):
        user = self.get_object()
        user = get_object_or_404(get_user_model(),pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
            detail=False,
            methods=["GET"]
    )
    def chats(self,request):
        instance = Room.objects.filter(
            Q(user1=request.user.id) | Q(user2=request.user.id)
        )
        serializer = RoomSerializer(
                instance,
                many=True
        )

        return Response(
                serializer.data
        )
        

    @action(
            detail=False,
            methods=["GET"]
    )
    def notifs(self,request):
        instance = UserNotifications.objects.filter(
                user=request.user
        )

        serializer = UserNotifsSerializer(
                instance
        )

        return Response(serializer.data)

    @action(detail=False,methods=["GET"])
    def favs(self,request):
        instance = UserFavs.objects.filter(
                user=request.user
        )
        serializer = UserFavsSerializer(instance)
        return Response(
                serializer.data
        )


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

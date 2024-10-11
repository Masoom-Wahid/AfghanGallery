from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView, status
from rest_framework.permissions import AllowAny

from realestate.models import RealEstate
from user.paginations import HistoryPagination, StandardPagination
from user_info.models import UserFavs, UserHistory, UserNotifications
from user_info.serializers import UserFavsSerializer, UserHistorySerializer, UserNotifsSerializer
from vehicle.models import Vehicle
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
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin,UpdateModelMixin,DestroyModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.parsers import FormParser,MultiPartParser
from drf_yasg.utils import serializers, swagger_auto_schema
from drf_yasg import openapi
from payment.models import PaymentPlan
from .models import CustomUser, Room
from django.utils import timezone
from django.db.models import F,ExpressionWrapper,DurationField,DateTimeField
from vehicle.serializers import VitrineVehicleSerializer
from realestate.serializers import VitrineRealEstateSerializer


class UserViewSet(
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
    GenericViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = CustomUserSerializer


    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        elif self.action in [
                "chats",
                "notifs",
                "favs",
                "history",
                "reset_password"
                ]:
            return [IsAuthenticated()]
        elif self.action in  [
            "partial_update",
            "destroy",
            "upload_tazkira",
            "payment_history",
            "reset_password",
            "admin_change_password"
        ]:
            return [IsOwnerOrAdminOrStaff()]
        elif self.action in ["staff","verify"]:
            return [IsAdmin()]
        return super().get_permissions()


    def create(self,request):
        serializer = CustomUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        instance.set_password(serializer.data["password"])#type:ignore
        instance.save() #type:ignore
        token = create_token(instance)
        return Response({"token": token}, status=status.HTTP_201_CREATED)




    @action(
        detail=False,
        url_path='(?P<pk>\d+)/verify',
        methods=["POST"],
        url_name="verify_user"
    )
    def verify(self,request,pk=None):
        user = self.get_object()
        user.is_verified=True
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


    @action(
        detail=False,
        methods=["POST"],
        url_path='(?P<pk>\d+)/change_password',
        url_name="admin change user password",
        filter_backends=[],
        serializer_class=None,
    )
    def admin_change_password(self,request,pk=None):
        instance : CustomUser = self.get_object()
        if not request.data.get("password"):
            return Response(
                {
                    "detail" : "password required'"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.set_password(
            request.data.get("password")
        )
        instance.save()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


    def get_active_instances(self,*,user : CustomUser,filter : int):
        """
            returns the vehicles and realestates of a person
            params :
                user -> the user
                filter([is_active],[not_active],[all]) -> should the package still be active? (calcultaed by payment_plan_activation_date + package__effective_date >= today)
        """
        if filter == "active":
            today = timezone.now()
            vehicles = Vehicle.objects.annotate(
                payment_plan_end_date=ExpressionWrapper(
                    F('payment_plan_activation_date') + F('payment__package__effective_date'),
                    output_field=DateTimeField()
                )
            ).filter(
                lister=user,
                payment__isnull=False,
                payment_plan_end_date__gte=today
            )

            realestates = RealEstate.objects.annotate(
                payment_plan_end_date=ExpressionWrapper(
                    F('payment_plan_activation_date') + F('payment__package__effective_date'),
                    output_field=DateTimeField()
                )
            ).filter(
                lister=user,
                payment__isnull=False,
                payment_plan_end_date__gte=today
            )
        if filter == "not_active":
            today = timezone.now()
            vehicles = Vehicle.objects.annotate(
                payment_plan_end_date=ExpressionWrapper(
                    F('payment_plan_activation_date') + F('payment__package__effective_date'),
                    output_field=DateTimeField()
                )
            ).filter(
                lister=user,
                payment__isnull=False,
                payment_plan_end_date__lte=today
            )

            realestates = RealEstate.objects.annotate(
                payment_plan_end_date=ExpressionWrapper(
                    F('payment_plan_activation_date') + F('payment__package__effective_date'),
                    output_field=DateTimeField()
                )
            ).filter(
                lister=user,
                payment__isnull=False,
                payment_plan_end_date__lte=today
            )


        else:
            vehicles = Vehicle.objects.filter(
                lister=user,
                payment__isnull=False
            )

            realestates = RealEstate.objects.filter(
                lister=user,
                payment__isnull=False
            )

        return vehicles,realestates



    @swagger_auto_schema(
        method='get',
        manual_parameters=[
            openapi.Parameter(
                'filter',
                openapi.IN_QUERY,
                description="Filter based on what the user gives , can be 'active' , 'not_active'  and 'all' ",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of payment records'),
                'next': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description='URL to the next page', nullable=True),
                'previous': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description='URL to the previous page', nullable=True),
                'results': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'type': openapi.Schema(type=openapi.TYPE_STRING, example="vehicles or realestates"),
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=3),
                            'name': openapi.Schema(type=openapi.TYPE_STRING, example="Toyota F 2000"),
                            'price': openapi.Schema(type=openapi.TYPE_INTEGER, example=3000),
                            'img': openapi.Schema(type=openapi.TYPE_STRING, example="vehicle/bmw_FHCUADb.jpg", nullable=True),
                            'package': openapi.Schema(type=openapi.TYPE_STRING, example="SILVER"),
                            'location': openapi.Schema(type=openapi.TYPE_STRING, example="Heartttt", nullable=True)
                        },
                        required=['type', 'id', 'price', 'package']
                    )
                )
            }
        )}
    )
    @action(
        detail=False,
        methods=["GET"],
        url_path="payment_history",
        url_name="Get user's payment history",
        filter_backends=[],
        serializer_class=None,
    )
    def payment_history(self,request):
        filter_query = request.GET.get("filter",False)
        if not filter_query:
            return Response(
                {
                    "detail" : "filter requried"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        vehicles,real_estates = self.get_active_instances(user=request.user,filter=filter_query)

        vehicle_serializer = VitrineVehicleSerializer(vehicles,many=True)
        real_estates_serializer = VitrineRealEstateSerializer(real_estates,many=True)


        combined_data = vehicle_serializer.data + real_estates_serializer.data # type:ignore

        paginator = StandardPagination()
        paginated_combined_data = paginator.paginate_queryset(combined_data, request, view=self)

        response_data = {
                "count": len(combined_data),
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": paginated_combined_data
        }

        return Response(response_data)



    def retrieve(self, request,pk=None):
        instance = self.get_object()
        serializer = CustomUserSerializer(instance)
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
    def history(self,request):
        instance = UserHistory.objects.filter(
            user=request.user
        )
        page = self.paginate_queryset(instance)
        if page:
            serializer = UserHistorySerializer(instance,many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserHistorySerializer(instance,many=True)
        return self.get_paginated_response(serializer.data)


    @action(detail=False,methods=["GET"])
    def favs(self,request):
        instance = UserFavs.objects.filter(
            user=request.user
        )
        page = self.paginate_queryset(instance)
        if page:
            serializer = UserFavsSerializer(instance,many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserFavsSerializer(instance,many=True)
        return self.get_paginated_response(serializer.data)
    


    @swagger_auto_schema(
        method='post',
        operation_description="Reset the user's password by providing the old and new passwords.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['old_password', 'new_password'],
            properties={
                'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='Current password'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
            },
        ),
        responses={
            status.HTTP_204_NO_CONTENT: 'Password reset successfully',
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                }
            )
        }
    )
    @action(
            detail=False,
            methods=["POST"]
    )
    def reset_password(self,request):
        old_pass = request.data.get("old_password",None)
        new_pass = request.data.get("new_password",None)

        if not old_pass or not new_pass:
            return Response(
                {
                    "detail" : "old_password and new_password required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user and request.user.check_password(old_pass):
            request.user.set_password(new_pass)
            request.user.save()
            return Response(
                    status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {
                    "detail": "Invalid Old Pass"
                },
                status=status.HTTP_400_BAD_REQUEST
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

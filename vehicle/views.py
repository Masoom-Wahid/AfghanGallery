from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.parsers import FormParser,MultiPartParser,JSONParser
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from user.perms import IsAuthenticated
from vehicle.filterset import VehicleFilterSet
from .perms import IsVehicleOwner, IsVehicleOwnerOrIsAdminOrStaff
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin,RetrieveModelMixin, UpdateModelMixin
from .models import Vehicle, VehicleImages
from user_info.models import UserFavs, UserHistory
from rest_framework.views import status
from .serializers import VehicleCreationSerializer, VehicleSerializer
from drf_yasg import openapi
from payment.models import PaymentPlan
from utils.tasks import scheduler
from utils.notifs import update_notifs
from django_filters.rest_framework import DjangoFilterBackend



class VehicleViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
    GenericViewSet
):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = VehicleFilterSet
    

    def get_parser_classes(self):
        if self.action == "create":
            return [MultiPartParser(), FormParser()]
        return [JSONParser()]


    def get_permissions(self):
        if self.action in ["create","fav_a_vehicle"]:
            return [IsAuthenticated()]
        elif self.action in ["update","destroy","patch"]:
            return [IsVehicleOwnerOrIsAdminOrStaff()]
        elif self.action in ["upload_img","boost_vehicle"]:
            return [IsVehicleOwner()]
        return [AllowAny()]



    @action(
        methods=["POST"],
        detail=False,
        url_path='(?P<pk>\d+)/boost',
        url_name="Boost a particular vehicle",
        filter_backends=[],
        serializer_class=None,
    )
    def boost_vehicle(self,request,pk=None):
        instance : Vehicle = self.get_object()
        payment_plan : PaymentPlan = get_object_or_404(
            PaymentPlan,
            pk=request.data.get("payment_plan"),
            user=request.user
        )

        if payment_plan.num_of_products >= payment_plan.package.num_of_ads:
            return Response(
                    {
                        "detail" : "max of this package used"
                    },
                    status=status.HTTP_400_BAD_REQUEST
            )
        else:
            payment_plan.num_of_products += 1
            instance.payment = payment_plan  
            instance.payment_plan_activation_date = timezone.now()
            instance.save()
            payment_plan.save()
            return Response(
                    status=status.HTTP_204_NO_CONTENT
            )




    """
    cateogry
    price
    type
    city
    plate_no
    color
    """
    



    def destroy(self, request, pk=None):
        instance = self.get_object()
        instance.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )



    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'img',
                openapi.IN_FORM,
                description="Image file to be uploaded",
                type=openapi.TYPE_FILE,
                required=True
            ),
            *[
                openapi.Parameter(
                    field_name,
                    openapi.IN_FORM,
                    description=f"{field_name} of the vehicle",
                    type=openapi.TYPE_STRING,
                    required=True
                )
                for field_name in VehicleCreationSerializer().get_fields() if field_name != "lister"
            ]
        ],
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Vehicle and image successfully created",
                schema=VehicleCreationSerializer()
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="Validation error or missing image",
                examples={
                    "application/json": {
                        "detail": "one image required"
                    }
                }
            )
        }
    )
    @action(
        detail=False,
        methods=["POST"],
        parser_classes=[MultiPartParser,FormParser],
        url_path='(?P<pk>\d+)/upload',
        url_name="Upload RealEstate images Url",
        filter_backends=[],
        serializer_class=None,
    )
    def upload_img(self,request,pk=None):
        instance = self.get_object()
        imgs = request.FILES.getlist("imgs")
        if not imgs:
            return Response(
                {"detail":"imgs required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        for img in imgs:
            VehicleImages.objects.create(
                img = img,
                vehicle = instance
            )

        return Response(
            status=status.HTTP_201_CREATED
        )


    @action(
        detail=False,
        methods=["POST"],
        url_path='(?P<pk>\d+)/fav',
        url_name="Add a vehicle to favs",
        filter_backends=[],
        serializer_class=None,
    )
    def fav_a_vehicle(self,request,pk=None):
        instance = self.get_object()
        UserFavs.objects.create(
                user=request.user,
                type="vehicle",
                vehicle=instance
        )
        return Response(
                status=status.HTTP_204_NO_CONTENT
        )




    def update(self, request, *args, **kwargs):
        vehicle = self.get_object()
        last_price = vehicle.price
        serializer = VehicleCreationSerializer(
            vehicle,
            data=request.data,
            context={"request":request}
        )
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            

            if request.data.get("price",None):
                scheduler.add_job(
                    update_notifs,
                    args=[
                        instance,
                        instance.price,
                        last_price,
                        "vehicle"
                    ],
                    trigger="date",
                    run_date=timezone.now(),
                )            
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    


    def partial_update(self, request, pk=None):
        vehicle = self.get_object()
        last_price : int = vehicle.price
        serializer = VehicleCreationSerializer(
            vehicle,
            data=request.data,
            partial=True,
            context={"request":request}
        )
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            if request.data.get("price",None):
                scheduler.add_job(
                    update_notifs,
                    args=[
                        instance,
                        instance.price,
                        last_price,
                        "vehicle"
                    ],
                    trigger="date",
                    run_date=timezone.now(),
                )              

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)








    def create(self, request, *args, **kwargs):
        img = request.FILES.get("img")
        if not img:
            return Response(
                {"detail" : "one image required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        requestdata = request.data.copy()
        requestdata['lister'] = request.user.id

        serializer = VehicleCreationSerializer(
            data=requestdata,
            context= {
                "request" : request
            }
        )


        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        VehicleImages.objects.create(
            img = img,
            vehicle=instance
        )

        return Response(
            serializer.data
        )


    def retrieve(self, request,pk=None):
        instance = self.get_object()
        if request.user.is_authenticated:
            UserHistory.objects.create(
                type="vehicle",
                user = request.user,
                vehicle = instance
            )


        serializer = VehicleSerializer(instance)
        return Response(serializer.data)

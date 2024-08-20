from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.parsers import FormParser,MultiPartParser,JSONParser
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from user.perms import IsAuthenticated
from .perms import IsVehicleOwner, IsVehicleOwnerOrIsAdminOrStaff
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin,RetrieveModelMixin, UpdateModelMixin
from .models import Vehicle, VehicleImages
from user_info.models import UserHistory
from rest_framework.views import status
from .serializers import VehicleCreationSerializer, VehicleSerializer
from drf_yasg import openapi
from payment.models import PaymentPlan


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


    def get_parser_classes(self):
        if self.action == "create":
            return [MultiPartParser(), FormParser()]
        return [JSONParser()]


    def get_permissions(self):
        if self.action == "create":
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
    # def boost_vehicle(self,request):
    #     # TODO: what if for some reason the user had 2 active payment plans ?
    #     # i think getting the latest active would be a better plan
    #     # maybe the network was bad or we had an error , so there is not gurantee
    #     # that the user will only have 1 active payment plan per time

    #     try:
    #         payment_instance = Payment.objects.get(
    #                 is_active=True,
    #                 user=request.user
    #         )
    #     except Exception as e:
    #         return Response({

    #         },
    #         status=status.HTTP_400_BAD_REQUEST
    #         )

    #     product = Vehicle.objects.get(
    #             pk=request.data.get("vehicle")
    #     )
    #     if not payment_instance or not payment_instance.is_active:
    #         return Response(
    #                 {
    #                     "detail" : "no active payment plan",
    #                 },
    #             status=HTTP_400_BAD_REQUEST
    #         )


    #     count_of_vehicles = Vehicle.objects.filter(
    #             payment_plan=payment_instance
    #     ).count()

    #     count_of_realestate = Vehicle.objects.filter(
    #             payment_plan=payment_instance
    #     ).count()


    #     # TODO: also count the time , check if the time of the plan has gone down if so
    #     # just make the is_active = False , so that u dont have to bother anymore
    #     if count_of_realestate + count_of_vehicles >= payment_plan.package.nums_of_ads:
    #         return Response(
    #                 {
    #                     "detail" : "max number of ads reached"
    #                 },
    #                 status=status.HTTP_400_BAD_REQUEST
    #         )
    #     else:
    #         product.payment_plan =  payment_instance
    #         product.save()
    #         return Response(
    #                 status=status.HTTP_204_NO_CONTENT
    #         )











    """
            VEHICLE CRUD
            C done
            filter read missing
            R done
            U update done
            D delete done
            upload_imgs done
            retreive -> AllowAny
            create -> UserOnly
            update,patch -> admin,staff,owner
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



    def update(self, request, *args, **kwargs):
        vehicle = self.get_object()
        serializer = VehicleCreationSerializer(
            vehicle,
            data=request.data,
            context={"request":request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    def partial_update(self, request, pk=None):
        vehicle = self.get_object()
        serializer = VehicleCreationSerializer(
            vehicle,
            data=request.data,
            partial=True,
            context={"request":request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
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

from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from vehicle.models import Vehicle
from realestate.models import RealEstate
from rest_framework.response import Response
from vehicle.serializers import VitrineVehicleSerializer
from realestate.serializers import VitrineRealEstateSerializer
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class VitrinePagination(PageNumberPagination):
    page_size = 20


class Vitrine(
    ListModelMixin,
    GenericViewSet
):
    queryset = None
    serializer_class = None
    permission_classes=[AllowAny]
    pagination_class=VitrinePagination
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                'Successful Response',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of items'),
                        'next': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description='URL to the next page', nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description='URL to the previous page', nullable=True),
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the item (vehicle or real estate)'),
                                    'price': openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT, description='Price of the item'),
                                    'img': openapi.Schema(type=openapi.TYPE_STRING, description='Image URL of the item'),
                                    "id" : openapi.Schema(type=openapi.TYPE_INTEGER,description="id of the given thing"),
                                    "type" : openapi.Schema(type=openapi.TYPE_STRING,description="'realestates' or 'vehicles' ")
                                }
                            )
                        )
                    }
                )
            )
        }
    )
     
    def list(self,request):
        vehicles = Vehicle.objects.vitrine_vehicles()
        vehicle_serializer = VitrineVehicleSerializer(vehicles, many=True)
        vehicle_data = vehicle_serializer.data

        real_estates = RealEstate.objects.vitrine_real_estate()
        real_estate_serializer = VitrineRealEstateSerializer(real_estates, many=True)
        real_estate_data = real_estate_serializer.data

        combined_data = vehicle_data + real_estate_data # type:ignore 

        paginator = self.pagination_class()
        paginated_combined_data = paginator.paginate_queryset(combined_data, request, view=self)

        response_data = {
            "count": len(combined_data),
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": paginated_combined_data
        }

        return Response(response_data)

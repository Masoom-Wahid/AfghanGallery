from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from .models import Vehicle
from rest_framework.views import status
from .serializers import VehicleSerializer

class VehiceViewSet(ListModelMixin,GenericViewSet):
    permission_classes = [AllowAny]
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

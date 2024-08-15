from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from .models import RealEstate
from rest_framework.views import status
from .serializers import RealStateSerializer

class RealEstateViewSet(ListModelMixin,GenericViewSet):
    permission_classes = [AllowAny]
    queryset = RealEstate.objects.all()
    serializer_class = RealStateSerializer

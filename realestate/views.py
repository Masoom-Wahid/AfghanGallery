from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.parsers import FormParser,MultiPartParser,JSONParser
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from user.perms import IsAuthenticated
from .perms import IsRealEstateOwner, IsRealEstateOwnerOrIsAdminOrStaff
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin,RetrieveModelMixin, UpdateModelMixin
from .models import RealEstate,RealEstateImage
from user_info.models import UserHistory
from rest_framework.views import status
from .serializers import RealEstateCreationSerializer, RealEstateSerializer
from drf_yasg import openapi


class RealEstateViewSet(
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    GenericViewSet
):
    permission_classes = [AllowAny]
    queryset = RealEstate.objects.all()
    serializer_class = RealEstateSerializer

    def get_parser_classes(self):
        if self.action == "create":
            return [MultiPartParser(), FormParser()]
        return [JSONParser()]


    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        elif self.action in ["update","destroy","patch"]:
            return [IsRealEstateOwnerOrIsAdminOrStaff()]
        elif self.action == "upload_img":
            return [IsRealEstateOwner()]
        return [AllowAny()]


    def destroy(self, request, pk=None):
        instance = self.get_object()

        for img in RealEstateImage.objects.filter(
            realestate = instance
        ):
            img.delete()


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
                    description=f"{field_name} of the realestate",
                    type=openapi.TYPE_STRING,
                    required=True
                )
                for field_name in RealEstateCreationSerializer().get_fields() if field_name != "lister"
            ]
        ],
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Realestate and image successfully created",
                schema=RealEstateCreationSerializer()
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
            RealEstateImage.objects.create(
                img = img,
                realestate = instance
            )

        return Response(
            status=status.HTTP_201_CREATED
        )



    def update(self, request, *args, **kwargs):
        realestate = self.get_object()
        serializer = RealEstateCreationSerializer(
            realestate,
            data=request.data,
            context={"request":request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    def partial_update(self, request, pk=None):
        realestate = self.get_object()
        serializer = RealEstateCreationSerializer(
            realestate,
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

        serializer = RealEstateCreationSerializer(
            data=requestdata,
            context= {
                "request" : request
            }
        )


        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        RealEstateImage.objects.create(
            img = img,
            realestate=instance
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


        serializer = RealEstateSerializer(instance)
        return Response(serializer.data)

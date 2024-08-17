from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin,RetrieveModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from .models import Packages, PaymentHistory, PaymentPlan
from user.perms import IsAdminOrStaff
from .perms import PaymentOwnerOrAdminOrStaff
from .serializers import PackagesSerializer, PaymentPlanSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class PackagesViewset(ModelViewSet):
    queryset = Packages.objects.all()
    serializer_class = PackagesSerializer


    def get_permissions(self):
        if self.action == "list":
            return [AllowAny()]
        return [IsAdminOrStaff()]


class PaymentPlanViewSet(
    GenericViewSet,
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin
):


    def get_permissions(self):
        if self.action == [
            "create",
            "destroy"
        ]:
            return [IsAdminOrStaff()]
        elif self.action == "retrieve":
            return [PaymentOwnerOrAdminOrStaff()]
        return super().get_permissions()

    queryset = PaymentPlan.objects.all()
    serializer_class = PaymentPlanSerializer



    @swagger_auto_schema(
        operation_description="Create a new payment plan for a user.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['package','phone','email'],
            properties={
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number of the user'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the user'),
                'package': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the package'),
            },
        ),
        responses={
            201: PaymentPlanSerializer,
            400: "Validation error: either phone or email is required, but not both.",
            404: "User or package not found",
        }
    )
    def create(self, request):

        """
            STEPS TO CREATING A PAYMENT PLAN
            create the new payment plan
            make the old payment_plan is_active = False
                - `user.payment_plan.is_active = False`

            user->payment_plan -> instance
            payment_history->add

        """



        phone = request.data.get("phone",None)
        email = request.data.get("email",None)



        package = get_object_or_404(
            Packages,
            pk=request.data.get("package",None)
        )

        if not phone and not email:
            raise ValidationError("Either phone or email is required")

        if phone:
            user = get_object_or_404(
                get_user_model(),
                phone_no=phone
            )
        elif email:
            user = get_object_or_404(
                get_user_model(),
                email=email
            )


        user_payment_plan = PaymentPlan.objects.filter(
            user=user
        ).order_by('-created_at').first()

        # just to make sure if the user has a payment plan
        # other wise we are just hitting a null -> null value
        if user_payment_plan:
            user_payment_plan.is_active = False
            user_payment_plan.save()

        instance = PaymentPlan.objects.create(
            package=package,
            user=user
        )

        # add to the users history
        PaymentHistory.objects.create(
            user=user,
            payment=instance
        )





        serializer = PaymentPlanSerializer(
            instance
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = PaymentPlanSerializer(instance)
        return Response(
            serializer.data
        )

    def destroy(self,request):
        instance = self.get_object()
        instance.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

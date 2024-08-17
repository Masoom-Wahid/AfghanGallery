from rest_framework import serializers
from .models import Packages, PaymentHistory,PaymentPlan

class PackagesSerializer(serializers.ModelSerializer):
   class Meta:
      model = Packages
      fields = "__all__"


class PaymentPlanSerializer(serializers.ModelSerializer):
   class Meta:
      model = PaymentPlan
      fields = "__all__"


class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = "__all__"

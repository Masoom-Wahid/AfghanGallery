from rest_framework import serializers
from .models import Packages,PaymentPlan

class PackagesSerializer(serializers.ModelSerializer):
   class Meta:
      model = Packages
      exclude = ["is_valid"]


class PaymentPlanSerializer(serializers.ModelSerializer):
   class Meta:
      model = PaymentPlan
      fields = "__all__"


from rest_framework import serializers
from .models import Packages,PaymentPlan

class PackagesSerializer(serializers.ModelSerializer):
   class Meta:
      model = Packages
      exclude = ["is_valid"]


class PaymentPlanSerializer(serializers.ModelSerializer):
   package_name = serializers.SerializerMethodField()
   remaining_products = serializers.SerializerMethodField()
   class Meta:
      model = PaymentPlan
      fields = "__all__"

   def get_package_name(self,obj):
      return obj.package.name

   def get_remaining_products(self,obj):
      return obj.remaining_products


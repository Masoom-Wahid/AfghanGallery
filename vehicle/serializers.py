from rest_framework import serializers
from .models import Vehicle,VehicleImages
from django.urls import reverse
from django.conf import settings

class VehicleSerializer(serializers.ModelSerializer):
    brandname = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    imgs = serializers.SerializerMethodField()
    class Meta:
        model = Vehicle
        fields = [
            "price",
            "description",
            "brandname",
            "series",
            "type",
            "category",
            "model",
            "year",
            "gear",
            "km",
            "engine_type",
            "heavy_damage_recorded",
            "color",
            "warranty",
            "swap",
            "payment",
            "imgs",
            "created_at",
        ]

    def get_brandname(self,obj):
        return obj.brand.name if obj.brand else None

    def get_category(self,obj):
        return obj.brand.name if obj.brand else None

    def get_imgs(self, obj):
        # request = self.context.get('request')
        imgs = VehicleImages.objects.filter(vehice=obj.id)
        # return [request.build_absolute_uri(settings.MEDIA_URL + img.img.name) for img in imgs]
        return [img.img.name for img in imgs]

from django.core.serializers.base import SerializationError
from django.utils import timezone
from rest_framework import serializers
from .models import Vehicle,VehicleImages
from django.urls import reverse
from django.conf import settings

class VehicleSerializer(serializers.ModelSerializer):
    imgs = serializers.SerializerMethodField()
    class Meta:
        model = Vehicle
        exclude = ["payment","payment_plan_activation_date"]


    def get_imgs(self, obj):
        # request = self.context.get('request')
        imgs = VehicleImages.objects.filter(vehicle=obj.id)
        # return [request.build_absolute_uri(settings.MEDIA_URL + img.img.name) for img in imgs]
        return [img.img.name for img in imgs]


class VehicleCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        exclude= ["created_at","updated_at","payment"]

    def validate_price(self,value):
        if value < 0:
            raise serializers.ValidationError("Price must not be lower than 0")
        return value

    def validate_year(self,value):
        curr_year = timezone.now().year
        if value < 1950 or value > curr_year:
            raise serializers.ValidationError("Year should not be lower than 1950 or higher the current year")

        return value

    def validate_km(self,value):
        if value < 0:
            raise serializers.ValidationError("Km can not be negative ")
        return value


    def validate_plate_no(self,value):
        if value < 0 or value > 99999:
            raise serializers.ValidationError("Plato No can not be negative or bigger than 99,999")
        return value

    def validate_plate_model(self,value):
        if value < 0 or value > 7:
           raise serializers.ValidationError("Plate model cannot be lower than 0 or higher than 7")
        return value


    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if not request:
            return fields
        if request.method in ["PUT","PATCH"]:
            fields["lister"].read_only = True
            return fields
        else:
            return fields


class VitrineVehicleSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    class Meta:
        model = Vehicle
        fields = ["name","price","img"]

    def get_name(self,obj):
        return f"{obj.brand}  {obj.model} {obj.year}"


    def get_img(self,obj):
        first_img = VehicleImages.objects.filter(
            id=obj.id
        ).first()
        return first_img.img.name if first_img else None

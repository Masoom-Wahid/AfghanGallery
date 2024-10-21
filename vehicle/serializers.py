from django.utils import timezone
from rest_framework import serializers

from utils.serializers import generate_keyword_args
from .models import Vehicle,VehicleImages

class VehicleSerializer(serializers.ModelSerializer):
    imgs = serializers.SerializerMethodField()
    lister_name = serializers.SerializerMethodField()
    lister_email = serializers.SerializerMethodField()
    ad_type = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicle
        exclude = ["payment","payment_plan_activation_date"]
        extra_kwargs = generate_keyword_args(
            fields=[field for field  in model._meta.get_fields()],
            unique_names=["plate_no"],
            model=model
        )


    def get_ad_type(self,obj):
        return "vehicles"
    def get_lister_name(self,obj):
        return f"{obj.lister.name} {obj.lister.last_name}"
    
    def get_lister_email(self,obj):
        return str(obj.lister.email)
    def get_imgs(self, obj):
        # request = self.context.get('request')
        imgs = VehicleImages.objects.filter(vehicle=obj.id)
        # return [request.build_absolute_uri(settings.MEDIA_URL + img.img.name) for img in imgs]
        return [img.img.name for img in imgs]


class VehicleCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        exclude= ["created_at","updated_at"]
        extra_kwargs = generate_keyword_args(
            fields=[field.name for field  in model._meta.get_fields()],
            unique_names=["plate_no"],
            model=model
        )
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
            fields["payment"].read_only = True
            fields["payment_plan_activation_date"].ready_only = True
            return fields
        else:
            return fields


class VitrineVehicleSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    ad_type = serializers.SerializerMethodField()
    package = serializers.SerializerMethodField()
    class Meta:
        model = Vehicle
        fields = ["type","id","name","price","img","package","ad_type"]


    def get_package(self,obj) -> str | None:
            if obj.payment != None:
                return obj.payment.package.name
            else:
                return None

    def get_name(self,obj):
        return f"{obj.brand}  {obj.model} {obj.year}"

    def get_ad_type(self,_) -> str:
        return "vehicles"

    def get_img(self,obj):
        first_img = VehicleImages.objects.filter(
            id=obj.id
        ).first()
        return first_img.img.name if first_img else None

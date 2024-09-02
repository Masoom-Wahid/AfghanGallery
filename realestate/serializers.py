from rest_framework import serializers
from .models import RealEstate,RealEstateImage

class RealEstateSerializer(serializers.ModelSerializer):
    imgs = serializers.SerializerMethodField()
    class Meta:
        model = RealEstate
        fields = "__all__"


    def get_imgs(self,obj):
        all_imgs = RealEstateImage.objects.filter(realestate=obj.id)
        return [imgs.img.name for imgs in all_imgs]



class RealEstateCreationSerializer(serializers.ModelSerializer):
    type = serializers.CharField(required=False)
    class Meta:
        model = RealEstate
        exclude= ["created_at","updated_at","payment","payment_plan_activation_date"]

    def validate_price(self,value):
        if value < 0:
            raise serializers.ValidationError("Price must not be lower than 0")
        return value

    def validate_area(self,value):
        if value < 0:
            raise serializers.ValidationError("area should not be negative")
        return value

    def validate_price_per_area(self,value):
        if value < 0:
            raise serializers.ValidationError("price_per_area should not be negative")
        return value

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')


        #just to bypass the nonetype has no attr 'method'
        if not request:
            return fields


        # we dont care either way
        # the 'lister' is not editable by anybody , if u want to
        # change it then delete the whole record
        if request.method in ["PUT","PATCH"]:
            fields["lister"].read_only = True
            return fields
        else:
            return fields



class VitrineRealEstateSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    class Meta:
        model = RealEstate
        fields = ["type","id","location","price","img"]


    def get_type(self,_) -> str:
        return "realestates"
    def get_img(self,obj):
        first_img = RealEstateImage.objects.filter(
            id=obj.id
        ).first()

        return first_img.img.name if first_img else None

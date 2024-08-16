from rest_framework import serializers
from .models import RealEstate,RealEstateImage

class RealStateSerializer(serializers.ModelSerializer):
    imgs = serializers.SerializerMethodField()
    class Meta:
        model = RealEstate
        fields = "__all__"


    def get_imgs(self,obj):
        all_imgs = RealEstateImage.objects.filter(realestate=obj.id)
        return [imgs.img.name for imgs in all_imgs]



class VitrineRealEstateSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField()
    class Meta:
        model = RealEstate
        fields = ["location","price","img"]

    def get_img(self,obj):
        first_img = RealEstateImage.objects.filter(
            id=obj.id
        ).first()

        return first_img.img.name if first_img else None

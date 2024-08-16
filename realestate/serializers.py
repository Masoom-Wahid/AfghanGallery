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

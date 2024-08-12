from django.contrib import admin
from .models import RealEstate,RealEstateType,RealEstateImage


admin.site.register(RealEstate)
admin.site.register(RealEstateType)
admin.site.register(RealEstateImage)

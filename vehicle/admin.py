from django.contrib import admin
from .models import VehicleCategory,Vehicle,VehicleBrand,VehicleImages

admin.site.register(Vehicle)
admin.site.register(VehicleBrand)
admin.site.register(VehicleImages)
admin.site.register(VehicleCategory)

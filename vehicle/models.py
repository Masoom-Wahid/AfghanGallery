from django.db import models
from django.contrib.auth import get_user_model
from payment.models import PaymentPlan

VEHICLE_TYPES = (
    ("rental","Rental"),
    ("on_sale","On Sale")
)


GEAR_TYPES = (
    ("manual","Manual"),
    ("auto","Automatic"),
)



class VehicleCategory(models.Model):
    name = models.CharField(max_length=255,null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self) -> str:
        return self.name


class VehicleBrand(models.Model):
    name  = models.CharField(max_length=255,null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name





class Vehicle(models.Model):
    lister = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    description = models.TextField(null=True,blank=True)
    price = models.IntegerField(null=False,blank=False)
    brand = models.ForeignKey(VehicleBrand,on_delete=models.SET_NULL,null=True,blank=True)
    series = models.CharField(max_length=255,null=False,blank=False)
    # ON_SALE or RENTAL
    type = models.CharField(max_length=20,choices=VEHICLE_TYPES,null=False,blank=False)
    category = models.ForeignKey(VehicleCategory,on_delete=models.SET_NULL,null=True,blank=True)
    model = models.CharField(max_length=255,null=True,blank=True)
    year = models.SmallIntegerField(null=False,blank=False)
    gear = models.CharField(max_length=20,choices=GEAR_TYPES,null=False,blank=False)
    km = models.IntegerField(null=False,blank=False)
    # V8,V16,V4
    engine_type = models.CharField(max_length=40,null=False,blank=False)
    heavy_damage_recorded = models.BooleanField(default=False)
    color = models.CharField(max_length=50,null=False,blank=False)
    warranty = models.BooleanField(default=False)
    swap = models.BooleanField(default=False)

    payment = models.ForeignKey(PaymentPlan,blank=True,null=True,on_delete=models.SET_NULL) 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return self.model



class VehicleImages(models.Model):
    img = models.FileField(upload_to="vehicles",null=False,blank=False)
    vehice = models.ForeignKey(Vehicle,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return str(self.id)

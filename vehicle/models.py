from django.db import models
from django.contrib.auth import get_user_model
from payment.models import PaymentPlan
from django.utils import timezone
from datetime import timedelta
from django.db.models import ExpressionWrapper, F, DurationField,DateTimeField

VEHICLE_TYPES = (
    ("rental","Rental"),
    ("on_sale","On Sale")
)


GEAR_TYPES = (
    ("manual","Manual"),
    ("auto","Automatic"),
)



class VehicleCategory(models.Model):
    name = models.CharField(max_length=255,null=False,blank=False,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self) -> str:
        return self.name


class VehicleBrand(models.Model):
    name  = models.CharField(max_length=255,null=False,blank=False,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name





class VehicleManager(models.Manager):
    def vitrine_vehicles(self):
        """
            filter all vehicles on if they have payment first
            if they do have
            lets check how much time has it passes since
            meaning
            created_at + vitrine > today
        """
        today = timezone.now()
        # add another feild to each row which is payment-created_at + virtine
        vehicles = self.annotate(
            effective_end_date=ExpressionWrapper(
                F('payment__created_at') + F('payment__package__vitrine'),
                output_field=DateTimeField()
            )
        )

        # Filter vehicles where the vitrine is greater than or equal to today
        return vehicles.filter(
            payment__isnull=False,
            payment__is_active=True,
            effective_end_date__gte=today
        )


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


    plate_no = models.IntegerField(null=False,blank=False,unique=True)
    plate_model = models.SmallIntegerField(null=False,blank=False,db_index=True)

    payment = models.ForeignKey(PaymentPlan,blank=True,null=True,on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    objects = VehicleManager()


    def __str__(self) -> str:
        return f"{self.brand} {self.model} {self.year}"



class VehicleImages(models.Model):
    img = models.FileField(upload_to="vehicle",null=False,blank=False)
    vehice = models.ForeignKey(Vehicle,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return str(self.id)

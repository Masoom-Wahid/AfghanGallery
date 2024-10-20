from django.db import models
from django.contrib.auth import get_user_model
from payment.models import PaymentPlan
from django.utils import choices, timezone
from datetime import timedelta
from django.db.models import ExpressionWrapper, F, DurationField,DateTimeField
from utils.models import CITY_CHOICES
from django.core.validators import MaxValueValidator, MinValueValidator

VEHICLE_TYPES = (
    ("rental","Rental"),
    ("on_sale","On Sale")
)


GEAR_TYPES = (
    ("manual","Manual"),
    ("auto","Automatic"),
)



FULES_TYPES = (
    ("lpg","Lpg"),
    ("petrol", "Petrol"),
    ("diesel","Diesel")
)


DIRECTION_TYPES = (
    ("right","Right"),
    ("left","Left")

)


BRAND_CHOICES = [
    ('Toyota', 'Toyota'),
    ('Honda', 'Honda'),
    ('Nissan', 'Nissan'),
    ('Lexus','Lexus'),
    ('Mazda', 'Mazda'),
    ('Benz','Benz'),
    ('BMW','BMW'),
    ('Chevorlet','Chevorlet'),
    ('Mitsubishi', 'Mitsubishi'),
    ('Subaru', 'Subaru'),
    ('Suzuki', 'Suzuki'),
    ('Daihatsu', 'Daihatsu'),
    ('Hyundai', 'Hyundai'),
    ('Kia', 'Kia'),
    ('Geely', 'Geely'),
    ('Great Wall', 'Great Wall'),
    ('BYD', 'BYD'),
    ('Changan', 'Changan'),
    ('BAIC', 'BAIC'),
    ('Foton', 'Foton'),
    ('JAC', 'JAC'),
]


VEHICLE_CATEGORY_CHOICES = [
    ('Sedan', 'Sedan'),
    ('SUV', 'SUV'),
    ('Hatchback', 'Hatchback'),
    ('Truck', 'Truck'),
    ('Minivan', 'Minivan'),
    ('Wagon', 'Wagon'),
    ('Coupe', 'Coupe'),
    ('Convertible', 'Convertible'),
    ('Roadster', 'Roadster'),
    ('Sports Car', 'Sports Car'),
    ('Luxury Car', 'Luxury Car'),
    ('Electric Vehicle', 'Electric Vehicle'),
    ('Hybrid Vehicle', 'Hybrid Vehicle'),
    ('MPV', 'MPV'),
    ('Crossover', 'Crossover'),
    ('Pickup Truck', 'Pickup Truck'),
]



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
        # add another feild to each row which is payment_plan_activation_date + virtine
        vehicles = self.annotate(
            effective_end_date=ExpressionWrapper(
                F('payment_plan_activation_date') + F('payment__package__vitrine'),
                output_field=DateTimeField()
            )
        )

        # Filter vehicles where the vitrine is greater than or equal to today
        return vehicles.filter(
            payment__isnull=False,
            effective_end_date__gte=today
        )




class Vehicle(models.Model):
    lister = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)

    city = models.CharField(max_length=255,null=False,blank=False,choices=CITY_CHOICES)

    description = models.TextField(null=True,blank=True)
    price = models.IntegerField(null=False,blank=False)
    brand = models.CharField(max_length=150,choices=BRAND_CHOICES,null=False,blank=False)
    # ON_SALE or RENTAL
    type = models.CharField(max_length=20,choices=VEHICLE_TYPES,null=False,blank=False)
    category = models.CharField(max_length=80,choices=VEHICLE_CATEGORY_CHOICES,null=False,blank=False)
    model = models.CharField(max_length=255,null=True,blank=True)
    year = models.SmallIntegerField(null=False,blank=False)
    gear = models.CharField(max_length=20,choices=GEAR_TYPES,null=False,blank=False)
    km = models.IntegerField(null=False,blank=False)
    # V8,V16,V4
    engine_type = models.CharField(max_length=40,null=False,blank=False)
    color = models.CharField(max_length=50,null=False,blank=False)
    warranty = models.BooleanField(default=False)
    swap = models.BooleanField(default=False)


    fuel = models.CharField(max_length=120,choices=FULES_TYPES,default="petrol",null=False,blank=False)
    direction =  models.CharField(max_length=120,choices=DIRECTION_TYPES,default="left",null=False,blank=False)

    plate_no = models.IntegerField(null=False,blank=False,unique=True)
    plate_model = models.SmallIntegerField(null=False,blank=False,db_index=True)

    payment = models.ForeignKey(PaymentPlan,blank=True,null=True,on_delete=models.SET_NULL)
    payment_plan_activation_date = models.DateTimeField(null=True,blank=True)



    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    objects = VehicleManager()


    def __str__(self) -> str:
        return f"{self.brand} {self.model} {self.year}"


    def get_price(self) -> int:
        return self.price


class VehicleImages(models.Model):
    img = models.ImageField(upload_to="vehicle",null=False,blank=False)
    vehicle = models.ForeignKey(Vehicle,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return str(self.id)

from django.db import models
from django.contrib.auth import get_user_model
from payment.models import PaymentPlan
from django.utils import timezone
from datetime import timedelta
from django.db.models import ExpressionWrapper, F, DurationField,DateTimeField
from utils.models import CITY_CHOICES
from django.core.validators import MaxValueValidator, MinValueValidator




REAL_STATE_CONTRACT_TYPES = [
    ("mortgage","Mortgage"),
    ("on_sale","On Sale"),
    ("rental","Rental")
]


REAL_ESTATE_TYPE_CHOICES = [
    ('Apartment', 'Apartment'),
    ('House', 'House'),
    ('Building', 'Building'),
    ('Land', 'Land'),
    ('Condominium', 'Condominium'),
    ('Townhouse', 'Townhouse'),
    ('Villa', 'Villa'),
    ('Bungalow', 'Bungalow'),
    ('Duplex', 'Duplex'),
    ('Triplex', 'Triplex'),
    ('Commercial Building', 'Commercial Building'),
    ('Office Space', 'Office Space'),
    ('Retail Space', 'Retail Space'),
    ('Warehouse', 'Warehouse'),
    ('Factory', 'Factory'),
    ('Farm', 'Farm'),
    ('Ranch', 'Ranch'),
    ('Plot', 'Plot'),
    ('Vacant Land', 'Vacant Land'),
    ('Agricultural Land', 'Agricultural Land'),
    ('Industrial Land', 'Industrial Land'),
    ('Commercial Land', 'Commercial Land'),
    ('Residential Land', 'Residential Land'),
]


class RealEstateManager(models.Manager):
    def vitrine_real_estate(self):
        """
            filter all vehicles on if they have payment first
            if they do have
            lets check how much time has it passes since
            meaning
            created_at + vitrine > today
        """
        today = timezone.now()
        # add another feild to each row which is payment-created_at + virtine
        real_estates = self.annotate(
            effective_end_date=ExpressionWrapper(
                F('payment_plan_activation_date') + F('payment__package__vitrine'),
                output_field=DateTimeField()
            )
        )

        # Filter vehicles where the vitrine is greater than or equal to today
        return real_estates.filter(
            payment__isnull=False,
            payment__is_active=True,
            effective_end_date__gte=today
        )

class RealEstate(models.Model):
    lister = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    description = models.TextField(null=True,blank=True)
    city = models.CharField(max_length=255,null=False,blank=False,choices=CITY_CHOICES)
    location = models.CharField(max_length=255,null=False,blank=False)
    area = models.IntegerField(null=False,blank=False)
    price_per_area = models.IntegerField(null=False,blank=False)
    """
        the diff between contract_type and type is that type
        describes the type of real_estate we talking , for example
        building ,land,house etc... , contract type is limited to the tree choice
    """
    contract_type = models.CharField(max_length=40,choices=REAL_STATE_CONTRACT_TYPES)
    type = models.CharField(max_length=100,choices=REAL_ESTATE_TYPE_CHOICES,blank=False,null=False)
    swap = models.BooleanField(default=False)
    water = models.BooleanField(default=False)
    sewage =  models.BooleanField(default=False)
    drilling_and_well = models.BooleanField(default=False)
    road_opened = models.BooleanField(default=False)
    heater = models.BooleanField(default=False)
    loan_compliance = models.BooleanField(default=False)
    price = models.IntegerField(null=False,blank=False)

    payment = models.ForeignKey(PaymentPlan,blank=True,null=True,on_delete=models.SET_NULL)
    payment_plan_activation_date = models.DateTimeField(null=True,blank=True)

    discount = models.PositiveIntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(100)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    objects = RealEstateManager()




    def get_price(self) -> int:
        discount_amount : int = (self.price /  100)  * self.discount
        return self.price - discount_amount


    def __str__(self) -> str:
        return self.location




class RealEstateImage(models.Model):
    img = models.ImageField(upload_to="real_estate",null=False,blank=False)
    realestate = models.ForeignKey(RealEstate,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.img)

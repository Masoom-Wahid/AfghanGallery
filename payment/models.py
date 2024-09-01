from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

class Packages(models.Model):
    name = models.CharField(max_length=255,null=False,blank=False,unique=True)
    price = models.IntegerField(null=False,blank=False)
    num_of_ads = models.SmallIntegerField(null=False,blank=False)
    approval = models.CharField(max_length=60,null=True,blank=True)
    vitrine = models.DurationField(null=False,blank=False,db_index=True)
    effective_date = models.DurationField(null=False,blank=False,db_index=True)
    # since deleting packages is too risky meaning if u delet a pacakge what happens
    # to the users who are still using that package ?
    # it is better to have this field , it simply should be used check if the package is
    # still valid or not 
    is_valid = models.BooleanField(default=True,db_index=True)

    discount = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def get_price(self):
        discount_amount : int = (self.price/100) * self.discount
        return self.price - discount_amount
        
    def __str__(self) -> str:
        return self.name


class PaymentPlan(models.Model):
    package = models.ForeignKey(Packages,on_delete=models.PROTECT)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    # is_active = models.BooleanField(default=True,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    # normalization or wtv , this is the easy route
    # although using .count() would be better but i dont want to count the rows every time
    # so who knows which one is better
    num_of_products = models.PositiveIntegerField(default=0,db_index=True)

    def __str__(self) -> str:
        return f"{self.user.email} == {self.package.name}"



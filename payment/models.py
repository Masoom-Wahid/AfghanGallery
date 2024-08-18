from django.db import models
from django.contrib.auth import get_user_model


class Packages(models.Model):
    name = models.CharField(max_length=255,null=False,blank=False,unique=True)
    price = models.IntegerField(null=False,blank=False)
    num_of_ads = models.SmallIntegerField(null=False,blank=False)
    approval = models.CharField(max_length=60,null=True,blank=True)
    vitrine = models.DurationField(null=False,blank=False,db_index=True)
    effective_date = models.DurationField(null=False,blank=False,db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class PaymentPlan(models.Model):
    package = models.ForeignKey(Packages,on_delete=models.PROTECT)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    # is_active = models.BooleanField(default=True,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # normalization or wtv , this is the easy route
    # although using .count() would be better but i dont want to count the rows every time
    # so who knows which one is better
    num_of_products = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.user.email} == {self.package.name}"



class PaymentHistory(models.Model):
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    payment = models.ForeignKey(PaymentPlan,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return f"{self.id} == {self.user.email}"

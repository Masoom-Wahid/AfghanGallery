from django.db import models
from django.contrib.auth import get_user_model


class Packages(models.Model):
    name = models.CharField(max_length=255,null=False,blank=False)
    price = models.IntegerField(null=False,blank=False)
    num_of_ads = models.SmallIntegerField(null=False,blank=False)
    approval = models.CharField(max_length=60,null=True,blank=True)
    vitrine = models.DurationField(null=False,blank=False)
    effective_date = models.DurationField(null=False,blank=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class PaymentPlan(models.Model):
    package = models.ForeignKey(Packages,on_delete=models.PROTECT)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return f"{self.user.email} == {self.package.name}"



class PaymentHistory(models.Model):
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    payment = models.ForeignKey(PaymentPlan,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return f"{self.id} == {self.user.email}"        


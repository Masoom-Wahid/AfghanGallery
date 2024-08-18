
from django.db import models
from vehicle.models import Vehicle
from realestate.models import RealEstate
from django.contrib.auth import get_user_model



PRODUCT_TYPES = [
    ("vehicle","Vehicle"),
    ("real_estate","RealEstate")
]




class UserFavs(models.Model):
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    type = models.CharField(max_length=50,choices=PRODUCT_TYPES,null=False,blank=False)
    vehicle = models.ForeignKey(Vehicle,on_delete=models.CASCADE,null=True,blank=True)
    real_estate = models.ForeignKey(RealEstate,on_delete=models.CASCADE,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.email} => {self.type}"



class UserNotifications(models.Model):
    """
    since the noficiations are only about fav products i am gonna only store the
    user_fav id
    """
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    msg = models.CharField(max_length=100,blank=False,null=False)
    fav = models.ForeignKey(UserFavs,on_delete=models.CASCADE,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return f""
    # link = models.Url


class UserHistory(models.Model):
    type = models.CharField(max_length=50,choices=PRODUCT_TYPES,null=False,blank=False)
    user = models.ForeignKey(get_user_model(),on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle,on_delete=models.CASCADE,null=True,blank=True)
    real_estate = models.ForeignKey(RealEstate,on_delete=models.CASCADE,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return f"{self.user.email} => {self.type}"

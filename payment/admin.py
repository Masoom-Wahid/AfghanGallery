from django.contrib import admin
from .models import Packages,PaymentHistory,PaymentPlan


admin.site.register(Packages)
admin.site.register(PaymentHistory)
admin.site.register(PaymentPlan)

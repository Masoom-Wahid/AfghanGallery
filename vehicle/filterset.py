from django_filters import rest_framework as filters 
from django.db.models import F, ExpressionWrapper,fields
from django.utils import timezone
from vehicle.models import Vehicle 


class VehicleFilterSet(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price",lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price",lookup_expr="lte")

    class Meta:
        model = Vehicle
        fields = ("category","price","city","type")
    

    def get_queryset(self, qs, value):
        today = timezone.now().date()
        qs = qs.annotate(
            relevance = ExpressionWrapper(
                today - F('payment_plan_activation_date'),
                output_field=fields.DurationField()
            )
        ).order_by('-relevance' if 'relevance' in value else '-relevance')
        return qs



from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls.conf import include
from realestate.views import RealEstateViewSet
from user.views import JwtToken,UserViewSet
from vehicle.views import VehicleViewSet
from payment.views import PackagesViewset,PaymentPlanViewSet
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import routers
from utils.views import Vitrine
from user.token_factory import MyTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
router = routers.DefaultRouter()
router.register(r'users',UserViewSet,basename="users")
router.register(r'vehicles',VehicleViewSet,basename="vehicles")
router.register(r'realestates',RealEstateViewSet,basename="realestate")
router.register(r'vitrine',Vitrine,basename="vitrine")
router.register(r'packages',PackagesViewset,basename="packages")
router.register(r'payments',PaymentPlanViewSet,basename="payment")

schema_view = get_schema_view(
   openapi.Info(
      title="AfghanGallery API",
      default_version='v4',
      description="Description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # path("api/users/",include("user.urls")),
    path("api/",include(router.urls)),
    path("api/auth/",MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
]


if settings.DEBUG:
    urlpatterns.append(path("admin/",admin.site.urls))
    urlpatterns.append(path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),)
    urlpatterns.append(path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),)
    urlpatterns.append(path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

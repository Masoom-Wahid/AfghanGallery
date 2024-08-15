from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls.conf import include
from realestate.views import RealEstateViewSet
from user.views import JwtToken,UserViewSet
from vehicle.views import VehiceViewSet
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users',UserViewSet,basename="users")
router.register(r'vehicles',VehiceViewSet,basename="vehicles")
router.register(r'realestates',RealEstateViewSet,basename="realestate")

schema_view = get_schema_view(
   openapi.Info(
      title="AfghanGallery API",
      default_version='v1',
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
    path("api/auth/",JwtToken.as_view()),
]


if settings.DEBUG:
    urlpatterns.append(path("admin/",admin.site.urls))
    urlpatterns.append(path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),)
    urlpatterns.append(path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),)
    urlpatterns.append(path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

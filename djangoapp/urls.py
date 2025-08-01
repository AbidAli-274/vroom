from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from djangoapp import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

swagger_url = ""

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@local.dev"),
        license=openapi.License(name="BSD License"),
    ),
    url=swagger_url,
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("", include("account.urls")),
    path("inventory/", include("inventory.urls")),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

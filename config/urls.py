from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("dashboard/", include("dashboard.urls")),
    path("accounts/", include("accounts.urls")),
    path("", include("properties.urls")),
    # Technical Django admin kept at /django-admin/ (optional)
    path("django-admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Baba Khatu Shyam Real Estate Admin"
admin.site.site_title = "Vidarbha Property Admin"
admin.site.index_title = "Manage Vidarbha properties & customer interests"

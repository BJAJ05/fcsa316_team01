"""
Root URL configuration.

Each app owns its endpoints in its own `urls.py`; they are mounted here under /api/.
All API paths end with a slash, e.g. POST /api/auth/register/.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from config.views import health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health, name="health"),
    path("api/auth/", include("accounts.urls")),
    path("api/classes/", include("classrooms.urls")),
    path("api/assignments/", include("assignments.urls")),
    path("api/submissions/", include("grading.urls")),
    path("api/analytics/", include("analytics.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

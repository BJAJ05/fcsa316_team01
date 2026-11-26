"""URL routes for `analytics`, mounted at /api/analytics/ in config/urls.py."""

from django.urls import path

from . import views

urlpatterns = [
    path("progress/", views.StudentProgressView.as_view(), name="student-progress"),
]

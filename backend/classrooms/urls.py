"""URL routes for `classrooms`, mounted at /api/classes/ in config/urls.py."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.ClassListCreateView.as_view(), name="class-list-create"),
]

"""URL routes for `assignments`, mounted at /api/assignments/ in config/urls.py."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.AssignmentListCreateView.as_view(), name="assignment-list-create"),
    path("<int:assignment_id>/", views.AssignmentDetailView.as_view(), name="assignment-detail"),
]

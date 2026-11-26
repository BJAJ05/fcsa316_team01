"""URL routes for `grading`, mounted at /api/submissions/ in config/urls.py."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.SubmissionCreateView.as_view(), name="submission-create"),
    path("<int:submission_id>/", views.SubmissionDetailView.as_view(), name="submission-detail"),
]

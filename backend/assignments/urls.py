"""URL routes for `assignments`, mounted at /api/assignments/ in config/urls.py."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.AssignmentListCreateView.as_view(), name="assignment-list-create"),
    path("<int:assignment_id>/", views.AssignmentDetailView.as_view(), name="assignment-detail"),
    path(
        "<int:assignment_id>/questions/",
        views.QuestionCreateView.as_view(),
        name="question-create",
    ),
    path(
        "<int:assignment_id>/questions/<int:question_id>/",
        views.QuestionDetailView.as_view(),
        name="question-detail",
    ),
]

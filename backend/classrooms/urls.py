"""URL routes for `classrooms`, mounted at /api/classes/ in config/urls.py."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.ClassListCreateView.as_view(), name="class-list-create"),
    path("join/", views.JoinClassView.as_view(), name="class-join"),
    path("<int:class_id>/", views.ClassDetailView.as_view(), name="class-detail"),
    path("<int:class_id>/students/", views.ClassStudentListView.as_view(), name="class-students"),
    path(
        "<int:class_id>/students/<int:student_id>/",
        views.ClassStudentDetailView.as_view(),
        name="class-student-detail",
    ),
]

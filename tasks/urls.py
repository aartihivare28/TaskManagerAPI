from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, ProjectViewSet , DashboardView, UpcomingTaskView, SubTaskViewSet
from django.urls import path, include

router = DefaultRouter()

router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"subtasks", SubTaskViewSet, basename="subtask")

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("upcoming/", UpcomingTaskView.as_view(), name="upcoming-tasks"),
    path("", include(router.urls)),
]


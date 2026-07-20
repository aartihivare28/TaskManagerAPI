from rest_framework.routers import DefaultRouter
from .views import (TaskViewSet, 
                    DashboardView,
                    UpcomingTaskView,
)
from django.urls import path, include

router = DefaultRouter()

router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("upcoming/", UpcomingTaskView.as_view(), name="upcoming-tasks"),
    path("", include(router.urls)),
]


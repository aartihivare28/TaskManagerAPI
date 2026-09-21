from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import SubTaskFilter, TaskFilter
from .models import Project, SubTask, Task
from .permissions import IsOwnerOrAdmin
from .serializers import (
    ProjectSerializer,
    ProjectWithTaskSerializer,
    SubTaskSerializer,
    TaskSerializer,
)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TaskFilter

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "completed",
        "priority",
        "status",
        "category",
    ]

    search_fields = [
        "title",
        "description",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "due_date",
    ]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Task.objects.none()

        qs = Task.objects.prefetch_related("subtasks").select_related("project", "category", "owner")
        if self.request.user.is_staff:
            return qs.all().order_by("-created_at")

        return qs.filter(owner=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        """Automatically assign the logged-in user as owner."""
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["get"], url_path="subtasks")
    def subtasks(self, request, pk=None):
        task = self.get_object()
        subtasks = task.subtasks.all()
        serializer = SubTaskSerializer(subtasks, many=True, context={"request": request})
        return Response(serializer.data)


class SubTaskViewSet(viewsets.ModelViewSet):
    serializer_class = SubTaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_class = SubTaskFilter
    search_fields = ["title"]
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return SubTask.objects.none()

        qs = SubTask.objects.select_related("task", "owner")
        if self.request.user.is_staff:
            return qs.all().order_by("-created_at")

        return qs.filter(owner=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProjectWithTaskSerializer
        return ProjectSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Project.objects.none()

        qs = Project.objects.prefetch_related("tasks__subtasks")
        if self.request.user.is_staff:
            return qs.all().order_by("-created_at")

        return qs.filter(owner=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        """Automatically assign the logged-in user as owner."""
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["get"], url_path="tasks")
    def tasks(self, request, pk=None):
        project = self.get_object()
        tasks = project.tasks.prefetch_related("subtasks").all()
        serializer = TaskSerializer(tasks, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="create-with-tasks")
    def create_with_tasks(self, request):
        """
        POST /projects/create-with-tasks/
        Creates a Project and any number of Task rows under it in a single request.
        """
        serializer = ProjectWithTaskSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            project = serializer.save()

        return Response(
            ProjectWithTaskSerializer(project, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(owner=request.user)

        data = {
            "total_tasks": tasks.count(),
            "completed_tasks": tasks.filter(completed=True).count(),
            "pending_tasks": tasks.filter(status="Pending").count(),
            "in_progress_tasks": tasks.filter(status="In Progress").count(),
            "high_priority": tasks.filter(priority="High").count(),
            "medium_priority": tasks.filter(priority="Medium").count(),
            "low_priority": tasks.filter(priority="Low").count(),
        }

        return Response(data)


class UpcomingTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        next_week = today + timedelta(days=7)

        tasks = Task.objects.filter(
            owner=request.user,
            due_date__range=[today, next_week],
            completed=False,
        )

        serializer = TaskSerializer(tasks, many=True, context={"request": request})

        return Response(serializer.data)

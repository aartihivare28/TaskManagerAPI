from .permissions import IsOwnerOrAdmin
from rest_framework import viewsets, status
from rest_framework.decorators import action
# from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db import transaction
from .models import Task, Project
from .serializers import TaskSerializer, ProjectSerializer, ProjectWithTaskSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    filter_backends=[
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
        
        if self.request.user.is_staff:
            return Task.objects.all().order_by("-created_at")
        
        return Task.objects.filter(owner=self.request.user).order_by("-created_at")
    
    def perform_create(self, serializer):
        """
        Automatically assign the logged-in user as owner.
        """

        serializer.save(owner=self.request.user)

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Project.objects.none()
        
        if self.request.user.is_staff:
            print("inside if")
            return Project.objects.all().order_by("-created_at")
        print("outside if")
        return Project.objects.filter(owner=self.request.user).order_by("-created_at")
    
    def perform_create(self, serializer):
        """Automatically assign the logged-in user as owner."""
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["post"], url_path="create-with-tasks")
    def create_with_tasks(self, request):
        """
        POST /projects/create-with-tasks/

        Creates a Project and any number of Task rows under it in a
    single request. Example body:

    {
        "name": "Website Revamp",
        "description": "Q4 redesign",
        "tasks": [
            {"title": "Wireframes", "priority": "High", "due_date": "2026-09-20"},
            {"title": "Homepage build"},
            {"title": "QA pass", "status": "Pending"}
        ]
    }
    """
        
        serializer = ProjectWithTaskSerializer(
        data=request.data, context={"request": request}
    )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            project = serializer.save()

        return Response(
            ProjectWithTaskSerializer(project, context={"request":request}).data,
            status=status.HTTP_201_CREATED,
    )


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(owner=request.user)

        data =  {
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
            completed = False,
        )

        serializer = TaskSerializer(tasks, many=True)

        return Response(serializer.data)
# Create your views here.

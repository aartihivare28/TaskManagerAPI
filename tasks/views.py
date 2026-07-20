from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Task
from .serializers import TaskSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from datetime import timedelta
from django.utils import timezone

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

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

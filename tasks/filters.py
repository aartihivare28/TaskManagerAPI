import django_filters
from .models import Task, SubTask


class TaskFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    description = django_filters.CharFilter(field_name="description", lookup_expr="icontains")
    due_date_after = django_filters.DateFilter(field_name="due_date", lookup_expr="gte")
    due_date_before = django_filters.DateFilter(field_name="due_date", lookup_expr="lte")
    project = django_filters.NumberFilter(field_name="project_id")

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "due_date_after",
            "due_date_before",
            "completed",
            "status",
            "priority",
            "category",
            "project",
        ]


class SubTaskFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    task = django_filters.NumberFilter(field_name="task_id")
    completed = django_filters.BooleanFilter(field_name="completed")

    class Meta:
        model = SubTask
        fields = ["id", "title", "task", "completed", "created_at", "updated_at"]
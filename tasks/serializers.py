from rest_framework import serializers
from .models import Task, Category, Project

class TaskSerializer(serializers.ModelSerializer):

    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Task

        fields = [
            "id",
            "title",
            "description",
            "category",
            "attachment",
            "priority",
            "status",
            "due_date",
            "completed",
            "created_at",
            "updated_at",
            "owner",
        ]

        read_only_fields = [
            "created_at",
            "updated_at",
            "owner",
        ]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class ProjectSerializer(serializers.ModelSerializer):
    """plain project serializser - used for normal list/retrieve/update."""
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
            "owner",
        ]
        read_only_fields = ["created_at", "updated_at", "owner"]

class ProjectTaskInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "category",
            "priority",
            "status",
            "due_date",
            "completed",
        ]
        

class ProjectWithTaskSerializer(serializers.ModelSerializer):
    tasks = ProjectTaskInputSerializer(many=True, required=False, write_only=True)
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "owner",
            "created_at",
            "updated_at",
            "tasks",
        ]
        read_only_fields = ["created_at", "updated_at", "owner"]

    def create(self, validated_data):
        tasks_data = validated_data.pop("tasks", [])
        owner = self.context["request"].user

        project = Project.objects.create(owner=owner, **validated_data)

        tasks = [
            Task(project=project, owner=owner, **task_data)
            for task_data in tasks_data
        ]
        Task.objects.bulk_create(tasks)

        return project
        
    def to_representation(self, instance):
        """Return the created project with its tasks fully expanded."""
        data = ProjectSerializer(instance, context=self.context).data
        data["tasks"] = TaskSerializer(
            instance.tasks.all(), many=True, context=self.context
        ).data
        return data
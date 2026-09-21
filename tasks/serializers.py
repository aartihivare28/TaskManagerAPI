from rest_framework import serializers
from .models import Task, Category, Project, SubTask


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class SubTaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = SubTask
        fields = [
            "id",
            "task",
            "title",
            "completed",
            "created_at",
            "updated_at",
            "owner",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "owner"]
        extra_kwargs = {
            "task": {"required": False},
        }

    def validate(self, attrs):
        # When creating a SubTask directly (not nested inside a Task), task is required
        if not self.instance and not self.parent and "task" not in attrs:
            raise serializers.ValidationError({"task": "This field is required."})
        return attrs


class TaskSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, required=False)
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
            "project",
            "subtasks",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "owner",
        ]

    def create(self, validated_data):
        subtasks_data = validated_data.pop("subtasks", [])
        owner = validated_data.get("owner")
        if not owner and "request" in self.context:
            owner = self.context["request"].user
            validated_data["owner"] = owner

        task = Task.objects.create(**validated_data)

        for subtask_data in subtasks_data:
            SubTask.objects.create(task=task, owner=task.owner, **subtask_data)

        return task

    def update(self, instance, validated_data):
        subtasks_data = validated_data.pop("subtasks", None)
        task = super().update(instance, validated_data)

        if subtasks_data is not None:
            owner = task.owner
            for subtask_data in subtasks_data:
                SubTask.objects.create(task=task, owner=owner, **subtask_data)

        return task


class ProjectSerializer(serializers.ModelSerializer):
    """Project serializer with nested tasks and subtasks for read representations."""
    owner = serializers.ReadOnlyField(source="owner.username")
    tasks = TaskSerializer(many=True, read_only=True)

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
        read_only_fields = ["id", "created_at", "updated_at", "owner"]


class ProjectWithTaskSerializer(serializers.ModelSerializer):
    """Serializer used for creating/updating a project with nested tasks (and subtasks)."""
    tasks = TaskSerializer(many=True, required=False)
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
        read_only_fields = ["id", "created_at", "updated_at", "owner"]

    def create(self, validated_data):
        tasks_data = validated_data.pop("tasks", [])
        owner = validated_data.get("owner")
        if not owner and "request" in self.context:
            owner = self.context["request"].user
            validated_data["owner"] = owner

        project = Project.objects.create(**validated_data)

        for task_data in tasks_data:
            subtasks_data = task_data.pop("subtasks", [])
            task = Task.objects.create(project=project, owner=owner, **task_data)
            for subtask_data in subtasks_data:
                SubTask.objects.create(task=task, owner=owner, **subtask_data)

        return project
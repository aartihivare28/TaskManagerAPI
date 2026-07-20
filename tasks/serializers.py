from rest_framework import serializers
from .models import Task, Category

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
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Task(models.Model):
   

    PRIORITY_CHOICES = [
        ("High", "High"),
        ("Medium", "Medium"),
        ("Low", "Low"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Completed", "completed"),
    ]

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )

    attachment = models.FileField(
        upload_to="task_files/",
        null=True,
        blank=True,
    )


    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="Medium",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending",
    )
    due_date = models.DateField(null=True, blank=True)

    completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    def __str__(self):
        return self.title
# Create your models here.

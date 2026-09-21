from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="projects",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Task(models.Model):

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tasks",
    )
   
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

class SubTask(models.Model):
    task = models.ForeignKey(Task,on_delete=models.CASCADE, related_name="subtasks")
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subtasks",
    )

    def __str__(self):
        return self.title

@receiver(post_save, sender=SubTask)
def task_completed(sender, instance, **kwargs):
    task = instance.task
    subtasks = task.subtasks.all()

    if not subtasks.exists():
        return

    all_done = not subtasks.filter(completed=False).exists()

    if all_done and not task.completed:
        task.completed = True
        task.save()

    elif not all_done and task.completed:
        task.completed = False
        task.save()


    


# Create your models here.

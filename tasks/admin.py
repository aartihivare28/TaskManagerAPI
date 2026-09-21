from django.contrib import admin
from .models import Task, Category, Project, SubTask

admin.site.register(Project)
admin.site.register(Task)
admin.site.register(SubTask)
admin.site.register(Category)

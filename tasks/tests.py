from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Project, SubTask, Task


class TaskAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="aarti",
            password="password123",
        )

        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

    def test_create_task(self):
        data = {
            "title": "Learn Testing",
            "description": "Write DRF tests",
            "priority": "High",
            "status": "Pending",
            "completed": False,
        }

        response = self.client.post("/api/tasks/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Learn Testing")

    def test_get_tasks(self):
        Task.objects.create(
            title="Task 1",
            description="Testing",
            priority="High",
            status="Pending",
            completed=False,
            owner=self.user,
        )

        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results", response.data)), 1)

    def test_create_task_with_subtasks(self):
        data = {
            "title": "Task with subtasks",
            "description": "Testing nested subtasks creation",
            "priority": "High",
            "status": "Pending",
            "subtasks": [
                {"title": "Subtask A"},
                {"title": "Subtask B"},
            ],
        }

        response = self.client.post("/api/tasks/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["subtasks"]), 2)

        task = Task.objects.get(id=response.data["id"])
        self.assertEqual(task.subtasks.count(), 2)
        self.assertEqual(task.subtasks.first().owner, self.user)

    def test_create_project_with_tasks_and_subtasks(self):
        data = {
            "name": "Backend Overhaul",
            "description": "Refactor APIs",
            "tasks": [
                {
                    "title": "Model setup",
                    "priority": "High",
                    "subtasks": [
                        {"title": "Add migrations"},
                        {"title": "Run tests"},
                    ],
                }
            ],
        }

        response = self.client.post("/api/projects/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["tasks"]), 1)
        self.assertEqual(len(response.data["tasks"][0]["subtasks"]), 2)

        project = Project.objects.get(id=response.data["id"])
        self.assertEqual(project.tasks.count(), 1)
        task = project.tasks.first()
        self.assertEqual(task.subtasks.count(), 2)

    def test_subtask_autocompletes_parent_task(self):
        # Create a task with two subtasks
        task = Task.objects.create(
            title="Auto complete test",
            owner=self.user,
        )
        sub1 = SubTask.objects.create(task=task, owner=self.user, title="Sub 1", completed=False)
        sub2 = SubTask.objects.create(task=task, owner=self.user, title="Sub 2", completed=False)

        task.refresh_from_db()
        self.assertFalse(task.completed)

        # Complete first subtask
        sub1.completed = True
        sub1.save()
        task.refresh_from_db()
        self.assertFalse(task.completed)

        # Complete second subtask -> signal should trigger task completion
        sub2.completed = True
        sub2.save()
        task.refresh_from_db()
        self.assertTrue(task.completed)

    def test_filter_tasks_by_project(self):
        proj1 = Project.objects.create(name="Project 1", owner=self.user)
        proj2 = Project.objects.create(name="Project 2", owner=self.user)

        Task.objects.create(title="Task in P1", project=proj1, owner=self.user)
        Task.objects.create(title="Task in P2", project=proj2, owner=self.user)

        response = self.client.get(f"/api/tasks/?project={proj1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Task in P1")

    def test_custom_actions(self):
        project = Project.objects.create(name="Custom Actions Proj", owner=self.user)
        task = Task.objects.create(title="Action Task", project=project, owner=self.user)
        sub = SubTask.objects.create(title="Action Subtask", task=task, owner=self.user)

        # GET /api/projects/{id}/tasks/
        p_res = self.client.get(f"/api/projects/{project.id}/tasks/")
        self.assertEqual(p_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(p_res.data), 1)
        self.assertEqual(p_res.data[0]["title"], "Action Task")

        # GET /api/tasks/{id}/subtasks/
        t_res = self.client.get(f"/api/tasks/{task.id}/subtasks/")
        self.assertEqual(t_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(t_res.data), 1)
        self.assertEqual(t_res.data[0]["title"], "Action Subtask")

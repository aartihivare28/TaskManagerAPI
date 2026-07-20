from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Task

class TaskAPITest(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="aarti",
            password="password123"
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
            "completed": False
        }

        response = self.client.post("/api/tasks/",data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_tasks(self):
        Task.objects.create(
            title="Task 1",
            description="Testing",
            priority="High",
            status="Pending",
            completed=False,
            owner=self.user
        )

        response = self.client.get("/api/tasks/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
# Create your tests here.

import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from projects.models import Project

User = get_user_model()


class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="owner@example.com",
            name="Owner",
            surname="User",
            password="pass",
        )

    def test_create_project(self):
        project = Project.objects.create(
            name="Test Project",
            description="A test project",
            owner=self.user,
            status="open",
        )
        self.assertEqual(project.name, "Test Project")
        self.assertEqual(project.status, "open")
        self.assertEqual(str(project), "Test Project")


class ProjectListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="list@example.com",
            name="List",
            surname="User",
            password="pass",
        )
        Project.objects.create(name="Proj 1", owner=self.user, status="open")
        Project.objects.create(name="Proj 2", owner=self.user, status="open")

    def test_project_list(self):
        response = self.client.get(reverse("projects:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Proj 1")
        self.assertContains(response, "Proj 2")


class ProjectDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="detail@example.com",
            name="Detail",
            surname="User",
            password="pass",
        )
        self.project = Project.objects.create(name="Detail Project", owner=self.user)

    def test_project_detail(self):
        response = self.client.get(reverse("projects:detail", kwargs={"pk": self.project.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detail Project")


class ToggleFavoriteTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="fav@example.com",
            name="Fav",
            surname="User",
            password="pass",
        )
        self.owner = User.objects.create_user(
            email="owner2@example.com",
            name="Owner",
            surname="Two",
            password="pass",
        )
        self.project = Project.objects.create(name="Fav Project", owner=self.owner)
        self.client.login(username="fav@example.com", password="pass")

    def test_toggle_favorite_add(self):
        response = self.client.post(
            reverse("projects:toggle_favorite", kwargs={"pk": self.project.pk}),
            content_type="application/json",
            data=json.dumps({}),
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["favorited"])
        self.assertIn(self.project, self.user.favorites.all())

    def test_toggle_favorite_requires_login(self):
        self.client.logout()
        response = self.client.post(
            reverse("projects:toggle_favorite", kwargs={"pk": self.project.pk}),
        )
        self.assertEqual(response.status_code, 302)


class CreateProjectTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="create@example.com",
            name="Create",
            surname="User",
            password="pass",
        )
        self.client.login(username="create@example.com", password="pass")

    def test_create_project_get(self):
        response = self.client.get(reverse("projects:create"))
        self.assertEqual(response.status_code, 200)

    def test_create_project_post(self):
        response = self.client.post(reverse("projects:create"), {
            "name": "New Project",
            "description": "Nice project",
            "status": "open",
            "github_url": "",
        })
        self.assertEqual(response.status_code, 302)
        project = Project.objects.get(name="New Project")
        self.assertEqual(project.owner, self.user)
        self.assertIn(self.user, project.participants.all())


class CompleteProjectTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="complete@example.com",
            name="Complete",
            surname="User",
            password="pass",
        )
        self.project = Project.objects.create(
            name="To Complete",
            owner=self.user,
            status="open",
        )
        self.client.login(username="complete@example.com", password="pass")

    def test_complete_project(self):
        response = self.client.post(
            reverse("projects:complete", kwargs={"pk": self.project.pk}),
            content_type="application/json",
            data=json.dumps({}),
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["status"], "ok")
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, "closed")

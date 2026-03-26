from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
from .models import Project, Task

class AdvancedProjectTests(TestCase):
    def setUp(self):
        
        self.user = User.objects.create_user(username='pro_coder', password='password123')
        self.client.login(username='pro_coder', password='password123')
        self.project_url = reverse('create_project')
        
        self.project = Project.objects.create(
            owner=self.user, 
            title="Initial Test Project",
            description="Base for testing"
        )

    @patch('notes.views.fetch_unsplash_cover')
    def test_unsplash_integration_on_create(self, mock_fetch):
        """Tests that the Unsplash helper is called during project creation."""
        mock_fetch.return_value = b"fake_image_data"
        data = {'title': 'Nature Study', 'description': 'Testing API call'}
        self.client.post(self.project_url, data)
        self.assertTrue(mock_fetch.called)

    def test_dashboard_context_data(self):
        """Ensures the home view carries the correct project count."""
        # Add one more project (total will be 2)
        Project.objects.create(owner=self.user, title="Project 2")
        response = self.client.get(reverse('home'))
        self.assertEqual(len(response.context['projects']), 2)

    def test_task_status_ajax_view(self):
        """Tests the AJAX status update returns 200 OK."""
        task = Task.objects.create(project=self.project, title="Update Me", status='todo')
        url = reverse('update_task_status', kwargs={'task_id': task.id, 'status': 'doing'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'doing')

    def test_delete_task_view(self):
        """Tests that a task is actually removed from the DB."""
        task = Task.objects.create(project=self.project, title="To be deleted")
        url = reverse('delete_task', kwargs={'task_id': task.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_toggle_pin_project_ajax(self):
        """Tests the AJAX pinning logic."""
        url = reverse('toggle_pin_project', kwargs={'project_id': self.project.id})
        response = self.client.post(url)
        self.project.refresh_from_db()
        self.assertTrue(self.project.is_pinned)

    def test_search_projects_ajax(self):
        """Tests that the search correctly filters projects by title."""
        url = f"{reverse('search_projects')}?q=Initial"
        response = self.client.get(url)
        self.assertEqual(len(response.json()['projects']), 1)
        self.assertEqual(response.json()['projects'][0]['title'], "Initial Test Project")
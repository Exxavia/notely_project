from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
from .models import Project, Task

class AdvancedProjectTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='pro_coder', password='password123')
        self.client.login(username='pro_coder', password='password123')
        self.project_url = reverse('create_project')

    @patch('notes.views.fetch_unsplash_cover')
    def test_unsplash_integration_on_create(self, mock_fetch):
        """ADVANCED: Test that the Unsplash helper is called when no image is provided."""
        # We tell the mock to return "fake_image_data" instead of actually calling the web
        mock_fetch.return_value = b"fake_image_data"
        
        data = {'title': 'Nature Study', 'description': 'Testing API call'}
        self.client.post(self.project_url, data)
        
        # Verify our helper function was actually triggered by the view
        self.assertTrue(mock_fetch.called)

    def test_dashboard_context_data(self):
        """ADVANCED: Ensure the home view carries the correct project count in context."""
        Project.objects.create(owner=self.user, title="Project 1")
        Project.objects.create(owner=self.user, title="Project 2")
        
        response = self.client.get(reverse('home'))
        
        # Check if the 'projects' list in the HTML template has exactly 2 items
        self.assertEqual(len(response.context['projects']), 2)

    def test_task_status_ajax_view(self):
        """ADVANCED: Test the AJAX status update view returns JSON, not HTML."""
        project = Project.objects.create(owner=self.user, title="AJAX Test")
        task = Task.objects.create(project=project, title="Update Me", status='todo')
        
        # Simulate an AJAX POST request to change status to 'doing'
        url = reverse('update_task_status', kwargs={'task_id': task.id, 'status': 'doing'})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'doing')
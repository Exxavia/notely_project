from django.urls import path
from . import views

urlpatterns = [

    # ---------------- HOME ----------------
    path('', views.home, name='home'),

    # ---------------- PROJECT ----------------
    path('create-project/', views.create_project, name='create_project'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/add-task/', views.add_task, name='add_task'),
    path('project/<int:project_id>/pin/', views.toggle_pin_project, name='toggle_pin_project'),

    # ---------------- TASK ----------------
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('task/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('task/<int:task_id>/quick/', views.toggle_quick_access, name='toggle_quick_access'),

    #  AJAX STATUS
    path('task/<int:task_id>/status/<str:status>/', views.update_task_status, name='update_task_status'),

    # ---------------- SUBTASK ----------------
    path('task/<int:task_id>/add-subtask/', views.add_subtask, name='add_subtask'),
    path('subtask/<int:task_id>/toggle/', views.toggle_subtask, name='toggle_subtask'),

    path('search/', views.search_projects, name='search_projects'),
    path('chart/<str:type>/', views.chart_data, name='chart_data'),
    path('tasks/filter/', views.filter_tasks, name='filter_tasks'),
    path('tasks/api/', views.filter_tasks_api, name='filter_tasks_api'),

]
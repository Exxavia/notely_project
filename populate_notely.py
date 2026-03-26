import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','notely_project.settings')
import django
django.setup()
from accounts.models import User, UserProfile
from notes.models import Project, Task

def populate(): 
    pass

def add_projects():
    pass

def add_tasks():
    pass
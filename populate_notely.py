import os
import random
from datetime import date, timedelta
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notely_project.settings')
import django
django.setup()
from django.contrib.auth.models import User
from accounts.models import UserProfile
from notes.models import Project, Task

def construct_user_data(): 
    first_names = ['Max','Alice','Kat','Pedro','Daniel']
    last_names = ['Smith','Radov','Lewis','Loo','Thain']
    occupations = ['teacher','student','professor','manager','intern']
    fname = random.choice(first_names)
    return {'username': f'{fname}{random.choice(last_names)}_t',
            'email': f'{fname.lower()}{random.choice(last_names).lower()}_t@example.com',
            'password': f'{fname}123',
            'bio': random.choice(occupations),
            'is_superuser': False
    }

def create_user(): 
    pass

def get_random_avatar():
    avatar_dir = 'media/avatars/'
    if os.path.exists(avatar_dir): 
        avatars = [f for f in os.listdir(avatar_dir) if f.endswith(('.jpg','.jpeg','.png','.gif'))]
        if avatars:
            return os.path.join(avatar_dir, random.choice(avatars))
    return None

def get_random_cover_image():
    cover_image_dir = 'media/cover_images/'
    if os.path.exists(cover_image_dir): 
        cover_images = [f for f in os.listdir(cover_image_dir) if f.endswith(('.jpg','.jpeg','.png','.gif'))]
        if cover_images:
            return os.path.join(cover_image_dir, random.choice(cover_images)) 
    return None

def add_projects(title, description, cover_image):
    p = Project.objects.get_or_create(title=title)
    p.save()
    return p
    

def add_tasks(title, description = '', due = '', priority = '', sub = '', is_quick_access = False):
    t = Task.objects.get_or_create(title=title)
    t.save()
    return t

def populate(): 
    # Create: Sample users, projects and tasks for testing purposes
    print("\nCreate Users\n")
    users = []
    test_user_data = [construct_user_data() for i in range(5)]
    for user_data in test_user_data: 
        user, created = User.objects.get_or_create(
            username = user_data['username'], 
            defaults = {
                'email': user_data['email'],
                'is_active': True,
                'is_superuser': user_data['is_superuser'],
                'is_staff': user_data['is_superuser']
            }
        )

        if created: 
            user.set_password(user_data['password'])
            user.save()
            print(f" Created: {user.username} (password: {user_data['password']})")
        else:
            print(f" Exists: {user.username}")

        profile, profile_created = UserProfile.objects.get_or_create(user=user)
        if profile_created or not profile.bio:
            profile.bio = user_data['bio']
            avatar_path = get_random_avatar()
            if avatar_path and not profile.avatar:
                with open(avatar_path, 'rb') as f:
                    profile.avatar.save(os.path.basename(avatar_path), File(f), save=True)
            profile.save() 

        users.append(user)
        print(f'Created {len(users)} users')
    
    print("\nCreate Projects\n")
    projects = [] 
    project_templates = [
        ('Website Redesign', 'Complete overhaul of company website', True),
        ('Mobile App Development', 'Build cross-platform mobile app', True),
        ('Marketing Campaign', 'Digital marketing for product launch', False),
        ('API Integration', 'Connect third-party services', False),
        ('Database Optimization', 'Improve query performance', False),
        ('User Research', 'Conduct interviews and testing', False),
        ('Documentation', 'Write technical documentation', True),
        ('Security Audit', 'Review application security', True),
    ]

    for user in users: 
        num_projs = random.randint(1,3)
        user_projs = random.sample(project_templates, min(num_projs, len(project_templates)))
        for title, description, is_pinned in user_projs: 
            project, created = Project.objects.get_or_create(
                title=title,
                owner=user,
                defaults={
                    'description': description,
                    'is_pinned': is_pinned,
                }
            )

            if created:
                cover_path = get_random_cover_image() 
                if cover_path:
                    with open(cover_path, 'rb') as f:
                        project.cover_image.save(os.path.basename(cover_path), File(f), save=True)
                    print(f" Created: '{project.title}' with cover image (owner: {user.username})")
                else: 
                    print(f" Created: '{project.title}' (owner: {user.username})")
                projects.append(project)
            else:
                print(f'Project exists: {project.title}')
    
    print("\nCreate Tasks\n")

    task_templates = [
        {'title': 'Research and Planning', 'desc': 'Gather requirements', 'priority': 'high'},
        {'title': 'Design Phase', 'desc': 'Create wireframes', 'priority': 'high'},
        {'title': 'Development', 'desc': 'Write code', 'priority': 'high'},
        {'title': 'Testing', 'desc': 'Run tests', 'priority': 'medium'},
        {'title': 'Documentation', 'desc': 'Write docs', 'priority': 'medium'},
        {'title': 'Deployment', 'desc': 'Deploy to production', 'priority': 'low'},
        {'title': 'Client Review', 'desc': 'Get feedback', 'priority': 'medium'},
        {'title': 'Bug Fixes', 'desc': 'Fix issues', 'priority': 'high'},
    ]

    tasks = [] 
    for project in projects:
        num_tasks = random.randint(0,4)
        proj_tasks = random.sample(task_templates, min(num_tasks, len(task_templates)))
        for i, task_data in enumerate(proj_tasks):
            if i == 0:
                status = 'done'
                due_date = date.today() - timedelta(days=random.randint(1, 10))
            elif i == 1:
                status = 'doing'
                due_date = date.today()
            else:
                status = random.choice(['todo', 'doing'])
                due_date = date.today() + timedelta(days=random.randint(1, 30))
            
            task, created = Task.objects.get_or_create(
                title=task_data['title'],
                project=project,
                defaults={
                    'description': task_data['desc'],
                    'status': status,
                    'priority': task_data['priority'],
                    'due_date': due_date,
                    'is_quick_access': random.choice([True, False]) if status == 'todo' else False
                }
            )

            if created:
                print(f" Created: '{task.title}' (project: {project.title})")
                tasks.append(task)

    print("\nCreate Sub-Tasks\n")
    subtask_titles = ['Review','Checklist','Resources','Schedule','Materials']
    for task in tasks[:8]:
        num_subtasks = random.randint(1, 2)
        for sub_title in random.sample(subtask_titles, num_subtasks):
            subtask, created = Task.objects.get_or_create(
                title=f"{sub_title} for {task.title}",
                project=task.project,
                parent=task,
                defaults={
                    'description': f'Subtask for: {task.title}',
                    'status': random.choice(['todo', 'doing']),
                    'priority': task.priority,
                }
            )
            if created:
                print(f" Created subtask: '{subtask.title}' (under: {task.title})")

    quick_tasks = [t for t in tasks if t.status == 'todo'][:5]
    for task in quick_tasks:
        task.is_quick_access = True
        task.save()
        print(f" Quick access: '{task.title}'")

    print("\nPOPULATION COMPLETE\n")
    print(f"SUMMARY:")
    print(f" Users: {User.objects.count()}")
    print(f" Profiles: {UserProfile.objects.count()}")
    print(f" Projects: {Project.objects.count()}")
    print(f" Tasks: {Task.objects.count()}")
    print(f" - Subtasks: {Task.objects.filter(parent__isnull=False).count()}")
    print(f" - Quick Access: {Task.objects.filter(is_quick_access=True).count()}")
    print("\nTEST LOGINS:")
    for user in users:
        password = next((ud['password'] for ud in test_user_data if ud['username'] == user.username), 'unknown')
        print(f"   {user.username} | password: {password}")


# Execute population script
if __name__ == '__main__':
    print('Starting notely population script...')
    populate()
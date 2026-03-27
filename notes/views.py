import os
import urllib.request
import urllib.parse
import json
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Project, Task
from .forms import ProjectForm



import urllib.request
import urllib.parse
import json
import os

def fetch_unsplash_cover(query):
    client_id = os.environ.get('7CYBwiGcKsKAaY6BI2HxnKyviG2wlRaftXhBTB85oI4')
    if not client_id:
        print("API Key missing in .env!")
        return None

    def get_data(search_term):
        safe_query = urllib.parse.quote(search_term)
        url = f"https://api.unsplash.com/search/photos?page=1&query={safe_query}&client_id={client_id}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'NotelyApp/1.0'})
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"Request Error for '{search_term}': {e}")
            return None

    # 1. Try the specific title (e.g., "McKinsey")
    data = get_data(query)
    
    # 2. If no results, try a generic backup (e.g., "business abstract")
    if not data or not data.get('results'):
        print(f"No results for '{query}', trying fallback...")
        data = get_data("business abstract")

    # 3. If we finally have data, grab the image
    if data and data.get('results'):
        try:
            img_url = data['results'][0]['urls']['regular']
            return urllib.request.urlopen(img_url).read()
        except Exception as e:
            print(f"Image Download Error: {e}")

    return None

# ---------------- HOME (SEARCH + QUICK + OVERDUE) ----------------
@login_required
def home(request):
    # Get search query
    query = request.GET.get('q', '').strip()

    # Get user projects
    projects = Project.objects.filter(owner=request.user).select_related('owner')

    # Apply search filter
    if query:
        projects = projects.filter(title__icontains=query)

    projects = projects.order_by('-id')

    # Get quick access tasks
    quick_tasks = Task.objects.filter(
        project__owner=request.user,
        is_quick_access=True
    )

    # FIX: Get pinned projects
    pinned_projects = Project.objects.filter(
        owner=request.user,
        is_pinned=True
    ).order_by('-id')

    # Get overdue tasks
    today = timezone.now().date()

    overdue_tasks = Task.objects.filter(
        project__owner=request.user,
        due_date__lt=today,
        status__in=['todo', 'doing']
    ).order_by('due_date')

    # Render template with all data
    return render(request, 'notes/home.html', {
        'projects': projects,
        'query': query,
        'quick_tasks': quick_tasks,
        'pinned_projects': pinned_projects,  # required for pinned UI
        'overdue_tasks': overdue_tasks
    })


# ---------------- AJAX SEARCH (FULL MARK FEATURE) ----------------
@login_required
def search_projects(request):
    query = request.GET.get('q', '').strip()

    projects = Project.objects.filter(owner=request.user)

    if query:
        projects = projects.filter(title__icontains=query)

    data = [
        {"id": p.id, "title": p.title}
        for p in projects.order_by('-id')
    ]

    return JsonResponse({"projects": data})


# ---------------- CREATE PROJECT (OPTIMIZED WITH API) ----------------
@login_required
def create_project(request):
    if request.method == 'POST':
        project_form = ProjectForm(request.POST, request.FILES)
        if project_form.is_valid():
            project = project_form.save(commit=False)
            project.owner = request.user
            
            # --- MOHAMED'S API OPTIMIZATION (ROBUST VERSION) ---
            if not project.cover_image:
                try:
                    image_data = fetch_unsplash_cover(project.title)
                    if image_data:
                        file_name = f"{project.title.replace(' ', '_')}_cover.jpg"
                        # Save the actual image from Unsplash
                        project.cover_image.save(file_name, ContentFile(image_data), save=False)
                    else:
                        # FALLBACK: If API finds nothing, we leave it blank 
                        # so the HTML template can show the default placeholder.
                        print(f"No match found for {project.title}, falling back to template default.")
                except Exception as e:
                    # Defensive Programming: Ensure an API error doesn't stop project creation
                    print(f"Unsplash Integration Error: {e}")
            # ----------------------------------------------------

            project.save()
            messages.success(request, f'Project {project.title} has been created successfully!')
            return redirect('home')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        project_form = ProjectForm()

    return render(request, 'notes/create_project.html', {'project_form' : project_form})

# ---------------- PROJECT DETAIL (DB SORT, NOT PYTHON SORT) ----------------
@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    today = timezone.now().date()

    tasks = Task.objects.filter(
        project=project,
        parent=None
    ).order_by(
        'due_date',
        '-id'
    )

    return render(request, 'notes/project_detail.html', {
        'project': project,
        'tasks': tasks,
        'today': today 
    })


# ---------------- ADD TASK ----------------
@login_required
def add_task(request, project_id):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '')
        due_date = request.POST.get('due_date')
        priority = request.POST.get('priority', 'medium')
        parent_id = request.POST.get('parent')

        if title:
            Task.objects.create(
                project_id=project_id,
                title=title,
                description=description,
                due_date=due_date or None,
                priority=priority,
                parent_id=parent_id or None
            )

    return redirect('project_detail', project_id=project_id)


# ---------------- TASK DETAIL ----------------
@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__owner=request.user)

    subtasks = task.subtasks.all()

    return render(request, 'notes/task_detail.html', {
        'task': task,
        'subtasks': subtasks
    })

# ---------------- UPDATE TASK DESCRIPTION ----------------
@login_required
def update_task_description(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__owner=request.user)
    if request.method == 'POST':
        description = request.POST.get('description','')
        task.description = description
        task.save()
    return redirect('task_detail',task_id=task_id)


# ---------------- UPDATE STATUS (AJAX) ----------------
@login_required
@require_POST
def update_task_status(request, task_id, status):
    task = get_object_or_404(Task, id=task_id, project__owner=request.user)

    if status in ['todo', 'doing', 'done']:
        task.status = status
        task.save()

    return JsonResponse({'status': task.status})


# ---------------- DELETE TASK ----------------
@login_required
@require_POST
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__owner=request.user)
    project_id = task.project.id
    task.delete()

    return redirect('project_detail', project_id=project_id)


# ---------------- QUICK ACCESS (AJAX) ----------------
@login_required
@require_POST
def toggle_quick_access(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__owner=request.user)

    task.is_quick_access = not task.is_quick_access
    task.save()

    return JsonResponse({
        'quick': task.is_quick_access
    })


# ---------------- PIN PROJECT (AJAX) ----------------
@login_required
@require_POST
def toggle_pin_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    project.is_pinned = not project.is_pinned
    project.save()

    return JsonResponse({
        'pinned': project.is_pinned
    })


# ---------------- ADD SUBTASK (FORM INTEGRATION) ----------------
@login_required
@require_POST
def add_subtask(request, task_id):
    parent_task = get_object_or_404(Task, id=task_id, project__owner=request.user)
    
    # Grab the text from the HTML form
    title = request.POST.get("title", "").strip()

    if title:
        # Prevent adding subtasks to completed tasks
        if parent_task.status == 'done':
            messages.error(request, "Cannot add subtask. Only 'todo' tasks can have subtasks.")
        else:
            # Create the subtask using your self-referential Task model
            Task.objects.create(
                project=parent_task.project,
                title=title,
                parent=parent_task
            )
            messages.success(request, "Subtask added successfully!")
    else:
        messages.error(request, "Subtask title cannot be empty.")

    return redirect('task_detail', task_id=parent_task.id)

# ---------------- TOGGLE SUBTASK (AJAX) ----------------
@login_required
@require_POST
def toggle_subtask(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__owner=request.user)

    task.status = 'done' if task.status != 'done' else 'todo'
    task.save()

    return JsonResponse({
        "status": task.status
    })


# ---------------- DASHBOARD CHART API ----------------
@login_required
def task_stats(request):
    tasks = Task.objects.filter(project__owner=request.user)

    return JsonResponse({
        "todo": tasks.filter(status='todo').count(),
        "doing": tasks.filter(status='doing').count(),
        "done": tasks.filter(status='done').count(),
    })

# ---------------- CHART DATA (TOP LEVEL DASHBOARD) ----------------
@login_required
def chart_data(request, type):
    # 1. Grab all tasks and projects for the user
    tasks = Task.objects.filter(project__owner=request.user)
    projects = Project.objects.filter(owner=request.user).order_by('id')

    # 2. Calculate the global totals for the top summary cards
    total_tasks = tasks.count()
    total_done = tasks.filter(status="done").count()
    total_overdue = tasks.filter(
        due_date__lt=timezone.now().date(),
        status__in=["todo", "doing"]
    ).count()

    # 3. Setup the lists we will send to the Stacked Bar Chart
    labels = []
    todo_values = []   # This will be the RED bar
    doing_values = []  # This will be the YELLOW bar
    done_values = []   # This will be the GREEN bar

    if type == "status":
        for p in projects:
            p_tasks = tasks.filter(project=p)
            p_total = p_tasks.count()
            
            labels.append(p.title)
            if p_total > 0:
                t_todo = p_tasks.filter(status="todo").count()
                t_doing = p_tasks.filter(status="doing").count()
                t_done = p_tasks.filter(status="done").count()

                # Calculate percentages per project
                todo_values.append(round((t_todo / p_total) * 100))
                doing_values.append(round((t_doing / p_total) * 100))
                done_values.append(round((t_done / p_total) * 100))
            else:
                todo_values.append(0)
                doing_values.append(0)
                done_values.append(0)

    elif type == "priority":
        for p in projects:
            p_tasks = tasks.filter(project=p)
            p_total = p_tasks.count()
            
            labels.append(p.title)
            if p_total > 0:
                t_high = p_tasks.filter(priority="high").count()
                t_med = p_tasks.filter(priority="medium").count()
                t_low = p_tasks.filter(priority="low").count()

                todo_values.append(round((t_high / p_total) * 100)) # High -> Red
                doing_values.append(round((t_med / p_total) * 100)) # Med -> Yellow
                done_values.append(round((t_low / p_total) * 100))  # Low -> Green
            else:
                todo_values.append(0)
                doing_values.append(0)
                done_values.append(0)

    elif type == "overdue":
        for p in projects:
            p_tasks = tasks.filter(project=p)
            p_total = p_tasks.count()
            
            labels.append(p.title)
            if p_total > 0:
                t_overdue = p_tasks.filter(due_date__lt=timezone.now().date(), status__in=["todo", "doing"]).count()
                t_ontime = p_total - t_overdue

                todo_values.append(round((t_overdue / p_total) * 100)) # Overdue -> Red
                doing_values.append(0) # Empty Yellow for this view
                done_values.append(round((t_ontime / p_total) * 100)) # On Time -> Green
            else:
                todo_values.append(0)
                doing_values.append(0)
                done_values.append(0)

    # 4. Package everything up for JavaScript
    data = {
        "labels": labels,
        "todo_values": todo_values,
        "doing_values": doing_values,
        "done_values": done_values,
        "total_tasks": total_tasks,
        "total_done": total_done,
        "total_overdue": total_overdue
    }

    return JsonResponse(data)

# ---------------- FILTER TASKS (FOR CHART CLICK) ----------------
@login_required
def filter_tasks(request):

    filter_type = request.GET.get("type")

    tasks = Task.objects.filter(project__owner=request.user)

    if filter_type == "todo":
        tasks = tasks.filter(status="todo")

    elif filter_type == "doing":
        tasks = tasks.filter(status="doing")

    elif filter_type == "done":
        tasks = tasks.filter(status="done")

    elif filter_type == "overdue":
        tasks = tasks.filter(
            due_date__lt=timezone.now().date(),
            status__in=["todo", "doing"]
        )

    return render(request, "notes/task_filter.html", {
        "tasks": tasks,
        "filter_type": filter_type
    })


@login_required
def filter_tasks_api(request):
    task_type = request.GET.get("type")

    tasks = Task.objects.filter(project__owner=request.user)

    if task_type == "todo":
        tasks = tasks.filter(status="todo")

    elif task_type == "doing":
        tasks = tasks.filter(status="doing")

    elif task_type == "done":
        tasks = tasks.filter(status="done")

    elif task_type == "overdue":
        tasks = tasks.filter(
            due_date__lt=timezone.now(),
            status__in=["todo", "doing"]
        )

    data = []

    for t in tasks:
        data.append({
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "project": t.project.title
        })

    return JsonResponse({"tasks": data})

# Delete a project owned by the current user
@login_required
def delete_project(request, project_id):
    # Get project that belongs to current user only (FIX: use owner instead of user)
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    # Delete project from database
    project.delete()

    # Redirect back to home/dashboard
    return redirect('home')
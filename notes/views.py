from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Project, Task


# ---------------- HOME (SEARCH + QUICK + OVERDUE) ----------------
@login_required
def home(request):
    query = request.GET.get('q', '').strip()

    projects = Project.objects.filter(owner=request.user)

    if query:
        projects = projects.filter(title__icontains=query)

    projects = projects.order_by('-id')

    quick_tasks = Task.objects.filter(
        project__owner=request.user,
        is_quick_access=True
    )

    today = timezone.now().date()

    overdue_tasks = Task.objects.filter(
        project__owner=request.user,
        due_date__lt=today,
        status__in=['todo', 'doing']
    ).order_by('due_date')

    return render(request, 'notes/home.html', {
        'projects': projects,
        'query': query,
        'quick_tasks': quick_tasks,
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


# ---------------- CREATE PROJECT ----------------
@login_required
def create_project(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '')

        if title:
            Project.objects.create(
                owner=request.user,
                title=title,
                description=description
            )

        return redirect('home')

    return render(request, 'notes/create_project.html')


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


# ---------------- ADD SUBTASK (AJAX) ----------------
@login_required
@require_POST
def add_subtask(request, task_id):
    parent_task = get_object_or_404(Task, id=task_id, project__owner=request.user)

    title = request.POST.get("title", "").strip()

    if title:
        sub = Task.objects.create(
            project=parent_task.project,
            title=title,
            parent=parent_task
        )

        return JsonResponse({
            "id": sub.id,
            "title": sub.title,
            "status": sub.status
        })

    return JsonResponse({"error": "Invalid"}, status=400)


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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.timezone import now

from .forms import UserRegisterForm, UserProfileForm
from .models import UserProfile
from .tokens import account_activation_token


# --------------------------------------------------
# Register
# --------------------------------------------------
def register(request):

    if request.method == "POST":

        user_form = UserRegisterForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save(commit=False)

            if User.objects.filter(email=user.email).exists():
                messages.error(request, "Email is already registered.")
                return redirect("register")

            user.set_password(user_form.cleaned_data["password"])
            user.is_active = False
            user.save()

            # profile created by signal
            profile = user.userprofile
            profile.avatar = profile_form.cleaned_data.get("avatar")
            profile.bio = profile_form.cleaned_data.get("bio")
            profile.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)

            activation_link = request.build_absolute_uri(
                reverse("activate", kwargs={"uidb64": uid, "token": token})
            )

            send_mail(
                subject="Activate your Notely account",
                message=f"Click the link below:\n\n{activation_link}",
                from_email="admin@notely.com",
                recipient_list=[user.email],
                fail_silently=False
            )

            messages.success(request, "Check terminal to activate account.")
            return redirect("login")

        else:
            messages.error(request, "Registration failed.")

    else:
        user_form = UserRegisterForm()
        profile_form = UserProfileForm()

    return render(request, "accounts/register.html", {
        "user_form": user_form,
        "profile_form": profile_form
    })


# --------------------------------------------------
# Activate
# --------------------------------------------------
def activate(request, uidb64, token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)
    except:
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated.")
        return redirect("login")

    messages.error(request, "Invalid or expired link.")
    return redirect("login")


# --------------------------------------------------
# Login
# --------------------------------------------------
def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect("dashboard")
            else:
                messages.error(request, "Account not activated.")
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, "accounts/login.html")


# --------------------------------------------------
# Logout
# --------------------------------------------------
def user_logout(request):
    logout(request)
    messages.info(request, "Logged out.")
    return redirect("login")


# --------------------------------------------------
# Dashboard (🔥 FINAL VERSION)
# --------------------------------------------------
@login_required
def dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    from notes.models import Project, Task

    projects = Project.objects.filter(
        owner=request.user
    ).order_by('-created_at')[:5]

    tasks = Task.objects.filter(
        project__owner=request.user
    ).order_by('-created_at')[:5]

    overdue_tasks = Task.objects.filter(
        project__owner=request.user,
        due_date__lt=now().date(),
        status__in=['todo', 'doing']
    ).order_by('due_date')[:5]

    stats = {
        'todo': Task.objects.filter(project__owner=request.user, status='todo').count(),
        'doing': Task.objects.filter(project__owner=request.user, status='doing').count(),
        'done': Task.objects.filter(project__owner=request.user, status='done').count(),
        'project_count': Project.objects.filter(owner=request.user).count(),
        'task_count': Task.objects.filter(project__owner=request.user).count(),
        'overdue_count': Task.objects.filter(
            project__owner=request.user,
            due_date__lt=now().date(),
            status__in=['todo', 'doing']
        ).count(),
    }

    return render(request, "accounts/dashboard.html", {
        "user": request.user,
        "profile": profile,
        "projects": projects,
        "tasks": tasks,
        "overdue_tasks": overdue_tasks,
        "stats": stats
    })

# --------------------------------------------------
# Edit Profile
# --------------------------------------------------
@login_required
def edit_profile(request):

    profile = request.user.userprofile
    user = request.user

    if request.method == "POST":

        profile_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        new_email = request.POST.get("email", "").strip()

        if profile_form.is_valid():

            profile_form.save()

            if new_email and new_email != user.email:
                if User.objects.filter(email=new_email).exists():
                    messages.error(request, "Email already used.")
                    return redirect("edit_profile")

                user.email = new_email
                user.save()

            messages.success(request, "Profile updated.")
            return redirect("profile")

    else:
        profile_form = UserProfileForm(instance=profile)

    return render(request, "accounts/edit_profile.html", {
        "profile_form": profile_form,
        "user": user,
        "profile": profile
    })


# --------------------------------------------------
# Profile
# --------------------------------------------------
@login_required
def profile(request):

    return render(request, "accounts/profile.html", {
        "user": request.user,
        "profile": request.user.userprofile
    })
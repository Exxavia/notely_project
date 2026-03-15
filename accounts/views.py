from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

from .forms import UserRegisterForm, UserProfileForm
from .tokens import account_activation_token


# --------------------------------------------------
# Register View
# Creates new user and sends activation email
# --------------------------------------------------
def register(request):

    if request.method == "POST":

        user_form = UserRegisterForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save(commit=False)

            # Prevent duplicate email registration
            if User.objects.filter(email=user.email).exists():

                messages.error(request, "Email is already registered.")
                return redirect("register")

            # Deactivate account until email verification
            user.is_active = False

            # Encrypt password
            user.set_password(user.password)
            user.save()

            # Create user profile
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            # Generate activation token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)

            activation_link = request.build_absolute_uri(
                reverse(
                    "activate",
                    kwargs={
                        "uidb64": uid,
                        "token": token
                    }
                )
            )

            # Send activation email
            send_mail(
                subject="Activate your Notely account",
                message=f"Click the link below to activate your account:\n\n{activation_link}",
                from_email="admin@notely.com",
                recipient_list=[user.email],
                fail_silently=False
            )

            messages.success(
                request,
                "Registration successful. Please check your email to activate your account."
            )

            return redirect("login")

        else:

            messages.error(request, "Registration failed. Please check the form.")

    else:

        user_form = UserRegisterForm()
        profile_form = UserProfileForm()

    context = {
        "user_form": user_form,
        "profile_form": profile_form
    }

    return render(request, "accounts/register.html", context)


# --------------------------------------------------
# Account Activation View
# Activates user account via email link
# --------------------------------------------------
def activate(request, uidb64, token):

    try:

        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):

        user = None

    if user and account_activation_token.check_token(user, token):

        user.is_active = True
        user.save()

        messages.success(request, "Account activated. You can now login.")

        return redirect("login")

    else:

        messages.error(request, "Activation link is invalid or expired.")

        return redirect("login")


# --------------------------------------------------
# Login View
# Authenticates user credentials
# --------------------------------------------------
def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(username=username, password=password)

        if user is not None:

            if user.is_active:

                login(request, user)
                return redirect("dashboard")

            else:

                messages.error(
                    request,
                    "Your account is not activated. Please verify your email."
                )

        else:

            messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


# --------------------------------------------------
# Logout View
# Logs user out of session
# --------------------------------------------------
def user_logout(request):

    logout(request)

    messages.info(request, "You have been logged out.")

    return redirect("login")


# --------------------------------------------------
# Dashboard View
# Main page after login
# --------------------------------------------------
@login_required
def dashboard(request):

    profile = request.user.userprofile

    context = {
        "user": request.user,
        "profile": profile,

        # Future integration for team modules
        "projects": [],   # Project.objects.filter(owner=request.user)
        "tasks": []       # Task.objects.filter(user=request.user)
    }

    return render(request, "accounts/dashboard.html", context)


# --------------------------------------------------
# Edit Profile View
# Allows user to update email, avatar and bio
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

            # Update email only if changed
            if new_email and new_email != user.email:

                if User.objects.filter(email=new_email).exists():

                    messages.error(request, "This email is already in use.")

                    return redirect("edit_profile")

                user.email = new_email
                user.save()

            messages.success(request, "Profile updated successfully.")

            return redirect("profile")

    else:

        profile_form = UserProfileForm(instance=profile)

    context = {
        "profile_form": profile_form,
        "user": user,
        "profile": profile
    }

    return render(request, "accounts/edit_profile.html", context)


# --------------------------------------------------
# Profile View
# Displays user profile information
# --------------------------------------------------
@login_required
def profile(request):

    profile = request.user.userprofile

    context = {
        "user": request.user,
        "profile": profile
    }

    return render(request, "accounts/profile.html", context)
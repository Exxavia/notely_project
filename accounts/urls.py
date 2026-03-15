from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [

    # ----------------------------
    # Authentication URLs
    # ----------------------------

    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),


    # ----------------------------
    # User dashboard
    # ----------------------------

    path("dashboard/", views.dashboard, name="dashboard"),


    # ----------------------------
    # User profile management
    # ----------------------------

    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),


    # ----------------------------
    # Email activation
    # ----------------------------

    path(
        "activate/<uidb64>/<token>/",
        views.activate,
        name="activate",
    ),


    # ----------------------------
    # Password reset
    # ----------------------------

    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html"
        ),
        name="password_reset",
    ),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
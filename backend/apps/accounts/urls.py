"""URL configuration for session authentication endpoints."""

from django.urls import path
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

from apps.accounts.views import (
    CsrfTokenView,
    CurrentUserView,
    LoginView,
    LogoutView,
)

app_name = "accounts"

csrf_view = ensure_csrf_cookie(CsrfTokenView.as_view())
# Login is unauthenticated, so DRF's session authentication does not check
# CSRF for it. Protect it explicitly to prevent login CSRF. DRF marks its views
# `csrf_exempt`, so clear that flag on the wrapped view.
login_view = csrf_protect(LoginView.as_view())
login_view.csrf_exempt = False

urlpatterns = [
    path("auth/csrf/", csrf_view, name="csrf"),
    path("auth/login/", login_view, name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/me/", CurrentUserView.as_view(), name="me"),
]

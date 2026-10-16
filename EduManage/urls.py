from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.urls import include, path

urlpatterns = [
    path("health/", lambda request: JsonResponse({"status": "ok"}), name="health"),
    path("health", lambda request: JsonResponse({"status": "ok"})),
    path("admin/", admin.site.urls),
    path("", include("info.urls")),
    path("info/", include("info.urls")),
    path("api/", include("apis.urls")),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="info/login.html"),
        name="login",
    ),
    path(
        "accounts/logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"
    ),
]

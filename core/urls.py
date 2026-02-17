from django.urls import path
from .views import HealthView, MeView, AdminOnlyView, OpsOnlyView

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("me/", MeView.as_view(), name="me"),
    path("admin-only/", AdminOnlyView.as_view(), name="admin_only"),
    path("ops-only/", OpsOnlyView.as_view(), name="ops_only"),
]

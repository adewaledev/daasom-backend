from django.contrib import admin
from django.urls import include, path

from accounts.auth import LogoutTokenView, RefreshTokenView, RoleTokenObtainPairView

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", include("core.urls")),
    path("api/", include("clients.urls")),
    path("api/", include("jobs.urls")),
    path("api/", include("tracking.urls")),

    path("api/auth/login/", RoleTokenObtainPairView.as_view(),
         name="token_obtain_pair"),
    path("api/auth/refresh/", RefreshTokenView.as_view(), name="token_refresh"),
    path("api/auth/logout/", LogoutTokenView.as_view(), name="token_logout"),
    path("api/", include("tracking.tracker_urls")),
    path("api/", include("expenses.urls")),
    path("api/", include("billing.urls")),
    path("api/", include("payments.urls")),
    path("api/", include("ledger.urls")),
    path("api/", include("documents.urls")),
]

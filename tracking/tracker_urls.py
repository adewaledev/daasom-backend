from django.urls import path
from tracking.tracker_views import TrackerView

urlpatterns = [
    path("tracker/", TrackerView.as_view(), name="tracker"),
]

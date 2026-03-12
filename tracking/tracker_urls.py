from django.urls import path
from tracking.tracker_views import TrackerOptionsView, TrackerView

urlpatterns = [
    path("tracker/options/", TrackerOptionsView.as_view(), name="tracker_options"),
    path("tracker/", TrackerView.as_view(), name="tracker"),
]

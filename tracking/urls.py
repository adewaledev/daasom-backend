from rest_framework.routers import DefaultRouter
from tracking.views import JobMilestoneViewSet, TrackerEntryViewSet

router = DefaultRouter()
router.register(r"job-milestones", JobMilestoneViewSet,
                basename="job_milestones")
router.register(r"tracker-entries", TrackerEntryViewSet,
                basename="tracker_entries")
urlpatterns = router.urls

from rest_framework.routers import DefaultRouter
from tracking.views import JobMilestoneViewSet

router = DefaultRouter()
router.register(r"job-milestones", JobMilestoneViewSet,
                basename="job_milestones")
urlpatterns = router.urls

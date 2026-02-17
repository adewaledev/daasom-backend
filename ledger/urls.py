from rest_framework.routers import DefaultRouter
from ledger.views import LedgerViewSet

router = DefaultRouter()
router.register(r"ledger", LedgerViewSet, basename="ledger")
urlpatterns = router.urls

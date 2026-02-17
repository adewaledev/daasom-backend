from rest_framework.routers import DefaultRouter
from payments.views import ReceiptViewSet

router = DefaultRouter()
router.register(r"receipts", ReceiptViewSet, basename="receipts")
urlpatterns = router.urls

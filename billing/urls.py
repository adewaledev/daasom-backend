from rest_framework.routers import DefaultRouter
from billing.views import InvoiceViewSet

router = DefaultRouter()
router.register(r"invoices", InvoiceViewSet, basename="invoices")
urlpatterns = router.urls

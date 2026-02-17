from rest_framework.routers import DefaultRouter
from billing.views import InvoiceViewSet, InvoiceAddonViewSet

router = DefaultRouter()
router.register(r"invoices", InvoiceViewSet, basename="invoices")
router.register(r"invoice-addons", InvoiceAddonViewSet,
                basename="invoice_addons")
urlpatterns = router.urls

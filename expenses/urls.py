from rest_framework.routers import DefaultRouter
from expenses.views import ExpenseViewSet

router = DefaultRouter()
router.register(r"expenses", ExpenseViewSet, basename="expenses")
urlpatterns = router.urls

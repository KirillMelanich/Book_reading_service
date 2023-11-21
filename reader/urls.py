from rest_framework import routers
from .views import BookViewSet, ReadingSessionViewSet

router = routers.DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'reading-sessions', ReadingSessionViewSet)

urlpatterns = router.urls

app_name = "reader"

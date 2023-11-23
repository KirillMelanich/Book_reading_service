from rest_framework import routers
from .views import BookViewSet, ReadingSessionViewSet, ProfileViewSet

router = routers.DefaultRouter()
router.register(r"book", BookViewSet, basename="book")
router.register(r"reading-sessions", ReadingSessionViewSet, basename="reading-session")
router.register(r"profile", ProfileViewSet, basename="profile")


urlpatterns = router.urls

app_name = "reader"

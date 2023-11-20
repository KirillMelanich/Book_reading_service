from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, ReadingSessionViewSet


router = DefaultRouter()

router.register("book", BookViewSet, basename="book")
router.register("reading-sessions", ReadingSessionViewSet, basename="reading-sessions")

urlpatterns = [
    path("", include(router.urls))
]

app_name = "reader"
